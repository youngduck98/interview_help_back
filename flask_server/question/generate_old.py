import os, json
import openai
import json
import time
import random

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
                 temperature=0.5,
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
    
    # translate english to korean by GPT
        # translate english to korean by GPT
    def translate_text_k2e(self, texts):
        # Create the translation prompt
        #prompt = "Translate the following Korean texts to English:\n" + "\n".join(texts)
        #print("tr_prompt: ", prompt)
        if all(item == " " for item in texts):
            return texts # item 내 대답 길이가 5 미만인 원소에 대해서 default 질문을 넣기
        
        # Join sentences with a delimiter
        delimiter = "|||" # 특정 delimiter 설정
        text_with_delimiter = delimiter.join(texts)
        #print(text_with_delimiter)
        
        # Create the translation prompt
        if '|||' not in text_with_delimiter:
            prompt = f"Translate the following Korean texts(Do not add any symbols) to English:\n{text_with_delimiter}"
        else:
            # Create the translation prompt
            prompt = f"Translate the following Korean texts(Please do not remove the symbol '|||') to English:\n{text_with_delimiter}"
        #print("tr_prompt: ", prompt)
        
        # Perform the translation using OpenAI API
        response = openai.Completion.create(
            engine='text-davinci-003',
            prompt=prompt,
            max_tokens=100*len(texts),
            temperature=0.5,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=None,
            n=1
        )
    
        # Extract the translated texts from the API response
        #translations = [choice['text'].strip() for choice in response['choices']]
        #translations = translations[0].split('\n')
        #print("response: ", response)
        
        # Extract the translated text from the API response
        translation = response['choices'][0]['text'].strip()
        
        # Split the translated text into individual sentences
        translations = translation.split(delimiter)
        #print("translations: ", translations)
        
        time.sleep(1)
        
        return translations
    
    # translate english to korean by GPT 
    def translate_text_e2k(self, texts):
        if all(item == " " for item in texts):
            return texts
        
        # Join sentences with a delimiter
        delimiter = "|||" # 특정 delimiter 설정
        text_with_delimiter = delimiter.join(texts)
        
        # Create the translation prompt
        if '|||' not in text_with_delimiter:
            prompt = f"Translate the following English texts(Do not add any symbols) to Korean using high honorifics(one listener):\n{text_with_delimiter}"
        else:
            # Create the translation prompt
            prompt = f"Translate the following English texts(Please do not remove the symbol '|||') to Korean using high honorifics(one listener):\n{text_with_delimiter}"
        #print("tr_prompt: ", prompt)
        
        
        # Perform the translation using OpenAI API
        response = openai.Completion.create(
            engine='text-davinci-003',
            prompt=prompt,
            max_tokens=100*len(texts),
            temperature=0.5,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=None,
            n=1
        )
    
        # Extract the translated texts from the API response
        #translations = [choice['text'].strip() for choice in response['choices']]
        #translations = translations[0].split('\n')
        #print("response: ", response)
        
        # Extract the translated text from the API response
        translation = response['choices'][0]['text'].strip()
        
        # Split the translated text into individual sentences
        translations = translation.split(delimiter)
        #print("translations: ", translations)
        
        time.sleep(1)
        
        return translations
    
    def parse_statement(self, s):
        ret1 = s.split("\n")
        while len(ret1) != 0 and ret1[0] == '':
            del ret1[0]
        for i in range(len(ret1)):
            if '. ' in ret1[i]:
                ret1[i] = ret1[i].split('. ')[1]
        return ret1
    
    def genQues(self):
        prompt_template = "Please generate a different question(Don't need an answer to generated questions) from the following 'Question', based on the following 'Answer' in korean:\n\n{self_introduction}"
        #prompt_template = "다음 'Question'을 기준으로 다음 'Answer'의 내용을 포함하여 면접을 질문을 생성해 주세요.(생성된 질문에 대한 대답은 필요 없음):\n\n{self_introduction}"
        output_list = []
        #ts = googletrans.Translator()
        
        # 질문생성 대상이 될 자소서 질문-대답 쌍 랜덤 선택
        selected_pairs = random.sample(range(len(self.contents_q)), self.num_pairs)
        contents_q_pick = [self.contents_q[i] for i in selected_pairs]
        contents_a_pick = [self.contents_a[i] for i in selected_pairs]
        
        # Remove short strings from contents_a_pick
        filtered_contents_a_pick = [a for a in contents_a_pick if len(a) >= 5]
        # Create index list of short strings
        idx = [i for i, a in enumerate(contents_a_pick) if a not in filtered_contents_a_pick]
        filtered_contents_q_pick = [q for i, q in enumerate(contents_q_pick) if i not in idx]
        
        # Translate Korean questions and answers to English (pick한 질답 쌍에 대해)
        #translated_questions = self.translate_text_k2e(contents_q_pick)
        #translated_answers = self.translate_text_k2e(contents_a_pick)
        #translated_questions = self.translate_text_k2e(filtered_contents_q_pick)
        #translated_answers = self.translate_text_k2e(filtered_contents_a_pick)
        translated_questions = filtered_contents_q_pick
        translated_answers = filtered_contents_a_pick
        
        #print("Picked question: ", filtered_contents_q_pick)

        # 각 자기소개 질문, 답변 쌍에 대한 질문 생성
        #for i in range(len(contents_q_pick)):
        for i in range(len(filtered_contents_q_pick)):
            # 자기소개 질문과 답변 하나의 문자열로 만듦
            #q_en = ts.translate(contents_q_pick[i], src='ko', dest='en').text
            #a_en = ts.translate(contents_a_pick[i], src='ko', dest='en').text
            #q_en = self.translate_korean_to_english(contents_q_pick[i])
            #a_en = self.translate_korean_to_english(contents_a_pick[i])
            q_en = translated_questions[i]
            a_en = translated_answers[i]
            self_introduction = "Question: " + q_en + "\n" + "Answer: " + a_en
            
            # 자기 소개에 따라 질문을 작성
            prompt = prompt_template.format(self_introduction=self_introduction)
            #print("prompt: ", prompt)
            for j in range(self.num_responses):
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
            
                # Wait for a short time to avoid exceeding the API rate limit
                time.sleep(1)
        
        #translated_output_list = self.translate_text_e2k(output_list)
        translated_output_list = output_list
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
        "저는 이전 회사에서 성공적으로 프로젝트를 수행하고, 이를 통해 벤처기업으로 이직할 수 있었다는 것이 가장 자랑스러운 성과입니다.",
    ]
    '''
    content_q = ["본인을 한 문장으로 표현한다면?", "이 회사에서 왜 당신을 채용해야 하는지, 자신의 경쟁력에 대해 구체적으로 적어주세요 ", "학교 수업이나 혹은 대외 활동을 통해 경험한 가장 잘한 프로젝트를 적어주시되 해당 프로젝트에서의 역할과 활용한 기술 및 개발방식, 그리고 어려웠던 점과 극복한 방법 등을 구체적으로 적어 주세요"]
    content_a = ["저는 도전 정신이 강하며, 적극적으로 일에 임하는 것이 제 강점입니다.", " ", " "]
    
    #content = "삼성 galaxy와 애플 iphone에 대한 차이점을 소프트웨어 차원에서 질문 4개 생성해줘"
    test = GenerateQues(contents_q=content_q, contents_a=content_a, num_pairs=2) # 질문생성 객체 생성
    #print(test.contents_q)
    #print(test.contents_a)
    response = test.genQues() # 질문 생성 함수

    print("asdf: ", response)
    print("type: ", type(response))
    '''
    "\n\n1. Attention 메커니즘이 어떻게 자연어 처리 작업에 사용되는지?\n2. Attention 메커니즘은 어떤 기능을 가지고 있는가?\n3. Attention 메커니즘을 사용하면 어떤 이점이 있는가?"

    ["Attention 메커니즘이 어떻게 자연어 처리 작업에 사용되는지?", "Attention 메커니즘은 어떤 기능을 가지고 있는가?", "Attention 메커니즘을 사용하면 어떤 이점이 있는가?"]
    '''
    
    ['I have a strong sense of challenge and actively engaging in work is my strength. I like cooking, especially making Italian food is one of my hobbies. The most memorable thing in school was the dance competition that I hosted in the university festival. The most rewarding experience in my previous company was when we successfully launched a new product. My strengths are the ability to adapt quickly and problem-solving skills. There are times when I need to focus more on tasks that require high completion. My proudest accomplishment is that I successfully completed projects in my previous company and was able to transfer to a venture company. My goal is to become a professional engineer and use technology to solve social problems in various fields. I am learning programming languages and machine learning technologies to actively participate in natural language processing.']
   