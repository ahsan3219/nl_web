"""Health check routes for aiohttp server"""

from aiohttp import web
import logging

logger = logging.getLogger(__name__)

async def health_check(request):
    """Simple health check endpoint for Render"""
    return web.json_response({
        "status": "healthy",
        "message": "Zenti AI Agent is running",
        "port": request.app['config']['port'],
        "host": request.app['config']['server']['host']
    })

async def root_handler(request):
    """Root endpoint that redirects to the chat interface"""
    raise web.HTTPFound('/static/zenti-final.html')

def setup_health_routes(app: web.Application):
    """Setup health check routes"""
    app.router.add_get('/health', health_check)
    app.router.add_get('/', root_handler)