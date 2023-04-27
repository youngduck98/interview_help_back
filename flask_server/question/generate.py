import os
import openai
import json

class GenerateQues:
    
    #발급받은 API 키 인증
    openai.api_key = "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"
    
    def __init__(self, contents, temperature=0.5, max_tokens=1000, top_p=1.0, frequency_penalty=0.0, presence_penalty=0.0):
        self.contents = contents
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
    
    def parse_statement(self, s):
        ret1 = s.split("\n")
        while len(ret1) != 0 and ret1[0] == '':
            del ret1[0]
        for i in range(len(ret1)):
            if '. ' in ret1[i]:
                ret1[i] = ret1[i].split('. ')[1]
        return ret1
    
    # def parse_anslist(self, l):
    
    def genQues(self):
        prompts = self.contents
        # -*- coding: utf-8 -*-
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompts,
            temperature=0.5,
            max_tokens=1000,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        
        response['choices'][0]['text'] = self.parse_statement(response['choices'][0]['text'])
        #print("-----choices 참조: ", response['choices'][0]['text'])
        ques_list = json.dumps(response, ensure_ascii=False, indent='\t')
        
        return ques_list
        

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
    
    #content = "삼성 galaxy와 애플 iphone에 대한 차이점을 소프트웨어 차원에서 질문 4개 생성해줘"
    test = GenerateQues(contents=content, max_tokens=10000) # 질문생성 객체 생성
    response = test.genQues() # 질문 생성 함수

    print("asdf: ", response)
    print("type: ", type(response))
    '''
    "\n\n1. Attention 메커니즘이 어떻게 자연어 처리 작업에 사용되는지?\n2. Attention 메커니즘은 어떤 기능을 가지고 있는가?\n3. Attention 메커니즘을 사용하면 어떤 이점이 있는가?"

    ["Attention 메커니즘이 어떻게 자연어 처리 작업에 사용되는지?", "Attention 메커니즘은 어떤 기능을 가지고 있는가?", "Attention 메커니즘을 사용하면 어떤 이점이 있는가?"]
    '''