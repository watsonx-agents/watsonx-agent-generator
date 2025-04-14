import uvicorn
from fastapi import FastAPI
from {AGENT_NAME}.configs import Logger, Settings
from {AGENT_NAME}.model import agent


app_logger = Logger().logger
app = FastAPI()

@app.post("/inference")
async def inference_endpoint(user_query: str):
    """Endpoint for performing inference of the new agent."""
    app_logger.info("Called inference endpoint")    
    response = agent(user_query) 
    return {"response": response}

@app.get("/test")
async def root():
    app_logger.info("Called TEST endpoint")
    return {"endpoint": "test", "working": True}


if __name__ == "__main__":
    settings: Settings = Settings()
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=settings.debug_mode)
