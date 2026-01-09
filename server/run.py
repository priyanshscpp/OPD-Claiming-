import uvicorn
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))

    # Render sets RENDER_EXTERNAL_URL in web services
    is_production = os.environ.get("RENDER_EXTERNAL_URL") is not None

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=not is_production
    )
