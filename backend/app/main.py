import asyncio
import logging
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.routes.realtime import router as realtime_router
from app.routes.rag_function import router as rag_function_router
from app.services.rag_client import rag_client

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
app.include_router(rag_function_router, tags=["rag"])


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint - checks backend and RAG service"""
    try:
        logger.info("Health check endpoint accessed")

        # Check RAG service
        try:
            rag_status = await rag_client.check_health()
        except Exception as e:
            logger.error(f"RAG service health check exception: {e}")
            rag_status = {
                "status": "error",
                "url": settings.rag_service_url,
                "details": {"error": str(e)[:100]}
            }

        # Determine overall status
        rag_connected = rag_status.get("status") == "connected"
        overall_status = "healthy" if rag_connected else "degraded"

        response_data = {
            "status": overall_status,
            "service": "backend",
            "rag_service": rag_status,
            "openai_api_key_configured": bool(settings.openai_api_key)
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
                "rag_service": {"status": "unknown"}
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.backend_port)
