import wikipediaapi
import requests
from typing import List, Dict, Tuple
from langchain.text_splitter import RecursiveCharacterTextSplitter
from .config import settings

class WikipediaDataIngester:
    def __init__(self):
        self.headers = {
            'User-Agent': settings.WIKIPEDIA_USER_AGENT
        }
        if settings.WIKIPEDIA_ACCESS_TOKEN:
            self.headers['Authorization'] = f'Bearer {settings.WIKIPEDIA_ACCESS_TOKEN}'

        self.wiki = wikipediaapi.Wikipedia(
            user_agent=settings.WIKIPEDIA_USER_AGENT,
            language='en',
            extract_format=wikipediaapi.ExtractFormat.WIKI
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len
        )

    def search_wikipedia(self, query: str, max_results: int = 5) -> List[str]:
        """Search Wikipedia using the REST API"""
        print(f"Searching Wikipedia for: {query}")
        base_url = 'https://api.wikimedia.org/core/v1/wikipedia/en/search/page'
        
        # Add some relevant keywords to improve search
        enhanced_query = f"{query} concept explanation research"
        params = {'q': enhanced_query, 'limit': max_results}
        
        response = requests.get(base_url, headers=self.headers, params=params)
        if response.status_code == 200:
            data = response.json()
            titles = [page['title'] for page in data.get('pages', [])]
            print(f"Found {len(titles)} relevant articles: {', '.join(titles)}")
            return titles
        print(f"Wikipedia search failed with status code: {response.status_code}")
        return []

    def fetch_article(self, title: str) -> Tuple[List[str], List[Dict]]:
        """Fetch and process a Wikipedia article"""
        print(f"Fetching article: {title}")
        page = self.wiki.page(title)
        
        if not page.exists():
            print(f"Article not found: {title}")
            return [], []

        # Get the full text and truncate if necessary
        text = page.text[:settings.MAX_ARTICLE_LENGTH]
        print(f"Retrieved {len(text)} characters from article")
        
        # Split the text into chunks
        chunks = self.text_splitter.split_text(text)
        print(f"Split into {len(chunks)} chunks")
        
        # Create metadata for each chunk
        metadatas = [{
            'source': title,
            'url': page.fullurl,
            'chunk_index': i
        } for i in range(len(chunks))]
        
        return chunks, metadatas

    def search_and_fetch(self, query: str, max_articles: int = None) -> Tuple[List[str], List[Dict]]:
        """Search Wikipedia and fetch multiple articles"""
        print(f"\n=== Wikipedia Search and Fetch ===")
        print(f"Query: {query}")
        print(f"Max articles: {max_articles or settings.MAX_ARTICLES}")
        
        if max_articles is None:
            max_articles = settings.MAX_ARTICLES

        # Search for pages using the REST API
        titles = self.search_wikipedia(query, max_articles)
        if not titles:
            print("No relevant articles found")
            return [], []
        
        all_chunks = []
        all_metadatas = []
        
        # Fetch each article
        for title in titles:
            chunks, metadatas = self.fetch_article(title)
            all_chunks.extend(chunks)
            all_metadatas.extend(metadatas)
        
        print(f"Total chunks collected: {len(all_chunks)}")
        print("=== Search and Fetch Complete ===\n")
        return all_chunks, all_metadatas

# Create a global instance
wikipedia_ingester = WikipediaDataIngester() 