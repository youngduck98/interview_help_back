import openai
import json

openai.api_key = "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"

def get_gpt_response(prompt, model, max_tokens=500):
    response = openai.Completion.create(
        engine=model,
        prompt=prompt,
        max_tokens=max_tokens,
        n=1,
        stop=None,
        temperature=0.5,
    )
    print(response)

    return response.choices[0].text.strip()

def score_answer(question, answer, model="text-davinci-002"):
    prompt = f"Score the following answer based on its relevance to the question:\nQuestion: {question}\nAnswer: {answer}\nScore:"
    #prompt = f"question과의 관련성을 기준으로 다음 answer를 scoring 해줘:\nQuestion: {question}\nAnswer: {answer}\nScore:"
    response = get_gpt_response(prompt, model)

    try:
        score = float(response)
        return score
    except ValueError:
        return None


question = "What motivated you to apply for our company?"
answer = "Your company is showing very rapid growth. The current size is small, but I want to work with you by spreading the possibility of future growth."

score = score_answer(question, answer)
print(score)