import os, json
import openai
import torch
from transformers import AutoTokenizer, AutoModel
import time
from sklearn.metrics.pairwise import cosine_similarity

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!

secret_file = os.path.join(BASE_DIR, '/home/ubuntu/gitrepo/interview_help_back/flask_server/question/secrets.json')

with open(secret_file) as f:
    secrets = json.loads(f.read())

def get_secret(setting, secrets=secrets):
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)

SECRET_KEY = get_secret("OPENAI_KEY")

class ScoreAns:
    
    openai.api_key = SECRET_KEY
    
    def __init__(self, inter_q, inter_a,
                 max_tokens=500,
                 n=1,
                 stop=None,
                 temperature=0.7,
                 frequency_penalty=0.0,
                 presence_penalty=0.0):
        self.inter_q = inter_q
        self.inter_a = inter_a
        self.max_tokens = max_tokens
        self.n = n
        self.stop = stop
        self.temperature = temperature
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
    
    def score_question_answer_hdn(self, question, answer):
        # BERT 모델 및 토크나이저 초기화
        tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/bert-base-nli-mean-tokens')
        model = AutoModel.from_pretrained('sentence-transformers/bert-base-nli-mean-tokens')
        
        # 입력 문장을 토큰화하고 텐서로 변환
        input_ids = torch.tensor([tokenizer.encode(question, add_special_tokens=True)])
        answer_ids = torch.tensor([tokenizer.encode(answer, add_special_tokens=True)])
        
        # BERT 모델의 hidden states 추출
        with torch.no_grad():
            outputs = model(input_ids)
            question_hidden_states = outputs[0].squeeze(0)  # 첫 번째 문장의 hidden states
            outputs = model(answer_ids)
            answer_hidden_states = outputs[0].squeeze(0)  # 첫 번째 문장의 hidden states

        # 벡터 값을 추출하여 코사인 유사도 계산
        question_vector = torch.mean(question_hidden_states, dim=0).numpy()
        answer_vector = torch.mean(answer_hidden_states, dim=0).numpy()
        similarity = cosine_similarity([question_vector], [answer_vector])[0][0]

        return similarity
    
    def translate_text_k2e(self, texts):
        # Create the translation prompt
        prompt = "Translate the following Korean texts to English:\n" + "\n" + texts
        #print("tr_prompt: ", prompt)
        
        while True:
            try:
                # Perform the translation using OpenAI API
                response = openai.Completion.create(
                    engine='text-davinci-003',
                    prompt=prompt,
                    max_tokens=500,
                    temperature=0.1,
                    top_p=1.0,
                    frequency_penalty=0.0,
                    presence_penalty=0.0,
                    n=1,
                )

                # Extract the translated text from the API response
                translation = response['choices'][0]['text'].strip()

                #print("translations: ", translation)

                return translation
            except openai.error.RateLimitError:
                print("RateLimitError occurred. Retrying in 1 second...")
                time.sleep(1)
    
    def translate_text_e2k(self, texts):
        # Create the translation prompt
        prompt = "Translate the following English texts to Korean using high honorifics:\n" + "\n" + texts
        #print("tr_prompt: ", prompt)
        
        while True:
            try:
                # Perform the translation using OpenAI API
                response = openai.Completion.create(
                    engine='text-davinci-003',
                    prompt=prompt,
                    max_tokens=400,
                    temperature=0.1,
                    top_p=1.0,
                    frequency_penalty=0.0,
                    presence_penalty=0.0,
                    n=1,
                )
                
                # Extract the translated text from the API response
                translation = response['choices'][0]['text'].strip()
                
                print("translations: ", translation)
                
                return translation
            except openai.error.RateLimitError:
                print("RateLimitError occurred. Retrying in 1 second...")
                time.sleep(1)
    
    def score_answer(self):
        scores = []
        feedbacks = []
        #prompt_template = "Please generate feedback to evaluate if the following answer to the question is appropriate in Korean using high honorifics(From the evaluator to one listener): Quesion: {question}\nAnswer: {answer}\n\nFeedback:"
        prompt_template = "From the evaluator's point of view, generate feedback to assess whether the following answer to the question is appropriate(one listener): Quesion: {question}\nAnswer: {answer}\n\nFeedback:"
        bound_max = 10 # 받을 수 있는 점수 중 가장 높은 점수
        pass_score = 5 # 합격 기준 score
        
        # Remove short strings from self.inter_q
        filtered_inter_q = [q for q in self.inter_q if len(q) >= 5]
        # Create index list of short strings
        idx = [i for i, q in enumerate(self.inter_q) if q not in filtered_inter_q]
        filtered_inter_a = [a for i, a in enumerate(self.inter_a) if i not in idx]
        #filtered_inter_a = [a for a in self.filtered_inter_a if len(a) >= 5]
        
        #print("filter q: ", filtered_inter_q)
        #print("filter a: ", filtered_inter_a)

        # Translate Korean questions and answers to English
        translated_questions = []
        translated_answers = []
        for text_q in filtered_inter_q:
            #print("asdf: ", text_q)
            translated_questions.append(self.translate_text_k2e(text_q))
        for text_a in filtered_inter_a:
            if len(text_a) <= 5:
                translated_answers.append(" ")
            else:
                #print("fdsa: ", text_a)
                translated_answers.append(self.translate_text_k2e(text_a))
        
        #for i in range(len(self.inter_q)):
        for i in range(len(translated_questions)):
            #prompt = prompt_template.format(question=self.inter_q[i], answer=self.inter_a[i])
            #prompt_score = prompt_template_score.format(question=self.inter_q[i], answer=self.inter_a[i])
            prompt = prompt_template.format(question=translated_questions[i], answer=translated_answers[i])
            #print("prompt: ", prompt)
            
            
            if len(translated_answers[i]) <= 5:
                score = 0.0
                feedback = "대답 없음"
                
            else:
                while True:
                    try:
                        # 피드백 생성
                        response = openai.Completion.create(
                            engine="text-davinci-003",
                            prompt=prompt,
                            max_tokens=self.max_tokens,
                            n=self.n,
                            stop=self.stop,
                            temperature=self.temperature,
                            frequency_penalty=self.frequency_penalty,
                            presence_penalty=self.presence_penalty,
                        )
                        time.sleep(1)
                        score = self.score_question_answer_hdn(question=translated_questions[i], answer=translated_answers[i])
                        score = float(score)*10
                        
                        # 대답으로부터 feedback 가져오기
                        response_text = response.choices[0].text
                        feedback = response.choices[0].text.strip()
                        break
                        
                    except openai.error.RateLimitError:
                        print("RateLimitError occurred. Retrying in 1 second...")
                        time.sleep(1)

            
            print("{}th feedback: {}".format(i, feedback))
            print("{}th score: {}".format(i, score))
            
            '''
            score = self.score_question_answer(question=self.inter_q[i], answer=self.inter_a[i])
            
            '''
            # output list에 요소 append
            feedbacks.append(feedback)
            scores.append(score)
            
        translated_feedback = []
        for text_f in feedbacks:
            #print("asdf: ", text_q)
            translated_feedback.append(self.translate_text_e2k(text_f))
            
        # Add "질문 오류" and 0.0 for short strings
        for i in idx:
            translated_feedback.insert(i, "질문 오류")
            scores.insert(i, 0.0)
            
        #pass_score*(len(self.inter_q)- len(idx))

        return scores, translated_feedback, bound_max, 25


if __name__ == "__main__":
    '''
    question = "What motivated you to apply for our company?"
    answer = "Your company is showing very rapid growth. The current size is small, but I want to work with you by spreading the possibility of future growth."
    '''
    '''
    inter_q = [
        "Can you tell me about yourself?",
        "What are your strengths?",
        "What are your weaknesses?",
        "Why do you want to work for our company?",
        "What is freedom in your opinion?",
    ]

    inter_a = [
        "I am a recent graduate with a degree in computer science. During my studies, I worked on several projects that involved software development, and I also completed an internship at a technology company. In my free time, I enjoy reading books and hiking.",
        "One of my strengths is my ability to work well in a team. I am a good listener and communicator, and I always make an effort to understand my team members' perspectives. I am also a quick learner, which allows me to adapt to new situations easily.",
        "One of my weaknesses is that I tend to be a perfectionist, which can sometimes lead to spending too much time on a task. I have been working on finding a balance between striving for excellence and not letting perfect be the enemy of good.",
        "I am excited about the work that your company is doing in the field of artificial intelligence, and I admire your commitment to innovation and collaboration. I believe that my skills and interests align well with the work that your company is doing, and I would love to be a part of that.",
        "I want to eat pizza.",
    ]
    '''
    '''
    inter_q = ["저의 역량을 증명하기 위해서요. 다른 후보자들과 비교해서 나는 이 산업의 최신 트렌드와 기술에 대해 업데이트를 유지하는 데 적극적이라는 것이 나를 강조합니다.", "이"]
    inter_a = [" ", " "]
    '''
    '''
    inter_q = ["say your vision related to our company's work", 'java example question2', 'c   example question', '어떤 음악을 가장 좋아하십니까?', '가장 자주 들으시는 음악은 어떤 것입니까?']
    inter_a = ['', '', '', '', '']
    '''
    '''
    inter_q = [
        "당신이 가장 선호하는 프로그래밍 언어는 무엇인가요?",
        "특정 언어나 기술 스택에 대한 지식이 없는 지원자에게 회사에서 기대하는 것은 무엇인가요?",
        "어떤 프로젝트에서 힘들었던 점이나 어려움을 어떻게 해결했는지 알려주세요.",
        "",
        "당신에게 있어서 자유란 무엇입니까?"
    ]

    inter_a = [
        "저는 파이썬이 가장 선호되는 프로그래밍 언어입니다.",
        "저는 지원자가 특정 언어나 기술 스택에 대한 전문 지식보다는 학습 및 적응 능력, 문제 해결 능력, 그리고 협업 능력을 중요하게 여깁니다.",
        "저는 지난번 프로젝트에서 X 기술을 활용하려다가 어려움을 겪었지만, Y 기술로 대체하여 문제를 해결하였습니다.",
        " ",
        "저는 피자가 먹고싶습니다."
    ]
    '''
    inter_q = [
        "당신이 가장 선호하는 프로그래밍 언어는 무엇인가요?",
        "어떤 프로젝트에서 힘들었던 점이나 어려움을 어떻게 해결했는지 알려주세요.",
        ""
    ]

    inter_a = [
        "저는 파이썬이 가장 선호되는 프로그래밍 언어입니다.",
        " ",
        "저는 피자가 먹고싶습니다."
    ]
    
    #inter_q = ["CSS 박스 모델에 대해 설명해줘세요."]
    #inter_a = ["css 박스 모델에 대해서는 잘 알지 못합니다 죄송합니다"]
    '''
    inter_q = [
        "인공지능 모델의 과적합(Overfitting)에 대해 설명해주세요. 과적합이 발생할 때 어떻게 대응하시나요?",
        "어떤 데이터 전처리 기법을 사용하여 인공지능 모델을 향상시켰던 경험이 있나요? 그 효과에 대해 이야기해주세요.",
        "인공지능 모델의 평가 지표에는 어떤 것들이 있나요? 그리고 어떤 경우에 어떤 평가 지표를 사용해야 할까요?",
        "인공지능 분야에서의 혁신적인 동향에 대해 어떻게 알아가시나요? 어떤 논문, 블로그, 컨퍼런스 등을 주시하는지 알려주세요.",
        ]
    inter_a = [
        "과적합은 모델이 너무 단순하여 학습 데이터에서도 잘 작동하지 않는 상황을 의미합니다. 이를 해결하기 위해 모델을 더 복잡하게 만들어야 합니다.",
        "저는 텍스트 데이터를 다룰 때 정규화, 토큰화, 불용어 제거, 단어 임베딩 등의 전처리 기법을 사용하여 모델 성능을 향상시켰습니다. 특히, Word2Vec을 이용한 단어 임베딩을 적용하여 단어 간 의미적 유사성을 반영한 표현을 사용하였고, 이는 텍스트 분류 문제에서 좋은 결과를 얻을 수 있었습니다.",
        "인공지능 모델의 평가 지표는 정확도만 사용하면 충분합니다. 다른 평가 지표는 복잡하고 이해하기 어려우므로 신경쓰지 않아도 됩니다.",
        "저는 인공지능 연구 동향을 파악하기 위해 주요 컨퍼런스인 NeurIPS, ICCV, ACL 등의 논문 발표를 주시하고, AI 관련 블로그 및 논문 아카이브인 arXiv를 활용합니다. 또한, AI 기술을 공유하는 온라인 커뮤니티나 연구 그룹에 참여하여 최신 동향을 알아가고 적용합니다.",
        ]
    '''
    '''
    inter_q = [
        "AWS 중에 어떤 것을 사용해보았는지를 해당 기술에 대한 간단한 설명과 함께 제시해주세요.",
        "반응형 웹 디자인과 웹 접근성에 대해서 어떻게 이해하고 계신가요?",
        "JavaScript에서 비동기 처리를 위해 사용하는 다양한 패턴과 기술에 대해서 설명해주세요",
        "ETL, ELT의 차이에 대해 설명하고, 각각의 장점에 대해 설명해보세요",
        "NAT(Bridge)가 무엇인가?",
        "DevOps에 대해 간략하게 정의해 주세요.",
        ]
    inter_a = [
        "저는 AWS의 EC2 인스턴스를 사용해보았습니다. EC2는 확장 가능한 컴퓨팅 파워를 제공하는 서비스로, 가상 서버를 프로비저닝하고 관리할 수 있습니다. EC2를 사용하여 웹 애플리케이션을 배포하고 운영하는 경험이 있습니다.",
        "반응형 웹 디자인은 웹 사이트가 모바일 환경에서 잘 작동하는 것을 의미하고, 웹 접근성은 웹 사이트에 접속할 수 있는 보안 기능을 의미합니다.",
        "JavaScript에서 비동기 처리를 위해 사용하는 패턴은 주로 if-else 문이나 for 루프와 같은 제어 구문을 사용합니다.",
        "ETL과 ELT는 데이터 추출에 사용되는 도구의 차이로, ETL은 데이터 추출을 위해 SQL 쿼리를 사용하고, ELT은 Python 스크립트를 사용합니다.",
        "NAT은 네트워크에서 데이터 패킷을 분석하여 정상적인 패킷인지 확인하는 보안 기술입니다.",
        "DevOps는 소프트웨어 개발에 사용되는 도구와 기술을 의미하며, 소프트웨어의 기능 개선을 위한 테스트와 디버깅을 수행합니다.",
        ]
    '''
    '''
    inter_q = ['이전에 하였던 프로젝트 도중의 갈등 상황과 해결방안?', '이전에 하였던 프로젝트에 대한 설명과 보완하고 싶은 내용은?', '사용해 보신 프레임워크에 대한 경험을 알려주세요', '고맙습니다. 이 역할에서 성공하기 위해 갖추어야 할 스킬은 무엇입니까?', '당신의 경험에서 어떤 가장 중요한 교훈을 얻으셨습니까?']
    inter_a = ['해당 프로젝트의 방향성 문제에서 어느 방향으로 프로젝트를 먼저 진행을 해야 되는지에 대해 갈등상황이 있었습니다. 위에서 단순히 상대방의 이기심이라고 판단하지 않고 실제로 어떤 이유를 가지고 그런 판단을 해야 하는지 자세하게 들음으로써 상대방을 이해하고 갈등을 해결할 수 있었습니다', '이전에 하던 프로젝트의 내용으로는 곳에 사진을 보고 해당 꽃에 꽃망울 찾아주는 프로젝트를 진행 한 적이 있었습니다 대부분 만족스러웠지만 대하여 제대로 판단하지 못하는 오류가 있었는데 해당 부분을 제대로 고치지 못히고 프로젝트를 종결하게 되어 아직 아쉬움이 있습니다', '파이토치 와 텐서플로우에 대해 사용해 보았고 이전에 사용하는 프레임워크에 대비하여 훨씬 간편한 용도로 사용할 수 있다는 것을 알게 되었습니다', '해당 역할에서 성공하기 위해서는 먼저 인공 지능 전체에 대한 전반적인 지식이 있어야 하고 본인이 맡은 일을 끝까지 하는 책임감이 있어야 된다 생각합니다', '프로젝트 진행 하다 보면은 중요하다고 생각하는 하나의 매물 돼요 전체를 보지 못하는 경우가 가끔 생깁니다 그런 부분을 피할 수 있 있어야 된다는 교훈이 저에게는 상당히 중요하다 생각됩니다']
    '''
    '''
    inter_q = [
        "사용해 보신 프레임워크에 대한 경험을 알려주세요",
        "본인을 한 문장으로 표현한다면?",
    ]
    inter_a = [
        "저는 못과 망치를 잘 사용할 줄 압니다.",
        "저는 도전 정신이 강하며, 적극적으로 일에 임하는 것이 제 강점입니다.",
    ]
    '''
    scoring = ScoreAns(inter_q, inter_a)
    score, feedback, bound_max, pass_score= scoring.score_answer()
    print("score: ", score)
    print("feedback: ", feedback)