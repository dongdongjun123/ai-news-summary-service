from typing import Any, Dict, List, Optional

from stat_summary.keyword_extractor import count_keyword_occurrences, normalize_keyword
from stat_summary.model_config import DEFAULT_EMBEDDING_MODEL
from stat_summary.stat_calculator import STOPWORDS


def extract_related_terms_with_keybert(
    content: str,
    keywords: List[str],
    top_n: int = 6,
    embedding_model_name: str = DEFAULT_EMBEDDING_MODEL,
) -> Optional[List[Dict[str, Any]]]:
    if not content:
        return None

    try:
        from keybert import KeyBERT
        from sentence_transformers import SentenceTransformer
    except ImportError:
        return None

    try:
        embedding_model = SentenceTransformer(embedding_model_name)
        keyword_model = KeyBERT(model=embedding_model)

        candidates = keyword_model.extract_keywords(
            content,
            keyphrase_ngram_range=(1, 2),
            stop_words=None,
            top_n=top_n * 3,
            use_mmr=True,
            diversity=0.6,
        )

        keyword_set = set(keywords)
        related_terms = []

        for word, score in candidates:
            normalized = normalize_keyword(str(word))

            if len(normalized) < 2:
                continue

            if normalized in keyword_set:
                continue

            if normalized in STOPWORDS or normalized.lower() in STOPWORDS:
                continue

            count = count_keyword_occurrences(content, [normalized]).get(normalized, 0)

            related_terms.append({
                "word": normalized,
                "score": min(100, round(float(score) * 100)),
                "count": count,
            })

            if len(related_terms) >= top_n:
                break

        return related_terms if related_terms else None

    except Exception:
        return None