from typing import List, Optional
from fastapi import FastAPI
from pydantic import BaseModel
from contextlib import asynccontextmanager
from summarizer.model import load_model, summarize


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_model()
    yield


app = FastAPI(lifespan=lifespan)


class Article(BaseModel):
    id: int
    text: str


class SummarizeRequest(BaseModel):
    articles: List[Article]


class SummaryResult(BaseModel):
    id: int
    summary: Optional[str]


class SummarizeResponse(BaseModel):
    summaries: List[SummaryResult]


@app.post("/summarize/batch", response_model=SummarizeResponse)
def summarize_batch(request: SummarizeRequest):
    results = []
    for article in request.articles:
        summary = summarize(article.text)
        results.append(SummaryResult(id=article.id, summary=summary))
    return SummarizeResponse(summaries=results)
