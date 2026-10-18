# Use official lightweight Python image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install uv and dependencies system-wide in the container
RUN pip install --no-cache-dir uv && \
    uv pip install --system fastapi uvicorn google-genai pillow pydantic requests starlette typing_extensions

# Copy application source code
COPY . .

# Expose port 8000 for Cloud Run traffic
EXPOSE 8000

# Start FastAPI using Uvicorn
CMD ["uvicorn", "backend.py:app", "--host", "0.0.0.0", "--port", "8000"]