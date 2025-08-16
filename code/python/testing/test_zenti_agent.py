"""
Test script for the Zenti payment processing AI agent.
Tests various query types and verifies appropriate responses.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from core.baseHandler import NLWebHandler
from core.config import CONFIG
from misc.logger.logging_config_helper import get_configured_logger

logger = get_configured_logger("test_zenti_agent")

class TestResponse:
    """Mock response handler for testing."""
    def __init__(self):
        self.messages = []

    async def write_stream(self, message):
        """Store messages for verification."""
        self.messages.append(message)
        logger.info(f"Received message: {json.dumps(message, indent=2)}")

async def test_query(query, site="zenti.com", prev_queries=None, prev_answers=None):
    """Test a specific query and return responses."""
    logger.info(f"\nTesting query: {query}")
    
    # Set up query parameters
    query_params = {
        "query": query,
        "site": site,
        "prev": prev_queries or [],
        "last_ans": prev_answers or [],
        "query_id": "test_" + query.replace(" ", "_")[:20],
        "streaming": True
    }

    # Create response handler
    response_handler = TestResponse()
    
    # Create and run handler
    handler = NLWebHandler(query_params, response_handler)
    await handler.runQuery()
    
    return response_handler.messages

async def run_tests():
    """Run a series of test queries."""
    test_cases = [
        # Basic vertical acceptance query
        {
            "query": "Do you accept CBD businesses?",
            "description": "Testing vertical acceptance query"
        },
        
        # High-risk categorization query
        {
            "query": "Why is my online gaming business considered high-risk?",
            "description": "Testing high-risk categorization explanation"
        },
        
        # Processing fees query
        {
            "query": "How much will payment processing cost for my nutraceutical business?",
            "description": "Testing processing fee structure query"
        },
        
        # Chargeback prevention query
        {
            "query": "What can I do to reduce chargebacks for my subscription service?",
            "description": "Testing chargeback prevention guidance"
        },
        
        # Rolling reserve query
        {
            "query": "Can you explain how rolling reserves work?",
            "description": "Testing rolling reserve explanation"
        },
        
        # Documentation requirements query
        {
            "query": "What documents do I need to apply for a merchant account?",
            "description": "Testing documentation requirements query"
        },
        
        # Account termination query
        {
            "query": "What should I do if my merchant account was terminated?",
            "description": "Testing account termination guidance"
        },
        
        # Multi-turn conversation test
        {
            "query": "I run an online supplement store",
            "prev_queries": ["What documents do I need to apply?"],
            "prev_answers": ["List of required documents..."],
            "description": "Testing conversation context handling"
        }
    ]

    for test_case in test_cases:
        logger.info(f"\n=== {test_case['description']} ===")
        
        messages = await test_query(
            test_case["query"],
            prev_queries=test_case.get("prev_queries"),
            prev_answers=test_case.get("prev_answers")
        )
        
        # Verify responses
        if not messages:
            logger.error("No response received")
            continue
            
        # Check for answer in messages
        answer = None
        for msg in messages:
            if msg.get("message_type") == "nlws":
                answer = msg.get("answer")
                break
        
        if not answer:
            logger.error("No answer found in response")
            continue
            
        logger.info(f"Answer received: {answer[:200]}...")
        logger.info("Test case completed successfully\n")

if __name__ == "__main__":
    # Run tests
    asyncio.run(run_tests())
