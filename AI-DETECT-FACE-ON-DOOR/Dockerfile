# Dockerfile for Jetson Nano
FROM nvcr.io/nvidia/l4t-ml:r32.7.1-py3

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose API port
EXPOSE 8000

# Run both API and AI Engine (Simplified entrypoint)
# In production, you might want to split these into two containers
CMD ["python3", "main.py"]
