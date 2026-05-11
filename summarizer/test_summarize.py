import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from transformers import PreTrainedTokenizerFast, BartForConditionalGeneration
import torch

print("모델 로딩 중... (처음 실행 시 다운로드로 1~2분 걸릴 수 있어요)")

tokenizer = PreTrainedTokenizerFast.from_pretrained('gogamza/kobart-summarization')
model = BartForConditionalGeneration.from_pretrained('gogamza/kobart-summarization')

print("모델 로딩 완료!")

text = """
서울시는 10일 오전 10시부터 시청 앞 광장에서 '2026 서울 봄꽃 축제'를 개최한다고 밝혔다.
이번 축제는 오는 20일까지 열흘간 진행되며, 벚꽃·개나리·진달래 등 다양한 봄꽃을 감상할 수 있다.
축제 기간 동안 버스킹 공연, 플리마켓, 사진 전시회 등 다채로운 문화 행사도 마련된다.
서울시 관계자는 "올해는 예년보다 개화 시기가 빨라 더욱 풍성한 봄꽃을 즐길 수 있을 것"이라고 말했다.
시민 누구나 무료로 참여할 수 있으며, 자세한 일정은 서울시 공식 홈페이지에서 확인할 수 있다.
"""

print("\n[원문]")
print(text.strip())

raw_input_ids = tokenizer.encode(text)
input_ids = [tokenizer.bos_token_id] + raw_input_ids + [tokenizer.eos_token_id]

summary_ids = model.generate(torch.tensor([input_ids]), num_beams=4, max_length=512, eos_token_id=1)
summary = tokenizer.decode(summary_ids.squeeze().tolist(), skip_special_tokens=True)

print("\n[요약 결과]")
print(summary)
