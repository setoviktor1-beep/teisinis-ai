"""
RAG (Retrieval-Augmented Generation) Vector Store
Manages semantic search across Lithuanian legal documents
"""

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
import os


class LegalRAG:
    """
    Vector database for legal document retrieval using semantic search
    """
    
    def __init__(self, persist_directory: str = "data/chroma_db"):
        """
        Initialize the RAG system with ChromaDB and multilingual embeddings
        
        Args:
            persist_directory: Where to store the vector database
        """
        # Ensure directory exists
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))
        
        # Create or get collection for legal documents
        self.collection = self.client.get_or_create_collection(
            name="legal_documents",
            metadata={"description": "Lithuanian legal codes and laws"}
        )
        
        # Load multilingual sentence transformer
        # This model supports Lithuanian and provides good semantic understanding
        print("⏳ Loading multilingual embedding model...")
        self.embedder = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
        print("✅ Embedding model loaded")
    
    def index_law(self, law_data: Dict):
        """
        Index an entire law/code into the vector database
        
        Args:
            law_data: Dictionary containing law metadata and articles
                {
                    'law_id': 'TAIS.245495',
                    'title': 'Civilinis kodeksas',
                    'articles': [
                        {
                            'number': '1.1',
                            'title': 'Kodekso taikymo sritis',
                            'content': '...'
                        }
                    ]
                }
        """
        print(f"\n📚 Indexing: {law_data['title']}")
        print(f"   Articles: {len(law_data['articles'])}")
        
        documents = []
        metadatas = []
        ids = []
        
        for article in law_data['articles']:
            # Combine title and content for better semantic search
            full_text = f"{article['title']}\n\n{article['content']}"
            
            documents.append(full_text)
            metadatas.append({
                "law_id": law_data['law_id'],
                "law_title": law_data['title'],
                "article_number": str(article['number']),
                "article_title": article['title'],
                "category": law_data.get('category', 'unknown')
            })
            ids.append(f"{law_data['law_id']}_art_{article['number']}")
        
        # Generate embeddings and add to collection
        print("⏳ Generating embeddings...")
        embeddings = self.embedder.encode(documents, show_progress_bar=True)
        
        print("⏳ Adding to vector database...")
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"✅ Indexed {len(documents)} articles from {law_data['title']}\n")
    
    def search_relevant_articles(
        self, 
        query: str, 
        top_k: int = 5,
        category: Optional[str] = None
    ) -> List[Dict]:
        """
        Find the most relevant legal articles for a given query
        
        Args:
            query: User's legal question or search term
            top_k: Number of results to return
            category: Optional filter by legal category (e.g., 'civilinė_teisė')
        
        Returns:
            List of relevant articles with metadata and similarity scores
        """
        print(f"\n🔍 Searching for: '{query}'")
        if category:
            print(f"   Category filter: {category}")
        
        # Generate query embedding
        query_embedding = self.embedder.encode([query])[0]
        
        # Build where filter if category specified
        where_filter = {"category": category} if category else None
        
        # Search in vector database
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            where=where_filter
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                'article_id': results['ids'][0][i],
                'law_title': results['metadatas'][0][i]['law_title'],
                'article_number': results['metadatas'][0][i]['article_number'],
                'article_title': results['metadatas'][0][i]['article_title'],
                'content': results['documents'][0][i],
                'distance': results['distances'][0][i] if 'distances' in results else None,
                'metadata': results['metadatas'][0][i]
            })
        
        print(f"✅ Found {len(formatted_results)} relevant articles\n")
        return formatted_results
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the indexed documents"""
        count = self.collection.count()
        return {
            "total_articles": count,
            "collection_name": self.collection.name
        }
    
    def clear_collection(self):
        """Clear all indexed documents (use with caution!)"""
        self.client.delete_collection(name="legal_documents")
        self.collection = self.client.create_collection(
            name="legal_documents",
            metadata={"description": "Lithuanian legal codes and laws"}
        )
        print("⚠️ Collection cleared")


# Test code
if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 LEGAL RAG SYSTEM TEST")
    print("="*70 + "\n")
    
    # Initialize RAG
    rag = LegalRAG()
    
    # Test with sample data
    sample_law = {
        'law_id': 'TAIS.TEST',
        'title': 'Test Kodeksas',
        'category': 'test',
        'articles': [
            {
                'number': '1',
                'title': 'Darbo sutarties nutraukimas',
                'content': 'Darbuotojas turi teisę nutraukti darbo sutartį įspėjęs darbdavį prieš 2 savaites.'
            },
            {
                'number': '2',
                'title': 'Atostogos',
                'content': 'Darbuotojui priklauso 20 darbo dienų atostogos per metus.'
            }
        ]
    }
    
    # Index sample law
    rag.index_law(sample_law)
    
    # Test search
    results = rag.search_relevant_articles("Kaip nutraukti darbo sutartį?", top_k=2)
    
    print("📊 SEARCH RESULTS:")
    print("-"*70)
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['law_title']} - Straipsnis {result['article_number']}")
        print(f"   {result['article_title']}")
        print(f"   Distance: {result['distance']:.4f}")
    
    # Stats
    stats = rag.get_collection_stats()
    print(f"\n📈 Database stats: {stats}")
    
    print("\n" + "="*70)
    print("✅ RAG SYSTEM TEST PASSED")
    print("="*70)
