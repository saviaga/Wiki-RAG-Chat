from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from app.model import rag_pipeline
from app.database import vector_store
from app.data_ingestion import wikipedia_ingester
import os
from dotenv import load_dotenv
from pathlib import Path
import time

## Author: Claudia Flores-Saviaga
## GitHub: @saviaga

# Set up base directory and load environment variables
BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR.parent / ".env")

# Get the API token from environment variable
API_TOKEN = os.getenv("API_TOKEN")
if not API_TOKEN:
    raise ValueError("API_TOKEN environment variable not set")

# Initialize FastAPI app
app = FastAPI()  # Re-enable docs for debugging

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Set up templates
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Mount static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

class QueryRequest(BaseModel):
    query: str
    k: Optional[int] = 4

class IngestRequest(BaseModel):
    search_term: str
    max_articles: Optional[int] = None

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    processing_time: float  # Add processing time to response

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Query the RAG system"""
    start_time = time.time()
    print(f"\n=== Processing query request ===")
    print(f"Query: {request.query}")
    print(f"k: {request.k}")
    
    try:
        # First, try to get relevant articles from Wikipedia
        wiki_start_time = time.time()
        print("Searching Wikipedia for relevant articles...")
        chunks, metadatas = wikipedia_ingester.search_and_fetch(
            request.query,
            max_articles=3  # Limit to 3 most relevant articles
        )
        wiki_time = time.time() - wiki_start_time
        print(f"Wikipedia search and fetch took {wiki_time:.2f} seconds")
        
        if chunks:
            print(f"Found {len(chunks)} new chunks from Wikipedia, adding to vector store...")
            vector_store.add_texts(chunks, metadatas)
        
        # Now get the response using the updated knowledge base
        rag_start_time = time.time()
        print("Getting response from RAG pipeline...")
        answer = rag_pipeline.get_response(request.query, k=request.k)
        print(f"Answer received: {answer[:100]}...")  # Print first 100 chars
        
        print("Getting sources...")
        sources = rag_pipeline.get_sources(request.query, k=request.k)
        rag_time = time.time() - rag_start_time
        print(f"RAG processing took {rag_time:.2f} seconds")
        
        total_time = time.time() - start_time
        print(f"Sources found: {len(sources)}")
        print(f"Total processing time: {total_time:.2f} seconds")
        
        response = {
            "answer": answer, 
            "sources": sources,
            "processing_time": total_time
        }
        print("=== Query processing complete ===\n")
        return response
    except Exception as e:
        total_time = time.time() - start_time
        import traceback
        error_details = {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "processing_time": total_time
        }
        print("\n=== Error in query processing ===")
        print("Error:", str(e))
        print("Traceback:", traceback.format_exc())
        print(f"Failed after {total_time:.2f} seconds")
        print("=== End error details ===\n")
        raise HTTPException(status_code=500, detail=error_details)

@app.post("/ingest")
async def ingest(request: IngestRequest):
    """Ingest articles from Wikipedia"""
    try:
        chunks, metadatas = wikipedia_ingester.search_and_fetch(
            request.search_term,
            max_articles=request.max_articles
        )
        
        if not chunks:
            raise HTTPException(status_code=404, detail="No articles found")
        
        vector_store.add_texts(chunks, metadatas)
        return {"message": f"Successfully ingested {len(chunks)} chunks"}
    except Exception as e:
        import traceback
        error_details = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        print("Error details:", error_details)  # This will show in the server logs
        raise HTTPException(status_code=500, detail=error_details)

@app.post("/clear")
async def clear():
    """Clear the vector store"""
    try:
        vector_store.clear()
        return {"message": "Vector store cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 