## Author: Claudia Flores-Saviaga
## GitHub: @saviaga

from typing import List
from ctransformers import AutoModelForCausalLM
from .config import settings
from .database import vector_store
from langchain.docstore.document import Document
from pathlib import Path

class RAGPipeline:
    def __init__(self):
        print("\n=== Initializing RAG Pipeline ===")
        print(f"Model path: {settings.MODEL_PATH}")
        print(f"Checking if model file exists: {Path(settings.MODEL_PATH).exists()}")
        
        try:
            self.llm = AutoModelForCausalLM.from_pretrained(
                settings.MODEL_PATH,
                model_type="llama",
                max_new_tokens=settings.MODEL_MAX_TOKENS,
                context_length=settings.MODEL_N_CTX,
                temperature=settings.MODEL_TEMPERATURE,
                batch_size=settings.MODEL_N_BATCH
            )
            print("Model loaded successfully")
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            raise
        print("=== RAG Pipeline Initialized ===\n")

    def generate_prompt(self, query: str, context: List[Document]) -> str:
        """Generate a prompt with context"""
        context_str = "\n\n".join([doc.page_content for doc in context])
        
        return f"""You are a helpful AI assistant. Use the following context to answer the question. 
If you cannot answer the question based on the context, say so.

Context:
{context_str}

Question: {query}

Answer:"""

    def get_response(self, query: str, k: int = 4) -> str:
        """Get response using RAG pipeline"""
        print("\n=== RAG Pipeline Processing ===")
        print(f"Getting context for query: {query}")
        # Get context
        context = vector_store.similarity_search(query, k=k)
        print(f"Found {len(context)} context documents")
        
        # Create prompt
        print("Generating prompt...")
        prompt = self.generate_prompt(query, context)
        print(f"Prompt length: {len(prompt)} characters")
        
        # Generate response
        print("Generating response with LLM...")
        response = self.llm(prompt)
        print("Response generated")
        print("=== RAG Pipeline Complete ===\n")
        
        return response.strip()

    def get_sources(self, query: str, k: int = 4) -> List[dict]:
        """Get sources for the response"""
        print("\n=== Getting Sources ===")
        print(f"Searching for sources with k={k}")
        relevant_docs = vector_store.similarity_search(query, k=k)
        print(f"Found {len(relevant_docs)} relevant documents")
        
        # Use a dictionary to track unique sources
        unique_sources = {}
        for doc in relevant_docs:
            if 'source' in doc.metadata and 'url' in doc.metadata:
                source_key = doc.metadata['url']  # Use URL as unique key
                if source_key not in unique_sources:
                    unique_sources[source_key] = {
                        'title': doc.metadata['source'],
                        'url': doc.metadata['url']
                    }
        
        # Convert dictionary values to list
        sources = list(unique_sources.values())
        print(f"Extracted {len(sources)} unique sources")
        print("=== Sources Complete ===\n")
        return sources

# Create a global instance
rag_pipeline = RAGPipeline() 