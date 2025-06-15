FROM python:3.10-slim

WORKDIR /app

# Install system dependencies required by OpenCV and other libraries
# Consolidate apt-get commands for efficiency and install essential build tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    # libxrender-dev is usually for building from source, might not be strictly needed for runtime
    # but keeping it doesn't hurt. Consider removing if image size is critical.
    libxrender-dev \
    # Add any other core build utilities if your packages need to compile anything
    # (e.g., build-essential, cmake, etc. - though often not for simple installs)
    && rm -rf /var/lib/apt/lists/*

# Ensure numpy is installed BEFORE other libraries that depend on it
# to avoid conflicts if they pick up a pre-compiled wheel
COPY requirements.txt .

# Install Python dependencies
# It's good practice to install requirements *after* system dependencies
# and before copying your application code.
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything else (your application code)
COPY . .

# Default command: Run your main.py with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]