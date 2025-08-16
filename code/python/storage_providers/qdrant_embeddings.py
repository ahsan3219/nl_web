# Copyright (c) 2025 Microsoft Corporation.
# Licensed under the MIT License

"""
Qdrant storage provider for embeddings.
"""

import os
import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models

from misc.logger.logging_config_helper import get_configured_logger

logger = get_configured_logger("qdrant_embeddings")

class QdrantStorage:
    """Qdrant-based storage for embeddings."""
    
    def __init__(self, path: str, collection_name: str = "nlweb_collection"):
        """
        Initialize Qdrant storage.
        
        Args:
            path: Path to Qdrant database
            collection_name: Name of the collection to use
        """
        self.path = path
        self.collection_name = collection_name
        self.client = None
        
    async def create_collection(self):
        """Create collection if it doesn't exist."""
        try:
            # Create client
            self.client = AsyncQdrantClient(path=self.path)
            
            # Check if collection exists
            collections = await self.client.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            if self.collection_name not in collection_names:
                logger.info(f"Creating collection '{self.collection_name}'")
                await self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=1536,  # OpenAI embedding size
                        distance=models.Distance.COSINE
                    )
                )
                
                # Create payload indexes
                try:
                    import warnings
                    with warnings.catch_warnings():
                        warnings.filterwarnings("ignore", message="Payload indexes have no effect in the local Qdrant")
                        await self.client.create_payload_index(
                            collection_name=self.collection_name,
                            field_name="url",
                            field_schema=models.PayloadSchemaType.KEYWORD
                        )
                        await self.client.create_payload_index(
                            collection_name=self.collection_name,
                            field_name="name",
                            field_schema=models.PayloadSchemaType.KEYWORD
                        )
                        await self.client.create_payload_index(
                            collection_name=self.collection_name,
                            field_name="site",
                            field_schema=models.PayloadSchemaType.KEYWORD
                        )
                except Exception as e:
                    # Silently ignore index creation errors in local mode
                    pass
                
            logger.info("Qdrant storage initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant storage: {e}")
            raise
    
    async def store(self, url: str, json_str: str, name: str, site: str, embedding: List[float]):
        """Store an item with its embedding."""
        try:
            if not self.client:
                await self.create_collection()
                
            # Create point
            point = models.PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "url": url,
                    "json_str": json_str,
                    "name": name,
                    "site": site
                }
            )
            
            # Store in Qdrant
            await self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            logger.debug(f"Stored item: {name}")
            
        except Exception as e:
            logger.error(f"Failed to store item: {e}")
            raise
    
    async def search(self, query_vector: List[float], site: Optional[str] = None, 
                    limit: int = 10) -> List[Tuple[str, str, str, str]]:
        """
        Search for similar items.
        
        Returns:
            List of tuples (url, json_str, name, site)
        """
        try:
            if not self.client:
                await self.create_collection()
            
            # Build filter
            filter_conditions = None
            if site and site != "all":
                filter_conditions = models.Filter(
                    must=[
                        models.FieldCondition(
                            key="site",
                            match=models.MatchValue(value=site)
                        )
                    ]
                )
            
            # Search
            results = await self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=filter_conditions,
                limit=limit,
                with_payload=True
            )
            
            # Extract results
            items = []
            for point in results:
                payload = point.payload
                items.append((
                    payload["url"],
                    payload["json_str"],
                    payload["name"],
                    payload["site"]
                ))
            
            return items
            
        except Exception as e:
            logger.error(f"Failed to search: {e}")
            return []
