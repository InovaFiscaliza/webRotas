"""FastAPI application initialization and configuration"""

import sys
import argparse
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from api.routes import process, health
from server_env import env


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app startup and shutdown lifecycle"""
    # Startup
    try:
        args = parse_args()
        env.get_port(args.port)
        env.save_server_data()
        print(f"[webRotas] Server starting on port {env.port}")
    except Exception as e:
        print(f"[webRotas] Startup error: {e}")
        raise

    yield

    # Shutdown
    try:
        env.clean_server_data()
        print("[webRotas] Server shutdown")
    except Exception as e:
        print(f"[webRotas] Cleanup error: {e}")


# Create FastAPI application
app = FastAPI(
    title="webRotas",
    description="Vehicle route management for ANATEL inspection activities",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add CORS middleware (allow all origins, methods, headers)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GZIP compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routers FIRST (so they have priority over static mount)
app.include_router(process.router, prefix="", tags=["routing"])
app.include_router(health.router, prefix="", tags=["health"])

# Mount static files AFTER routers (so API endpoints take precedence)
static_path = Path(__file__).parent / "static"
if static_path.exists():
    try:
        # Mount at root to serve index.html and other assets
        app.mount("/", StaticFiles(directory=str(static_path), html=True), name="webRotas_static")
        print(f"[webRotas] Static files mounted at / from {static_path}")
    except Exception as e:
        print(f"[webRotas] Warning: Could not mount static files: {e}")
else:
    print(f"[webRotas] Warning: Static directory not found at {static_path}")


@app.get(
    "/",
    summary="Root endpoint",
    description="Serve webRotas interface",
    include_in_schema=False
)
async def root():
    """Serve root - return index.html"""
    index_path = Path(__file__).parent / "static" / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    raise HTTPException(status_code=404, detail="index.html not found")


@app.get(
    "/index.html",
    summary="Index page",
    description="Serve index.html directly",
    include_in_schema=False
)
async def index():
    """Serve index.html"""
    index_path = Path(__file__).parent / "static" / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    raise HTTPException(status_code=404, detail="index.html not found")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description="WebRotas Server")

    parser.add_argument(
        "--port",
        type=int,
        default=env.port,
        help=f"Server port (default: {env.port})",
    )

    parser.add_argument(
        "--debug",
        type=bool,
        default=env.debug_mode,
        help=f"Debug mode (default: {env.debug_mode})",
    )

    try:
        args, unknown = parser.parse_known_args()
        if unknown:
            print(f"[webRotas] Warning: Unknown arguments ignored: {unknown}")
            print(
                f"[webRotas] Using default values: port={env.port}, debug={env.debug_mode}"
            )
        return args

    except Exception as e:
        print(f"[webRotas] Error parsing arguments: {e}")
        print(
            f"[webRotas] Using default values: port={env.port}, debug={env.debug_mode}"
        )
        return argparse.Namespace(port=env.port, debug=env.debug_mode)


def main():
    """Main entry point"""
    try:
        import uvicorn

        args = parse_args()

        print(f"[webRotas] Starting FastAPI server on port {args.port}")
        print(f"[webRotas] API documentation available at http://0.0.0.0:{args.port}/docs")

        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=args.port,
            reload=False,
            log_level="info",
        )
        return 0

    except Exception as e:
        print(f"[webRotas] Server error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
