from transformers import PreTrainedTokenizerFast, BartForConditionalGeneration
import torch

MAX_TOKEN_LENGTH = 1024

tokenizer = None
model = None


def load_model():
    global tokenizer, model
    print("모델 로딩 중...")
    tokenizer = PreTrainedTokenizerFast.from_pretrained('gogamza/kobart-summarization')
    model = BartForConditionalGeneration.from_pretrained('gogamza/kobart-summarization')
    print("모델 로딩 완료!")


def summarize(text: str) -> str | None:
    try:
        raw_input_ids = tokenizer.encode(text, max_length=MAX_TOKEN_LENGTH, truncation=True)
        input_ids = [tokenizer.bos_token_id] + raw_input_ids + [tokenizer.eos_token_id]

        summary_ids = model.generate(
            torch.tensor([input_ids]),
            num_beams=4,
            max_length=512,
            eos_token_id=1
        )
        return tokenizer.decode(summary_ids.squeeze().tolist(), skip_special_tokens=True)
    except Exception:
        return None
