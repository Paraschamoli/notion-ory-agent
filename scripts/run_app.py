import uvicorn
from src.config import settings
from src.api.main import create_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False
    )