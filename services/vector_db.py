import os
import json
import uuid
import logging
from typing import Dict, List, Any
from datetime import datetime
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
from config.settings import Config

logger = logging.getLogger(__name__)

class VectorDatabaseClient:
    """Production-grade vector database using Pinecone"""
    def __init__(self):
        self.embedder = SentenceTransformer(Config.EMBEDDING_MODEL)
        self.index = None
        self.initialize_db()
        
    def initialize_db(self):
        """Initialize Pinecone vector database"""
        try:
            # Initialize Pinecone using the new client
            pc = Pinecone(api_key=Config.PINECONE_API_KEY)

            # Check if index exists, create if not
            if Config.VECTOR_DB_INDEX not in pc.list_indexes().names():
                pc.create_index(
                    name=Config.VECTOR_DB_INDEX,
                    dimension=Config.VECTOR_DIMENSION,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region='us-east-1'
                    )
                )
                logger.info(f"Created new Pinecone index: {Config.VECTOR_DB_INDEX}")

            # Connect to index
            self.index = pc.Index(Config.VECTOR_DB_INDEX)
            logger.info(f"Connected to Pinecone index: {Config.VECTOR_DB_INDEX}")

            # Load initial data if index is empty
            stats = self.index.describe_index_stats()
            if stats.get('total_vector_count', 0) == 0:
                self._load_initial_data()
                
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {str(e)}")
            self.index = None
    
    def _load_initial_data(self):
        """Load initial health claims data if available"""
        try:
            # Check for local health claims file to bootstrap the database
            if os.path.exists('healthfc.json'):
                with open('healthfc.json', 'r') as f:
                    data = json.load(f)
                    health_claims = data.get("health_claims", [])
                    
                if health_claims:
                    logger.info(f"Loading {len(health_claims)} initial health claims into vector database")
                    batch_size = 100
                    for i in range(0, len(health_claims), batch_size):
                        batch = health_claims[i:i+batch_size]
                        self._index_claims_batch(batch)
                    logger.info("Initial health claims loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load initial data: {str(e)}")
    
    def _index_claims_batch(self, claims):
        """Index a batch of health claims into Pinecone"""
        vectors = []
        
        for claim in claims:
            claim_id = str(uuid.uuid4())
            # Create text for embedding (claim + explanation)
            text = claim.get("claim", "") + " " + claim.get("explanation", "")
            # Generate embedding
            embedding = self.embedder.encode(text).tolist()
            
            # Prepare metadata
            metadata = {
                "claim": claim.get("claim", ""),
                "evidence_level": claim.get("evidence_level", ""),
                "explanation": claim.get("explanation", ""),
                "sources": json.dumps(claim.get("sources", [])),
                "timestamp": datetime.now().isoformat()
            }
            
            vectors.append((claim_id, embedding, metadata))
        
        # Upsert vectors in batch
        if vectors:
            to_upsert = [(id, vec, meta) for id, vec, meta in vectors]
            self.index.upsert(vectors=to_upsert)
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for relevant claims using semantic similarity"""
        if not self.index:
            logger.error("Vector database not initialized")
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embedder.encode(query).tolist()
            
            # Search in Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            # Format results
            formatted_results = []
            for match in results.get('matches', []):
                metadata = match.get('metadata', {})
                
                # Parse sources from JSON string
                sources = []
                if metadata.get('sources'):
                    try:
                        sources = json.loads(metadata.get('sources', '[]'))
                    except json.JSONDecodeError:
                        sources = []
                
                formatted_results.append({
                    "claim": metadata.get("claim", ""),
                    "evidence_level": metadata.get("evidence_level", ""),
                    "explanation": metadata.get("explanation", ""),
                    "sources": sources,
                    "relevance_score": match.get('score', 0)
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return []
    
    def add_claim(self, claim: Dict) -> bool:
        """Add a new health claim to the vector database"""
        if not self.index:
            return False
        
        try:
            # Generate unique ID
            claim_id = str(uuid.uuid4())
            
            # Create text for embedding
            text = claim.get("claim", "") + " " + claim.get("explanation", "")
            
            # Generate embedding
            embedding = self.embedder.encode(text).tolist()
            
            # Prepare metadata
            metadata = {
                "claim": claim.get("claim", ""),
                "evidence_level": claim.get("evidence_level", "Low"),  # Default to Low for web-scraped
                "explanation": claim.get("explanation", ""),
                "sources": json.dumps(claim.get("sources", [])),
                "timestamp": datetime.now().isoformat(),
                "origin": claim.get("origin", "web_search")  # Track origin of claim
            }
            
            # Upsert vector
            self.index.upsert(vectors=[(claim_id, embedding, metadata)])
            logger.info(f"Added new claim to vector database: {claim.get('claim')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add claim: {str(e)}")
            return False