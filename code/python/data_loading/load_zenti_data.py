"""
Script to load Zenti knowledge base into Qdrant vector database.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from core.config import CONFIG
from embedding_providers.openai_embedding import OpenAIEmbedding
from storage_providers.qdrant_embeddings import QdrantStorage
from misc.logger.logging_config_helper import get_configured_logger

logger = get_configured_logger("load_zenti_data")

async def load_knowledge_base():
    """Load Zenti knowledge base into Qdrant."""
    try:
        # Read knowledge base
        kb_path = os.path.join("data", "json", "zenti_knowledge_base.json")
        try:
            with open(kb_path, 'r') as f:
                kb_data = json.load(f)
        except FileNotFoundError:
            # Try alternate path
            kb_path = os.path.join("..", "data", "json", "zenti_knowledge_base.json")
            with open(kb_path, 'r') as f:
                kb_data = json.load(f)
        
        # Initialize Qdrant storage
        storage = QdrantStorage(
            path=CONFIG.retrieval_endpoints["qdrant_local"].database_path,
            collection_name=CONFIG.retrieval_endpoints["qdrant_local"].index_name
        )
        
        # Create collection if it doesn't exist
        await storage.create_collection()
        
        # Process each item
        for item in kb_data["items"]:
            # Convert item to string for embedding
            item_text = json.dumps(item["schema_object"])
            
            # Get embedding
            embedder = OpenAIEmbedding()
            embedding = await embedder.get_embeddings([item_text])
            if not embedding or not embedding[0]:
                logger.error(f"Failed to get embedding for item: {item['name']}")
                continue
            
            # Store item with embedding
            await storage.store(
                url=item["url"],
                json_str=item_text,
                name=item["name"],
                site=kb_data["site"],
                embedding=embedding[0]
            )
            logger.info(f"Stored item: {item['name']}")
        
        logger.info("Knowledge base loading completed successfully")
        
    except Exception as e:
        logger.exception(f"Error loading knowledge base: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(load_knowledge_base())
