"""FastAPI application for NBA arbitrage detection service."""
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys

from odds_fetcher import fetch_nba_odds, OddsFetchError
from arbitrage import find_arbitrage_opportunities, ArbitrageCalculationError
from scheduler import start_scheduler, stop_scheduler
from db import check_db_connection, init_db, DatabaseError
from logger import get_logger
from config import config, ConfigError

logger = get_logger(__name__, config.LOG_LEVEL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle (startup and shutdown).
    """
    # Startup
    logger.info(f"Starting NBA Arbitrage Detection Service (Environment: {config.ENVIRONMENT})")

    try:
        # Check database connection
        if not check_db_connection():
            logger.error("Database connection check failed")
            raise DatabaseError("Cannot connect to database")

        # Initialize database tables
        logger.info("Initializing database tables...")
        init_db()

        # Start scheduler
        logger.info("Starting arbitrage detection scheduler...")
        start_scheduler()

        logger.info("Application startup completed successfully")

    except (ConfigError, DatabaseError) as e:
        logger.critical(f"Startup failed: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Unexpected error during startup: {str(e)}")
        sys.exit(1)

    yield

    # Shutdown
    logger.info("Shutting down application...")
    stop_scheduler()
    logger.info("Shutdown complete")


# Initialize FastAPI application
app = FastAPI(
    title="NBA Arbitrage Detection API",
    description="API for detecting arbitrage opportunities in NBA betting markets",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for production use
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if config.ENVIRONMENT == "development" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "NBA Arbitrage Detection API",
        "version": "1.0.0",
        "status": "running",
        "environment": config.ENVIRONMENT
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.

    Returns service health status and dependency checks.
    """
    health_status = {
        "status": "healthy",
        "checks": {
            "database": "unknown",
            "api": "healthy"
        }
    }

    # Check database connection
    try:
        if check_db_connection():
            health_status["checks"]["database"] = "healthy"
        else:
            health_status["checks"]["database"] = "unhealthy"
            health_status["status"] = "degraded"
    except Exception as e:
        logger.error(f"Health check - database error: {str(e)}")
        health_status["checks"]["database"] = "unhealthy"
        health_status["status"] = "degraded"

    status_code = status.HTTP_200_OK if health_status["status"] == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(content=health_status, status_code=status_code)


@app.get("/arbs")
async def get_arbitrage_opportunities():
    """
    Fetch current NBA games and detect arbitrage opportunities.

    Returns:
        Dictionary containing:
        - arbs: List of arbitrage opportunities
        - games_analyzed: Number of games analyzed
        - timestamp: When the analysis was performed
    """
    try:
        logger.info("Received request for arbitrage opportunities")

        # Fetch NBA odds
        games = await fetch_nba_odds()
        logger.info(f"Fetched {len(games)} NBA games")

        if not games:
            logger.warning("No NBA games available")
            return {
                "arbs": [],
                "games_analyzed": 0,
                "message": "No NBA games currently available"
            }

        # Find arbitrage opportunities
        arbs = find_arbitrage_opportunities(games)
        logger.info(f"Found {len(arbs)} arbitrage opportunities")

        return {
            "arbs": arbs,
            "games_analyzed": len(games),
            "opportunities_found": len(arbs)
        }

    except OddsFetchError as e:
        logger.error(f"Error fetching odds: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to fetch odds from external API: {str(e)}"
        )

    except ArbitrageCalculationError as e:
        logger.error(f"Error calculating arbitrage: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate arbitrage opportunities: {str(e)}"
        )

    except Exception as e:
        logger.error(f"Unexpected error in /arbs endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@app.get("/config/info")
async def get_config_info():
    """
    Get non-sensitive configuration information.

    Useful for debugging and verification.
    """
    return {
        "environment": config.ENVIRONMENT,
        "log_level": config.LOG_LEVEL,
        "odds_api_configured": bool(config.ODDS_API_KEY),
        "database_configured": bool(config.DATABASE_URL),
        "twilio_configured": bool(config.TWILIO_ACCOUNT_SID and config.TWILIO_AUTH_TOKEN)
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=config.ENVIRONMENT == "development",
        log_level=config.LOG_LEVEL.lower()
    )
