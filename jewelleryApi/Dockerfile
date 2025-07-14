#Dockerfile

# Use the official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app


# Install system dependencies (required for some Python packages)
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*


# Copy only requirements file first (for efficient caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt --index-url https://pypi.org/simple --extra-index-url http://192.168.0.104:8081/repository/packageREPO/simple/ --trusted-host 192.168.0.104


# Copy the project files
COPY . .


# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

