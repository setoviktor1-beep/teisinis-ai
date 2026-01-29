"""
Scraper API routes
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.scrapers.seimas_scraper import SeimasScraper
from typing import List, Optional

router = APIRouter()

class ScrapeRequest(BaseModel):
    url: Optional[str] = None
    document_type: str = "all"
    limit: int = 10

@router.post("/scrape")
async def scrape_documents(request: ScrapeRequest):
    """Scrape legal documents"""
    try:
        scraper = SeimasScraper()
        documents = await scraper.scrape_documents(
            document_type=request.document_type,
            limit=request.limit
        )
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def scraper_status():
    """Get scraper status"""
    return {"status": "operational", "sources": ["e-seimas.lt"]}
