import os
import time
import requests
from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from prometheus_client import Counter, Histogram, make_asgi_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(title="Chatbox API", version="1.0.0")

# Prometheus metrics
REQUEST_COUNT = Counter(
    "chatbox_request_count",
    "Number of requests received by the API",
    ["endpoint", "method", "status_code"]
)
REQUEST_LATENCY = Histogram(
    "chatbox_request_latency_seconds",
    "Request latency in seconds",
    ["endpoint"]
)

# Create metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Configure CORS
origins = [
    "http://localhost:3000",
    os.environ.get("FRONTEND_URL", "http://chatbox-frontend"),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ModelInput(BaseModel):
    message: str

class ModelResponse(BaseModel):
    response: str

# Health check endpoint
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "healthy"}

# API usage metrics endpoint
@app.get("/api/metrics")
async def api_metrics():
    return {
        "total_requests": int(REQUEST_COUNT._metrics["chatbox_request_count_total"]._value),
        "avg_latency": REQUEST_LATENCY._metrics["chatbox_request_latency_seconds_sum"]._value /
                      max(REQUEST_LATENCY._metrics["chatbox_request_latency_seconds_count"]._value, 1)
    }

# Use Ollama API to interact with model
def run_deepseek_model(input_text):
    model_service_url = os.environ.get("MODEL_SERVICE_URL", "http://chatbox-model:11434")
    url = f"{model_service_url}/api/generate"

    payload = {
        "model": "deepseek-r1:7b",
        "prompt": input_text,
        "stream": False
    }
    headers = {"Content-Type": "application/json"}

    try:
        logger.info(f"Sending request to model service: {url}")
        start_time = time.time()
        response = requests.post(url, json=payload, headers=headers, timeout=90)
        response_time = time.time() - start_time
        logger.info(f"Model response received in {response_time:.2f}s")

        response.raise_for_status()
        return response.json().get("response", "")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error requesting model: {e}")
        return {"error": f"Error: {e}"}

@app.post("/chat", response_model=ModelResponse)
async def chat(request: ModelInput, response: Response):
    start_time = time.time()

    try:
        model_response = run_deepseek_model(request.message)
        status_code = status.HTTP_200_OK
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        model_response = {"error": "Internal server error"}
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        response.status_code = status_code

    # Record metrics
    request_time = time.time() - start_time
    REQUEST_COUNT.labels(endpoint="/chat", method="POST", status_code=status_code).inc()
    REQUEST_LATENCY.labels(endpoint="/chat").observe(request_time)

    return {"response": model_response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
