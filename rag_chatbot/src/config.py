import os
from dotenv import load_dotenv

class Config:
    OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
    PINECONE_API_KEY=os.getenv("PINECONE_KEY")
    FINHUB_API_KEY=os.getenv("FINHUB_API_KEY")
    FMP_API_KEY=os.getenv("FMP_API_KEY")
    
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "gcp-starter")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "financial-docs")

    EMBEDDING_MODEL = "text-embedding-3-small"
    EMBEDDING_DIMENSION = 1536
    LLM_MODEL = "gpt-4o-mini"
    LLM_TEMPERATURE = 0.7
    LLM_MAX_TOKENS = 1000
    
    TOP_K_RESULTS = 5
    MIN_SIMILARITY_SCORE = 0.7
    
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    DATA_DIR = "data/documents"
    PROCESSED_DIR = "data/processed"
    
    @classmethod
    def validate(cls):
        """Validate that required API keys are present"""
        required = {
            "OPENAI_API_KEY": cls.OPENAI_API_KEY,
            "PINECONE_API_KEY": cls.PINECONE_API_KEY,
        }
        
        missing = [key for key, value in required.items() if not value]
        
        if missing:
            raise ValueError(f"Missing required API keys: {', '.join(missing)}")
        
        return True
Config.validate