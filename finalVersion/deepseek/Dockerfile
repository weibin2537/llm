FROM ubuntu:20.04

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    curl \
    bash \
    netcat \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Create startup script with OLLAMA_HOST set to listen on all interfaces
RUN echo '#!/bin/bash\n\
# Set environment variables to make Ollama listen on all interfaces\n\
export OLLAMA_HOST=0.0.0.0:11434\n\
\n\
# Start Ollama service\n\
ollama serve &\n\
\n\
# Wait for Ollama to start\n\
echo "Waiting for ollama to start..."\n\
until nc -z 0.0.0.0 11434; do\n\
  echo "Waiting for ollama to start..."\n\
  sleep 2\n\
done\n\
\n\
echo "Ollama service started successfully!"\n\
\n\
# Pull tinyllama model (the smallest and fastest to load)\n\
echo "Pulling tinyllama model..."\n\
ollama pull tinyllama\n\
\n\
# Keep container running\n\
tail -f /dev/null' > /start-model.sh

# Make script executable
RUN chmod +x /start-model.sh

# Set startup command
CMD ["/start-model.sh"]

# Expose port
EXPOSE 11434
