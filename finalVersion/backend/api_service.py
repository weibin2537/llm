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

# Configure CORS - more permissive for development
origins = [
    "http://localhost:3000",
    "http://localhost",
    "http://myapp.local",
    "http://chatbox-frontend",
    os.environ.get("FRONTEND_URL", "http://chatbox-frontend"),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for debugging
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ModelInput(BaseModel):
    message: str

class ModelResponse(BaseModel):
    response: str

# Function to check model status and ensure it's loaded
def ensure_model_loaded(model_name="tinyllama"):
    """Check if model is loaded and ready for inference"""
    model_service_url = os.environ.get("MODEL_SERVICE_URL", "http://chatbox-model:11434")

    try:
        # Log the URL we're trying to access
        logger.info(f"Checking model status at {model_service_url}")

        # Check if Ollama server is running
        health_url = f"{model_service_url}/api/tags"
        logger.info(f"Sending request to {health_url}")

        response = requests.get(health_url, timeout=10)
        logger.info(f"Response status: {response.status_code}")

        if response.status_code == 200:
            models = response.json().get("models", [])

            # Check if our model is in the list of loaded models
            if any(model.get("name") == model_name for model in models):
                logger.info(f"Model {model_name} is loaded and ready")
                return True
            else:
                logger.info(f"Model {model_name} not found, trying to pull it")
                # If model not found, try to pull it
                pull_url = f"{model_service_url}/api/pull"
                pull_response = requests.post(
                    pull_url,
                    json={"name": model_name},
                    timeout=60
                )

                if pull_response.status_code == 200:
                    logger.info(f"Successfully pulled model {model_name}")
                    return True
                else:
                    logger.error(f"Failed to pull model: {pull_response.text}")
                    return False
        else:
            logger.error(f"Ollama service health check failed: {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        logger.error(f"Error checking model status: {e}")
        return False

# Health check endpoint
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "healthy"}

# API usage metrics endpoint
@app.get("/api/metrics")
async def api_metrics():
    try:
        total_requests = int(REQUEST_COUNT._metrics.get("chatbox_request_count_total", {})._value or 0)
        avg_latency = 0

        latency_sum = REQUEST_LATENCY._metrics.get("chatbox_request_latency_seconds_sum", {})._value or 0
        latency_count = REQUEST_LATENCY._metrics.get("chatbox_request_latency_seconds_count", {})._value or 0

        if latency_count > 0:
            avg_latency = latency_sum / latency_count

        return {
            "total_requests": total_requests,
            "avg_latency": avg_latency
        }
    except Exception as e:
        logger.error(f"Error calculating metrics: {e}")
        return {
            "total_requests": 0,
            "avg_latency": 0,
            "error": str(e)
        }

# Use Ollama API to interact with model - updated to use phi3:mini
def run_model(input_text):
    # Choose ONE of these models - phi3:mini is recommended but you can switch to others if needed
    model_name = "phi3:mini"
    # Alternative models:
    # model_name = "orca-mini:3b"
    # model_name = "tinyllama"

    model_service_url = os.environ.get("MODEL_SERVICE_URL", "http://chatbox-model:11434")
    url = f"{model_service_url}/api/generate"

    payload = {
        "model": model_name,
        "prompt": input_text,
        "stream": False,
        "options": {
            "num_ctx": 2048,      # Limit context size
            "num_thread": 4,      # Limit thread count for better stability
            "temperature": 0.7,   # Slightly reduced temperature for more consistent responses
            "top_k": 40,          # Keep reasonable variety
            "top_p": 0.9          # Filter less probable tokens
        }
    }
    headers = {"Content-Type": "application/json"}

    try:
        logger.info(f"Sending request to model service: {url}")
        start_time = time.time()

        # First ensure model is loaded
        if not ensure_model_loaded(model_name):
            return "Model is still loading or unavailable. Please try again in a few moments."

        # Send request to model service
        response = requests.post(url, json=payload, headers=headers, timeout=90)
        response_time = time.time() - start_time
        logger.info(f"Model response received in {response_time:.2f}s")

        response.raise_for_status()
        # Safely extract the response text
        if response.status_code == 200:
            response_data = response.json()
            if isinstance(response_data, dict) and "response" in response_data:
                return response_data["response"]
            else:
                logger.warning(f"Unexpected response format: {response_data}")
                return "Received unexpected response format from model service."
        else:
            return f"Error: Status code {response.status_code}"
    except requests.exceptions.RequestException as e:
        logger.error(f"Error requesting model: {e}")
        # Return a string instead of a dict for error cases
        return f"Error connecting to model service: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error in run_model: {e}")
        return f"Unexpected error: {str(e)}"

@app.post("/chat", response_model=ModelResponse)
async def chat(request: ModelInput, response: Response):
    start_time = time.time()

    try:
        model_response = run_model(request.message)
        status_code = status.HTTP_200_OK
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        model_response = f"I'm sorry, I encountered an error while processing your request: {str(e)}"
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
