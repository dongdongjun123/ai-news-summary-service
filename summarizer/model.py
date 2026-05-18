from typing import Optional

import torch
from transformers import BartForConditionalGeneration, PreTrainedTokenizerFast

tokenizer = None
model = None
_device: torch.device = torch.device("cpu")

MAX_TOKEN_LENGTH = 1022  # 인코더에 넣을 본문 토큰 상한(BOS/EOS 제외 근처)


def _device_or_cpu() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def load_model():
    global tokenizer, model, _device
    _device = _device_or_cpu()
    print(f"모델 로딩 중... (device={_device})")
    tokenizer = PreTrainedTokenizerFast.from_pretrained("gogamza/kobart-summarization")
    model = BartForConditionalGeneration.from_pretrained("gogamza/kobart-summarization")
    model = model.to(_device)
    model.eval()
    print("모델 로딩 완료!")


def _inputs_ids_long_doc(text: str) -> Optional[list[int]]:
    """매우 긴 본문은 앞·뒤 토큰을 이어 넣어 앞 단락만 보는 현상 완화."""
    if tokenizer is None:
        return None
    full = tokenizer.encode(text, add_special_tokens=False)
    max_body = MAX_TOKEN_LENGTH
    if len(full) <= max_body:
        return [tokenizer.bos_token_id] + full + [tokenizer.eos_token_id]

    head_n = max_body // 2
    tail_n = max_body - head_n - 8
    merged = full[:head_n] + full[-tail_n:]
    merged = merged[:max_body]
    return [tokenizer.bos_token_id] + merged + [tokenizer.eos_token_id]


def summarize(text: str) -> Optional[str]:
    if tokenizer is None or model is None:
        return None
    try:
        input_ids = _inputs_ids_long_doc(text.strip())
        if not input_ids:
            return None

        tensor = torch.tensor([input_ids]).to(_device)
        eos = tokenizer.eos_token_id if tokenizer.eos_token_id is not None else 1
        pad = tokenizer.pad_token_id
        gen_kwargs = {
            "num_beams": 6,
            "max_new_tokens": 142,
            "min_length": 28,
            "length_penalty": 1.15,
            "repetition_penalty": 1.22,
            "no_repeat_ngram_size": 3,
            "early_stopping": True,
            "eos_token_id": eos,
        }
        if pad is not None:
            gen_kwargs["pad_token_id"] = pad

        with torch.no_grad():
            summary_ids = model.generate(tensor, **gen_kwargs)
        decoded = tokenizer.decode(summary_ids.squeeze().tolist(), skip_special_tokens=True).strip()
        return decoded or None
    except Exception:
        return None
