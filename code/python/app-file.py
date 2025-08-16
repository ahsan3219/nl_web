#!/usr/bin/env python3
"""
NLWeb - Natural Language Web Interface
Main application entry point
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Ensure we're in the right directory
os.chdir(Path(__file__).parent)

# Set PORT for Render deployment
if 'PORT' in os.environ:
    port = os.environ['PORT']
    print(f"Using PORT from environment: {port}")
    # Ensure the PORT is properly set for the server
    os.environ['PORT'] = str(port)
else:
    port = '8000'
    os.environ['PORT'] = port
    print(f"No PORT environment variable found, using default: {port}")

# Debug: Print all environment variables related to port
print(f"Final PORT environment variable: {os.environ.get('PORT', 'NOT SET')}")
print(f"All environment variables: {dict(os.environ)}")

# Load environment variables from .env file
load_dotenv()

# Suppress verbose HTTP client logging from OpenAI SDK
import logging
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)

# Suppress Azure SDK HTTP logging
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)
logging.getLogger("azure").setLevel(logging.WARNING)

# Suppress webserver middleware INFO logs
logging.getLogger("webserver.middleware.logging_middleware").setLevel(logging.WARNING)
logging.getLogger("aiohttp.access").setLevel(logging.WARNING)

# Initialize router
import core.router as router
router.init()

# Initialize LLM providers
import core.llm as llm
llm.init()

# Initialize retrieval clients
import core.retriever as retriever
retriever.init()

async def main():
    print("Starting aiohttp server...")
    from webserver.aiohttp_server import AioHTTPServer
    server = AioHTTPServer()
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())