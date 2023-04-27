import openai
import json

class ScoreAns:
    
    openai.api_key = "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"
    
    def __init__(self, questions, answers, max_tokens=500, n=1, stop=None, temperature=0.5):
        self.questions = questions
        self.answers = answers
        self.max_tokens = max_tokens
        self.n = n
        self.stop = stop
        self.temperature = temperature

    def get_gpt_response(self, prompt, model):
        response = openai.Completion.create(
            engine=model,
            prompt=prompt,
            max_tokens=self.max_tokens,
            n=self.n,
            stop=self.stop,
            temperature=self.temperature,
        )
        print(response)

        return response.choices[0].text.strip()

    def score_answer(self, question, answer, model="text-davinci-002"):
        prompt = f"Score the following answer based on its relevance to the question:\nQuestion: {question}\nAnswer: {answer}\nScore:"
        #prompt = f"question과의 관련성을 기준으로 다음 answer를 scoring 해줘:\nQuestion: {question}\nAnswer: {answer}\nScore:"
        response = self.get_gpt_response(prompt, model)

        try:
            score = float(response)
            return score
        except ValueError:
            return None


if __name__ == "__main__":
    question = "What motivated you to apply for our company?"
    answer = "Your company is showing very rapid growth. The current size is small, but I want to work with you by spreading the possibility of future growth."
    
    scoring = ScoreAns(question, answer)
    score = scoring.score_answer(question, answer)
    print(score)