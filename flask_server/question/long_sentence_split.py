import torch
from transformers import BertTokenizer, BertModel
import numpy as np
import re

def split_sentences(text, num_lines=2, model_name='bert-base-multilingual-cased'):
    tokenizer = BertTokenizer.from_pretrained(model_name)
    model = BertModel.from_pretrained(model_name)

    # 문장 토큰화
    sentences = text.split('\n')
    tokenized_sentences = tokenizer(sentences, padding=True, truncation=True, return_tensors='pt')

    # BERT 입력 텐서 생성
    input_ids = tokenized_sentences['input_ids']
    attention_mask = tokenized_sentences['attention_mask']

    # BERT 모델의 hidden states 추출
    with torch.no_grad():
        outputs = model(input_ids, attention_mask=attention_mask)
        hidden_states = outputs.last_hidden_state

    # 문장 임베딩 생성
    sentence_embeddings = torch.mean(hidden_states, dim=1)

    # 문장 간 유사도 계산
    similarity_matrix = np.inner(sentence_embeddings, sentence_embeddings)

    # 유사도 기준으로 문장을 그룹으로 나누기
    groups = []
    num_sentences = len(sentences)
    for i in range(0, num_sentences, num_lines):
        group = [sentences[j] for j in range(i, min(i + num_lines, num_sentences))]
        groups.append(group)

    # 의미적으로 비슷한 문장끼리 그룹으로 나누어진 결과를 하나의 문자열로 결합하여 리스트로 반환
    merged_sentences = [' '.join(group) for group in groups]
    # 문자열 내에 두 번 이상의 공백이 있는 경우 제거
    merged_sentences = [re.sub(r'\s+', ' ', sentence) for sentence in merged_sentences]
    return merged_sentences

if __name__ == "__main__":
    # 예시 문장들
    text = """
    "모든 일에 최선을 다해"
    저의 성격의 장점은 맡은 일에 최선을 다하는 것입니다. 어떠한 사소한 일을 줘도 저에게 맡겨진 일이라면 대충대충 하지 않고 최선을 다해 처리하려고 합니다.
    보완점은 일이 여러 가지가 주어졌을 때 우선순위를 고려하지 못하는 점이 있습니다. 따라서 저는 이러한 점을 보완하고자 일의 중요도를 파악하여 캘린더에 작성하고 있습니다. 이를 통해 중요도에 따라 일을 처리하고 있습니다.
    장점을 통해 주어진 일에 최선을 다하고 보완점을 통해 일의 우선순위를 파악하고 중요도에 따라 일을 처리할 수 있을 것으로 생각합니다.
    """
    
    # 문장 그룹화 후 하나의 문자열로 결합하여 리스트로 반환
    merged_sentences = split_sentences(text, num_lines=2, model_name='bert-base-multilingual-cased')
    
    # 결과 출력
    print(merged_sentences)
