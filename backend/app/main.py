import asyncio
import logging
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.routes.realtime import router as realtime_router
from app.services.rag_client import rag_client
from app.services.openai_gateway import openai_gateway

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = FastAPI(title="Voice Assistant Backend", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(realtime_router, prefix="/api", tags=["realtime"])


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint - checks backend and external services"""
    try:
        logger.info("Health check endpoint accessed")
        
        # Check external services in parallel
        rag_status, openai_status = await asyncio.gather(
            rag_client.check_health(),
            openai_gateway.check_health(),
            return_exceptions=True
        )
        
        # Handle exceptions from health checks
        if isinstance(rag_status, Exception):
            logger.error(f"RAG service health check exception: {rag_status}")
            rag_status = {
                "status": "error",
                "url": settings.rag_service_url,
                "details": {"error": str(rag_status)[:100]}
            }
        
        if isinstance(openai_status, Exception):
            logger.error(f"OpenAI health check exception: {openai_status}")
            openai_status = {
                "status": "error",
                "api_key_configured": bool(settings.openai_api_key),
                "details": {"error": str(openai_status)[:100]}
            }
        
        # Determine overall status
        rag_connected = rag_status.get("status") == "connected"
        openai_connected = openai_status.get("status") == "connected"
        
        if rag_connected and openai_connected:
            overall_status = "healthy"
        elif rag_connected or openai_connected:
            overall_status = "degraded"
        else:
            overall_status = "unhealthy"
        
        response_data = {
            "status": overall_status,
            "service": "backend",
            "rag_service": rag_status,
            "openai": openai_status
        }
        
        logger.info(f"Health check response: status={overall_status}")
        return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in health check endpoint: {e}", exc_info=True)
        return JSONResponse(
            content={
                "status": "error",
                "service": "backend",
                "error": str(e),
                "rag_service": {"status": "unknown"},
                "openai": {"status": "unknown"}
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.backend_port)
