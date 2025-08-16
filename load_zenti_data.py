#!/usr/bin/env python3
"""
Simple script to load Zenti FAQ data into the NLWeb database
"""

import os
import sys
import json
from pathlib import Path

# Add the python directory to the path
sys.path.insert(0, str(Path(__file__).parent / "code" / "python"))

from core.retriever import RetrievalClient
from core.embedding import EmbeddingProvider
import asyncio

async def load_zenti_data():
    """Load Zenti FAQ data into the database"""
    
    # Zenti FAQ data
    zenti_data = [
        {
            "@type": "Organization",
            "name": "Zenti",
            "description": "Payment Solutions For High-Risk Made Simple",
            "url": "https://zenti.com/",
            "text": "Zenti provides high-risk payment processing solutions with 14+ years of experience, $2 billion+ processing volume, and 5000+ approved merchants."
        },
        {
            "@type": "FAQPage",
            "mainEntity": [{
                "@type": "Question",
                "name": "Do you accept my vertical?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "We have solutions for most high risk verticals, but whether a merchant gets approved by a processor can be a dynamic process and will depend on the results from underwriting. We even have off shore solutions should domestic options not work."
                }
            }]
        },
        {
            "@type": "FAQPage",
            "mainEntity": [{
                "@type": "Question",
                "name": "Why is my business considered high-risk?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Merchants are often considered high-risk due to factors like chargeback rates, industry type, regulatory scrutiny, ticket size, business history, and processing volume."
                }
            }]
        },
        {
            "@type": "FAQPage",
            "mainEntity": [{
                "@type": "Question",
                "name": "What are my approval options?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "High-risk merchants have several options including specialized processors, offshore solutions, payment aggregators, and alternative payment methods."
                }
            }]
        },
        {
            "@type": "FAQPage",
            "mainEntity": [{
                "@type": "Question",
                "name": "How do processing fees work?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "High-risk processing fees are typically higher than mainstream businesses due to increased risk. Pricing is structured with percentage rates, per-transaction fees, monthly fees, and sometimes rolling reserves."
                }
            }]
        },
        {
            "@type": "FAQPage",
            "mainEntity": [{
                "@type": "Question",
                "name": "What is a rolling reserve?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "A rolling reserve is a percentage of your processing volume held by the processor as security against chargebacks and refunds. It's typically 5-10% held for 6-12 months."
                }
            }]
        },
        {
            "@type": "FAQPage",
            "mainEntity": [{
                "@type": "Question",
                "name": "How can I reduce chargebacks?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "To reduce chargebacks, implement clear billing descriptors, provide excellent customer service, use fraud detection tools, respond quickly to disputes, and maintain detailed transaction records."
                }
            }]
        }
    ]
    
    try:
        # Initialize the retrieval client
        client = RetrievalClient()
        
        # Load each FAQ item
        for item in zenti_data:
            # Convert to JSON string
            item_json = json.dumps(item)
            
            # Add to database
            await client.add_document(
                content=item_json,
                metadata={
                    "site": "Zenti",
                    "url": "https://zenti.com/",
                    "title": item.get("name", "Zenti FAQ")
                }
            )
            
            print(f"Loaded: {item.get('name', 'Zenti FAQ')}")
        
        print("✅ Successfully loaded Zenti data into the database!")
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(load_zenti_data())
