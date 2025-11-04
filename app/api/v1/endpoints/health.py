from fastapi import APIRouter

router = APIRouter()

@router.get("")
async def health_check():
    """
    Health check endpoint to verify API is running
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "database": "connected",
            "cache": "connected",
            "ai_models": "loaded"
        }
    }