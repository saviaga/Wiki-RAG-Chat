from typing import List, Dict
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from .config import settings

class VectorStore:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'}
        )
        self.vector_store = None

    def create_or_load(self):
        """Create a new vector store or load existing one"""
        try:
            self.vector_store = FAISS.load_local(
                settings.VECTOR_STORE_PATH,
                self.embeddings
            )
        except:
            self.vector_store = FAISS.from_documents(
                [Document(page_content="init", metadata={})],
                self.embeddings
            )
            self.vector_store.save_local(settings.VECTOR_STORE_PATH)

    def add_texts(self, texts: List[str], metadatas: List[Dict] = None) -> None:
        """Add new texts to the vector store"""
        if self.vector_store is None:
            self.create_or_load()
        
        documents = [
            Document(page_content=text, metadata=meta or {})
            for text, meta in zip(texts, metadatas or [{}] * len(texts))
        ]
        self.vector_store.add_documents(documents)
        self.vector_store.save_local(settings.VECTOR_STORE_PATH)

    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Search for similar documents"""
        if self.vector_store is None:
            self.create_or_load()
        
        return self.vector_store.similarity_search(query, k=k)

    def clear(self) -> None:
        """Clear the vector store"""
        self.vector_store = FAISS.from_documents(
            [Document(page_content="init", metadata={})],
            self.embeddings
        )
        self.vector_store.save_local(settings.VECTOR_STORE_PATH)

# Create a global instance
vector_store = VectorStore() 