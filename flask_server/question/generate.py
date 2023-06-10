import os, json
import openai
import json
import time
import random
import googletrans
from transformers import AutoTokenizer, AutoModelWithLMHead

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

class GenerateQues:
    
    #발급받은 API 키 인증
    openai.api_key = SECRET_KEY
    
    def __init__(self, contents_q, contents_a,
                 num_pairs,
                 temperature=0.7,
                 max_tokens=1000,
                 top_p=1.0,
                 frequency_penalty=0.0,
                 presence_penalty=0.0,
                 num_responses=1):
        self.contents_q = contents_q
        self.contents_a = contents_a
        self.num_pairs = num_pairs
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.num_responses = num_responses
    
    
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

                return translation
            except openai.error.RateLimitError:
                print("RateLimitError occurred. Retrying in 1 second...")
                time.sleep(1)
    
    # translate english to korean by GPT
    def translate_text_e2k(self, texts):
        prompt = "Translate the following English texts(Do not add any symbols) to Korean without changing IT jargon using high honorifics(one listener):\n" + "\n" + texts
        #print("tr_prompt: ", prompt)

        while True:
            try:
                # Perform the translation using OpenAI API
                response = openai.Completion.create(
                    engine='text-davinci-003',
                    prompt=prompt,
                    max_tokens=300,
                    temperature=0.1,
                    top_p=1.0,
                    frequency_penalty=0.0,
                    presence_penalty=0.0,
                    n=1
                )
            
                # Extract the translated texts from the API response
                #translations = [choice['text'].strip() for choice in response['choices']]
                #translations = translations[0].split('\n')
                #print("response: ", response)
                
                # Extract the translated text from the API response
                translation = response['choices'][0]['text'].strip()
                
                # Split the translated text into individual sentences
                #translations = translation.split(delimiter)
                #print("translations: ", translation)
                
                return translation
            except openai.error.RateLimitError:
                print("RateLimitError occurred. Retrying in 1 second...")
                time.sleep(1)
    
    
    def parse_statement(self, s):
        ret1 = s.split("\n")
        while len(ret1) != 0 and ret1[0] == '':
            del ret1[0]
        for i in range(len(ret1)):
            if '. ' in ret1[i]:
                ret1[i] = ret1[i].split('. ')[1]
        return ret1
    
    def genQues(self):
        prompt_template = "Please generate a different question(Do not need an answer to any questions) from the following 'Question', based on the following 'Answer':\n\n{self_introduction}"
        output_list = []
        #ts = googletrans.Translator()
        
        # 질문생성 대상이 될 자소서 질문-대답 쌍 랜덤 선택
        selected_pairs = random.sample(range(len(self.contents_q)), self.num_pairs)
        contents_q_pick = [self.contents_q[i] for i in selected_pairs]
        contents_a_pick = [self.contents_a[i] for i in selected_pairs]
        
        # contents_a_pick에서 길이 5 이하의 짧은 string 제거
        filtered_contents_a_pick = [a for a in contents_a_pick if len(a) >= 5]
        # 짧은 string에 대한 index 생성
        idx = [i for i, a in enumerate(contents_a_pick) if a not in filtered_contents_a_pick]
        filtered_contents_q_pick = [q for i, q in enumerate(contents_q_pick) if i not in idx]
        #print("picked question: ", filtered_contents_q_pick)
        
        translated_questions = []
        translated_answers = []
        for text_q in filtered_contents_q_pick:
            #print("asdf: ", text_q)
            translated_questions.append(self.translate_text_k2e(text_q))
        for text_a in filtered_contents_a_pick:
            #print("fdsa: ", text_a)
            translated_answers.append(self.translate_text_k2e(text_a))
            
        
        print("translated question: ", translated_questions)

        # 각 자기소개 질문, 답변 쌍에 대한 질문 생성
        #for i in range(len(contents_q_pick)):
        for i in range(len(filtered_contents_q_pick)):
            # 자기소개 질문과 답변 하나의 문자열로 만듦
            q_en = translated_questions[i]
            a_en = translated_answers[i]
            self_introduction = "Question: " + q_en + "\n" + "Answer: " + a_en
            
            # 자기 소개에 따라 질문을 작성
            prompt = prompt_template.format(self_introduction=self_introduction)
            #print("prompt: ", prompt)
            for j in range(self.num_responses):
                while True:
                    try:
                        # -*- coding: utf-8 -*-
                        response = openai.Completion.create(
                            engine="text-davinci-003",
                            prompt=prompt,
                            temperature=self.temperature,
                            max_tokens=self.max_tokens,
                            n=1,
                            stop=None,
                            frequency_penalty=self.frequency_penalty,
                            presence_penalty=self.presence_penalty
                        )
                    
                        #print(f"Questions based on '{contents_q_pick[i]}':")
                        for choice in response.choices:
                            #print(f"- {choice.text.strip()}")
                            output_list.append(str(choice.text.strip()))
                    
                        break
                    except openai.error.RateLimitError:
                        print("RateLimitError occurred. Retrying in 1 second...")
                        time.sleep(1)
        
        
        translated_output_list=[]
        for text_o in output_list:
            #print("fdsa: ", text_a)
            translated_output_list.append(self.translate_text_e2k(text_o))
        for i in idx:
            translated_output_list.insert(i, "대답 없음")
        #ques_list = json.dumps(output_list, ensure_ascii=False, indent='\t')
        return translated_output_list
        

if __name__ == "__main__":
    #print("---: ", response["choices"]["text"])
    
    content = "\
        2) 성격의 장점과 단점\
        논어에 '세 명의 사람이 길을 가면 그 중에 스승이 될 만한 사람이 한 명 있다'는 말이 있습니다. 어떤 사람에게도 한 가지 이상의 배울 점은 있다는 생각으로 겸손하게 생활하고 있으며 저의 모자란 부분을 상대방을 통해 채워 나가며 발전적인 삶을 지향합니다.\
        긍정적인 사고방식으로 항상 미소와 여유로움을 잃지 않으려고 노력하며 모나지 않게 사람들을 대하려고 합니다. 때문에 편안하고 부담 없이 친해질 수 있는 따뜻한 사람으로 기억되며 어떤 곳에서든 사람들과 쉽게 친해지고 적응하는 편입니다.\
        일에 있어서는 결코 느슨한 태도를 취하지 않으며 항상 옳은 것이 무엇인지 고민하고 그것을 잣대로 행동하려고 노력합니다. '마음가짐은 태산처럼 하되 몸은 풀처럼 낮추라' 는 말을 좋아하며 자부심은 크고 넓게 갖되 겸손함의 미덕을 잃지 않으려고 합니다. 다만 한번 선입견을 갖고 보기 시작하면 좀처럼 그 사람의 다른 면을 보려고 하지 않는 단점을 갖고 있습니다. 사회생활을 앞두고 열린 마음으로 사람들의 다양한 면을 포괄적으로 수용할 수 있는 포용력을 기르려고 노력하고 있습니다.\
            \
        3) 활동 사항\
        헌법은 국민의 가장 기본적인 의무와 권리가 명시된 것이며 일상생활에 지대한 영향을 끼치고 있지만 일반인들에게는 법은 아직 딱딱하고 근접하기 어려운 것이란 인식이 일반화되어 있기에 법이 바로 서는 나라, 일반화와 대중화가 이루어지는 나라를 만드는데 제 나름의 역할을 해내기 위해 법학과를 지원했습니다.\
        ○○대학교 법과대학 법학과에서 전공과목을 충실히 이수하면서 이론 및 법률실무에 관한 전문지식을 쌓았으며 졸업 후 사법연수원에 들어갔습니다. 제 삶의 방향과 기준을 마련해준 법으로 연수원 ○년 차에는 ○○○○에서 법률상담을 하였고, ○년 차에는 ○○○○○에서 전문분야 연수를 하였습니다.\
        20○○년 제 ○○기 사법연수원 수료를 앞두고 있으며 국제화시대에 걸 맞는 인재가 되기 위해 꾸준히 어학원을 다니며 어학실력을 키워 나가고 있습니다.\
        " + "\n 위 내용에서 성격과 관련된 질문 2개, 활동 사항에 대한 구체적 질문 2개 생성해줘"
    '''
    content_q = ["성격의 장점과 단점", "활동 사항"]
    content_a = ["논어에 '세 명의 사람이 길을 가면 그 중에 스승이 될 만한 사람이 한 명 있다'는 말이 있습니다. \
            어떤 사람에게도 한 가지 이상의 배울 점은 있다는 생각으로 겸손하게 생활하고 있으며 저의 모자란 부분을 상대방을 통해 채워 나가며 발전적인 삶을 지향합니다. \
            긍정적인 사고방식으로 항상 미소와 여유로움을 잃지 않으려고 노력하며 모나지 않게 사람들을 대하려고 합니다. \
            때문에 편안하고 부담 없이 친해질 수 있는 따뜻한 사람으로 기억되며 어떤 곳에서든 사람들과 쉽게 친해지고 적응하는 편입니다. \
            일에 있어서는 결코 느슨한 태도를 취하지 않으며 항상 옳은 것이 무엇인지 고민하고 그것을 잣대로 행동하려고 노력합니다. \
            '마음가짐은 태산처럼 하되 몸은 풀처럼 낮추라' 는 말을 좋아하며 자부심은 크고 넓게 갖되 겸손함의 미덕을 잃지 않으려고 합니다. \
            다만 한번 선입견을 갖고 보기 시작하면 좀처럼 그 사람의 다른 면을 보려고 하지 않는 단점을 갖고 있습니다. \
            사회생활을 앞두고 열린 마음으로 사람들의 다양한 면을 포괄적으로 수용할 수 있는 포용력을 기르려고 노력하고 있습니다.",
            "헌법은 국민의 가장 기본적인 의무와 권리가 명시된 것이며 일상생활에 지대한 영향을 끼치고 있지만 일반인들에게는 법은 아직 딱딱하고 근접하기 어려운 것이란 인식이 일반화되어 있기에 법이 바로 서는 나라, 일반화와 대중화가 이루어지는 나라를 만드는데 제 나름의 역할을 해내기 위해 법학과를 지원했습니다.\
            ○○대학교 법과대학 법학과에서 전공과목을 충실히 이수하면서 이론 및 법률실무에 관한 전문지식을 쌓았으며 졸업 후 사법연수원에 들어갔습니다. \
            제 삶의 방향과 기준을 마련해준 법으로 연수원 5년 차에는 765production에서 법률상담을 하였고, 10년 차에는 365production에서 전문분야 연수를 하였습니다.\
            2023년 제 10기 사법연수원 수료를 앞두고 있으며 국제화시대에 걸 맞는 인재가 되기 위해 꾸준히 어학원을 다니며 어학실력을 키워 나가고 있습니다."]
    '''
    '''
    content_q = ["What is your name?", "What do you do?", "Where are you from?", "What are your hobbies?"]
    content_a = ["My name is John.", "I'm a software engineer.", "I'm from San Francisco.", "I enjoy hiking and reading."]
    '''
    '''
    content_q = [
        "본인을 한 문장으로 표현한다면?",
        "본인이 가장 좋아하는 취미는 무엇인가요?",
        "학교에서 가장 기억에 남는 일은 무엇인가요?",
        "자신이 속한 조직에서 가장 뿌듯한 경험은 무엇인가요?",
        "자신의 강점을 적어보세요.",
        "자신의 약점을 적어보세요.",
        "본인이 얻은 성과 중 가장 자랑스러운 것은 무엇인가요?",
        "본인이 이루고 싶은 목표는 무엇인가요?",
        "자신이 지금까지 배운 것 중에서, 무엇이 가장 유용한 지식인가요?",
    ]
    
    content_a = [
        "저는 도전 정신이 강하며, 적극적으로 일에 임하는 것이 제 강점입니다.",
        "저는 요리하는 것을 좋아합니다. 특히 이탈리안 음식을 만드는 것이 취미 중 하나입니다.",
        "학교에서 가장 기억에 남는 일은 대학 축제에서 제가 주최한 댄스 대회입니다. 이를 성공적으로 마무리할 수 있어서 매우 뿌듯했습니다.",
        "전 회사에서 가장 뿌듯한 경험은 새로운 제품을 개발한 후, 이를 성공적으로 출시했을 때입니다.",
        "저는 빠르게 적응하는 능력과 문제 해결 능력이 강점입니다.",
        "저는 높은 완성도를 요구하는 작업에 대해 조금 더 집중이 필요한 상황에서 시간이 걸릴 때가 있습니다.",
        "저는 이전 회사에서 성공적으로 프로젝트를 수행하고, 이를 통해 벤처기업으로 이직할 수 있었다는 것이 가장 자랑스러운 성과입니다.",
        "제가 이루고 싶은 목표는 전문성 있는 엔지니어가 되어, 다양한 분야에서 기술을 활용해 사회 문제를 해결하는 것입니다.",
        "저는 프로그래밍 언어와 머신 러닝 기술을 배워서, 이를 활용해 자연어 처리 분야에서 활발하게 활동하고 싶습니다.",
    ]
    '''
    '''
    content_q = ["본인을 한 문장으로 표현한다면?", "이 회사에서 왜 당신을 채용해야 하는지, 자신의 경쟁력에 대해 구체적으로 적어주세요 ", "학교 수업이나 혹은 대외 활동을 통해 경험한 가장 잘한 프로젝트를 적어주시되 해당 프로젝트에서의 역할과 활용한 기술 및 개발방식, 그리고 어려웠던 점과 극복한 방법 등을 구체적으로 적어 주세요"]
    content_a = ["저는 도전 정신이 강하며, 적극적으로 일에 임하는 것이 제 강점입니다.", " ", " "]
    '''
    '''
    content_q = ["자신이 어떤 사람인지 자유롭게 소개해 주세요",
                 "학교 수업이나 혹은 대외 활동을 통해 경험한 가장 잘한 프로젝트를 적어주시되 해당 프로젝트에서의 역할과 활용한 기술 및 개발방식, 그리고 어려웠던 점과 극복한 방법 등을 구체적으로 적어 주세요",
                 "이 회사에서 왜 당신을 채용해야 하는지, 자신의 경쟁력에 대해 구체적으로 적어주세요",
                 "본인이 이룬 가장 큰 성취경험과 실패경험에 대해 적어주세요",
                 "해당 직무에 대한 역량과 경험에 대해 말해주세요"]
    content_a = ["안녕하세요! 저는 창의적이고 적극적인 프론트 엔드 개발자로, 새로운 도전에 열린 열정적인 사람입니다. 항상 사용자 경험과 디자인에 주안점을 두며, 직관적이고 효과적인 인터페이스를 제공하는 것을 목표로 삼고 있습니다.저는 문제 해결 능력과 분석력을 갖춘 개발자입니다. 복잡한 문제에 직면했을 때도 주저하지 않고 해결책을 찾아내고, 필요한 데이터를 분석하여 최적의 결과를 도출합니다. 또한, 적극적으로 학습과 개발을 추구하여 최신 트렌드와 도구에 대한 업데이트를 지속적으로 수행하며, 이를 실무에 적용하여 프로젝트에 가치를 더합니다.\n\n팀워크에 있어서도 소통과 협업을 중요시합니다. 다양한 배경과 역할을 가진 팀원들과 원활한 의사소통을 유지하며, 아이디어를 나누고 피드백을 주고받음으로써 팀의 목표를 달성합니다. 열린 마음과 존중하는 자세로 팀원들의 의견을 수용하고 발전시키며, 함께 성장하는 팀의 일원이 되고자 합니다.\n\n저는 프론트 엔드 개발 분야에서 끊임없이 발전하고자 하는 열망을 가지고 있습니다. 혁신적인 기술과 디자인에 대한 탐구와 적용을 통해 사용자들에게 가치 있는 경험을 제공하고, 웹 프로젝트의 성공을 위해 최선을 다할 것입니다.\n\n감사합니다.",
                 "학교 수업 중 가장 잘한 프로젝트는 '온라인 음악 스트리밍 웹 애플리케이션'입니다. 저는 팀의 프론트 엔드 개발자로 참여했고, HTML, CSS, JavaScript를 활용하여 사용자 인터페이스를 구현했습니다. 백엔드 개발자와 협력하여 RESTful API를 사용해 데이터 통신을 구현했고, Git을 활용하여 버전 관리를 진행했습니다. 어려웠던 점은 다양한 브라우저 호환성과 사용자 경험의 일관성을 유지하는 것이었는데, 크로스 브라우징 테스트와 UI/UX 디자인 가이드라인을 참고하여 문제를 극복했습니다.",
                 "이 회사에서 저를 채용해야 하는 이유는 제 경쟁력과 관련이 있습니다.\n\n첫째, 저는 폭넓은 프론트 엔드 개발 경험을 보유하고 있습니다. 학교 수업과 개인 프로젝트를 통해 다양한 웹 애플리케이션을 개발하고, HTML, CSS, JavaScript와 같은 핵심 기술을 능숙하게 다룰 수 있습니다. 또한, React와 Vue.js와 같은 프론트 엔드 프레임워크를 사용하여 복잡한 프로젝트를 구축할 수 있습니다.\n\n둘째, 저는 문제 해결과 소통 능력을 갖추고 있습니다. 어려운 상황에서도 창의적인 해결책을 찾아내고, 팀원들과 원활한 의사소통을 통해 협업을 강화시킬 수 있습니다. 문제 발생 시 적극적으로 대응하고, 효율적인 해결책을 제시하여 프로젝트의 원활한 진행과 성공에 기여할 수 있습니다.\n\n셋째, 지속적인 학습과 성장에 주의를 기울입니다. 프론트 엔드 개발은 빠르게 변화하는 분야이기 때문에, 새로운 기술과 도구에 대한 학습을 게을리하지 않으며, 개발 커뮤니티와 온라인 자료를 적극 활용하여 최신 동향을 파악하고 스스로를 계속해서 발전시키는 자세를 갖고 있습니다.\n\n이러한 경쟁력을 바탕으로 저는 뛰어난 프론트 엔드 개발자로서 이 회사에서 성과를 내고, 사용자 중심의 효과적인 웹 애플리케이션을 개발하는데 기여할 수 있을 것입니다. 저의 역량과 열정을 바탕으로, 팀과 함께 혁신적인 프로젝트를 추진하고 성공적인 결과를 이루어 나가기를 기대합니다.",
                 "가장 큰 성취 경험으로는, 이전 직장에서의 프로젝트를 성공적으로 완료한 것을 꼽을 수 있습니다. 해당 프로젝트는 대규모 웹 애플리케이션의 리디자인과 리팩토링을 담당했습니다. 저는 프론트 엔드 개발자로서 팀원들과 협력하여 사용자 경험 개선, 성능 최적화, 코드 품질 향상 등을 목표로 새로운 기술을 도입하고 기존 코드를 개선했습니다. 결과적으로, 사용자들의 피드백이 긍정적이었고, 애플리케이션의 성능과 사용성이 크게 향상되었습니다. 이 경험을 통해 프로젝트 관리, 팀워크, 기술적 역량 등을 발전시킬 수 있었습니다.\n\n실패 경험 중 가장 큰 것은 개인 프로젝트 중 하나였습니다. 웹 애플리케이션의 개발을 진행하던 중 예상치 못한 기술적인 문제와 시간 관리의 어려움으로 인해 프로젝트를 제때 완료하지 못했습니다. 이는 제 실수와 경험 부족에서 비롯된 것이었습니다. 그러나 이러한 실패를 통해 중요한 교훈을 얻었습니다. 먼저, 기술적인 도전에 대비하여 충분한 조사와 준비를 해야 한다는 것을 배웠습니다. 또한, 타이트한 일정을 관리하는 능력과 우선순위를 설정하는 중요성을 깨달았습니다. 이러한 실패를 반성하고 극복하기 위해 계속해서 개인적인 성장과 학습을 추구하며, 향후 프로젝트에서 더 나은 결과를 이끌어내기 위해 노력하고 있습니다.",
                 "제가 프론트 엔드 개발에 대한 역량과 경험을 갖고 있는 이유는 다음과 같습니다.\n\n첫째, 다양한 웹 기술에 대한 깊은 이해와 경험이 있습니다. HTML, CSS, JavaScript를 비롯한 핵심 웹 기술들을 다룰 수 있으며, React, Vue.js와 같은 프론트 엔드 프레임워크를 사용하여 복잡한 웹 애플리케이션을 개발할 수 있습니다. 또한, 웹 표준과 웹 접근성에 대한 이해를 바탕으로 사용자 친화적인 UI/UX를 구현할 수 있습니다.\n\n둘째, 다양한 프로젝트 경험을 갖고 있습니다. 학교 수업에서의 프로젝트뿐만 아니라 개인적으로도 다양한 웹 애플리케이션을 개발해 왔습니다. 이를 통해 프론트 엔드 개발의 전체적인 프로세스를 경험하고, 문제 해결 및 성능 최적화에 대한 능력을 갖추었습니다.\n\n셋째, 커뮤니케이션과 협업 능력이 뛰어납니다. 팀 프로젝트에서의 협업 경험과 이전 직장에서의 협업을 통해 팀원들과 원활하게 소통하며 프로젝트를 진행하는 데 있어서 중요한 역할을 수행할 수 있습니다. 또한, 비 기술적인 팀원들과도 원활한 의사소통을 통해 프로젝트의 목표를 달성할 수 있습니다.\n\n넷째, 항상 학습과 성장을 추구합니다. 웹 개발은 빠르게 진화하는 분야이므로, 최신 동향을 파악하고 새로운 기술과 도구에 대한 학습을 게을리하지 않습니다. 개발 커뮤니티, 온라인 자료, 기술 블로그 등을 적극 활용하여 지속적인 학습을 진행하고, 이를 바탕으로 업계의 변화에 능동적으로 대응할 수 있습니다.\n\n이러한 역량과 경험을 바탕으로, 저는 프론트 엔드 개발자로서 이 회사에서 팀의 성과를 높이고 사용자들에게 최상의 웹 경험을 제공하는데 기여할 수 있을 것입니다."]
    '''
    content_q = ['자신이 어떤 사람인지 자유롭게 소개해 주세요', '이 회사에서 왜 당신을 채용해야 하는지, 자신의 경쟁력에 대해 구체적으로 적어주세요 ']
    content_a = ['안녕하세요! 저는 창의적이고 적극적인 프론트 엔드 개발자로, 새로운 도전에 열린 열정적인 사람입니다. 항상 사용자 경험과 디자인에 주안점을 두며, 직관적이고 효과적인 인터페이스를 제공하는 것을 목표로 삼고 있습니다.\n\n저는 문제 해결 능력과 분석력을 갖춘 개발자입니다. 복잡한 문제에 직면했을 때도 주저하지 않고 해결책을 찾아내고, 필요한 데이터를 분석하여 최적의 결과를 도출합니다. 또한, 적극적으로 학습과 개발을 추구하여 최신 트렌드와 도구에 대한 업데이트를 지속적으로 수행하며, 이를 실무에 적용하여 프로젝트에 가치를 더합니다.\n\n팀워크에 있어서도 소통과 협업을 중요시합니다. 다양한 배경과 역할을 가진 팀원들과 원활한 의사소통을 유지하며, 아이디어를 나누고 피드백을 주고받음으로써 팀의 목표를 달성합니다. 열린 마음과 존중하는 자세로 팀원들의 의견을 수용하고 발전시키며, 함께 성장하는 팀의 일원이 되고자 합니다.', '이 회사에서 저를 채용해야 하는 이유는 제 경쟁력과 관련이 있습니다.\n\n첫째, 저는 폭넓은 프론트 엔드 개발 경험을 보유하고 있습니다. 학교 수업과 개인 프로젝트를 통해 다양한 웹 애플리케이션을 개발하고, HTML, CSS, JavaScript와 같은 핵심 기술을 능숙하게 다룰 수 있습니다. 또한, React와 Vue.js와 같은 프론트 엔드 프레임워크를 사용하여 복잡한 프로젝트를 구축할 수 있습니다.\n둘째, 저는 문제 해결과 소통 능력을 갖추고 있습니다. 어려운 상황에서도 창의적인 해결책을 찾아내고, 팀원들과 원활한 의사소통을 통해 협업을 강화시킬 수 있습니다. 문제 발생 시 적극적으로 대응하고, 효율적인 해결책을 제시하여 프로젝트의 원활한 진행과 성공에 기여할 수 있습니다.\n셋째, 지속적인 학습과 성장에 주의를 기울입니다. 프론트 엔드 개발은 빠르게 변화하는 분야이기 때문에, 새로운 기술과 도구에 대한 학습을 게을리하지 않은 사람만이 버틸 수 있고 저는 그런 사람 중 하나입니다.']
    
    #content = "삼성 galaxy와 애플 iphone에 대한 차이점을 소프트웨어 차원에서 질문 4개 생성해줘"
    test = GenerateQues(contents_q=content_q, contents_a=content_a, num_pairs=2) # 질문생성 객체 생성
    print(test.contents_q)
    print(test.contents_a)
    response = test.genQues() # 질문 생성 함수

    print("asdf: ", response)
    print("type: ", type(response))
    '''
    "\n\n1. Attention 메커니즘이 어떻게 자연어 처리 작업에 사용되는지?\n2. Attention 메커니즘은 어떤 기능을 가지고 있는가?\n3. Attention 메커니즘을 사용하면 어떤 이점이 있는가?"

    ["Attention 메커니즘이 어떻게 자연어 처리 작업에 사용되는지?", "Attention 메커니즘은 어떤 기능을 가지고 있는가?", "Attention 메커니즘을 사용하면 어떤 이점이 있는가?"]
    '''
    
    ['I have a strong sense of challenge and actively engaging in work is my strength. I like cooking, especially making Italian food is one of my hobbies. The most memorable thing in school was the dance competition that I hosted in the university festival. The most rewarding experience in my previous company was when we successfully launched a new product. My strengths are the ability to adapt quickly and problem-solving skills. There are times when I need to focus more on tasks that require high completion. My proudest accomplishment is that I successfully completed projects in my previous company and was able to transfer to a venture company. My goal is to become a professional engineer and use technology to solve social problems in various fields. I am learning programming languages and machine learning technologies to actively participate in natural language processing.']
    
    ['안녕하세요! 저는 창의적이고 적극적인 프론트 엔드 개발자로, 새로운 도전에 열린 열정적인 사람입니다. 항상 사용자 경험과 디자인에 주안점을 두며, 직관적이고 효과적인 인터페이스를 제공하는 것을 목표로 삼고 있습니다.\n\n저는 문제 해결 능력과 분석력을 갖춘 개발자입니다. 복잡한 문제에 직면했을 때도 주저하지 않고 해결책을 찾아내고, 필요한 데이터를 분석하여 최적의 결과를 도출합니다. 또한, 적극적으로 학습과 개발을 추구하여 최신 트렌드와 도구에 대한 업데이트를 지속적으로 수행하며, 이를 실무에 적용하여 프로젝트에 가치를 더합니다.\n\n팀워크에 있어서도 소통과 협업을 중요시합니다. 다양한 배경과 역할을 가진 팀원들과 원활한 의사소통을 유지하며, 아이디어를 나누고 피드백을 주고받음으로써 팀의 목표를 달성합니다. 열린 마음과 존중하는 자세로 팀원들의 의견을 수용하고 발전시키며, 함께 성장하는 팀의 일원이 되고자 합니다.\n\n저는 프론트 엔드 개발 분야에서 끊임없이 발전하고자 하는 열망을 가지고',
     '이 회사에서 저를 채용해야 하는 이유는 제 경쟁력과 관련이 있습니다.\n\n첫째, 저는 폭넓은 프론트 엔드 개발 경험을 보유하고 있습니다. 학교 수업과 개인 프로젝트를 통해 다양한 웹 애플리케이션을 개발하고, HTML, CSS, JavaScript와 같은 핵심 기술을 능숙하게 다룰 수 있습니다. 또한, React와 Vue.js와 같은 프론트 엔드 프레임워크를 사용하여 복잡한 프로젝트를 구축할 수 있습니다.\n\n둘째, 저는 문제 해결과 소통 능력을 갖추고 있습니다. 어려운 상황에서도 창의적인 해결책을 찾아내고, 팀원들과 원활한 의사소통을 통해 협업을 강화시킬 수 있습니다. 문제 발생 시 적극적으로 대응하고, 효율적인 해결책을 제시하여 프로젝트의 원활한 진행과 성공에 기여할 수 있습니다.\n\n셋째, 지속적인 학습과 성장에 주의를 기울입니다. 프론트 엔드 개발은 빠르게 변화하는 분야이기 때문에, 새로운 기술과 도구에 대한 학습을 게을리하지 않으며, 개발 커뮤니티와 온라인 자료를 적극 활용하여 최']