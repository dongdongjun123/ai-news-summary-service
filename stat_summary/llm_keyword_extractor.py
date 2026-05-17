import json
import re
from typing import Any, Dict, List, Optional

from stat_summary.keyword_extractor import normalize_keyword
from stat_summary.model_config import DEFAULT_LLM_MODEL


def safe_json_loads(text: str) -> Optional[Dict[str, Any]]:
    if not text:
        return None

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if not match:
        return None

    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return None


def build_keyword_prompt(content: str, top_n: int) -> str:
    return f"""
너는 한국어 뉴스 통계 분석 AI이다.

아래 뉴스 본문에서 핵심 키워드 {top_n}개를 추출해라.

조건:
1. 명사 또는 명사구 중심으로 추출한다.
2. 너무 일반적인 단어는 제외한다.
3. 본문 요약은 하지 않는다.
4. 숫자 계산은 하지 않는다.
5. 반드시 JSON 형식으로만 출력한다.

출력 형식:
{{
  "keywords": ["키워드1", "키워드2", "키워드3"]
}}

뉴스 본문:
{content}
"""


def extract_keywords_with_llm(
    content: str,
    top_n: int = 5,
    model_name: str = DEFAULT_LLM_MODEL,
) -> Optional[List[str]]:
    if not content:
        return None

    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError:
        return None

    prompt = build_keyword_prompt(content=content, top_n=top_n)

    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)

        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype="auto",
            device_map="auto",
        )

        messages = [
            {
                "role": "system",
                "content": "너는 한국어 뉴스 키워드 분석을 돕는 AI이다.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]

        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=256,
            do_sample=False,
        )

        generated_ids = [
            output_ids[len(input_ids):]
            for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        response = tokenizer.batch_decode(
            generated_ids,
            skip_special_tokens=True,
        )[0]

        parsed = safe_json_loads(response)

        if not parsed:
            return None

        raw_keywords = parsed.get("keywords", [])

        keywords = []
        for keyword in raw_keywords:
            normalized = normalize_keyword(str(keyword))

            if not normalized:
                continue

            if normalized not in keywords:
                keywords.append(normalized)

            if len(keywords) >= top_n:
                break

        return keywords if keywords else None

    except Exception:
        return None