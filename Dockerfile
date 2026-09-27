# =============================================================================
# Dockerfile for Movie Rating Prediction API
# DDM501 - Lab 3: Testing & CI/CD
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: build scikit-surprise
# scikit-surprise 1.1.3 ships only as source, so it needs a C compiler and must
# be built against the pinned numpy (not the latest one pip would pick)
# -----------------------------------------------------------------------------
FROM python:3.10-slim AS builder

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir setuptools wheel "cython<3" numpy==1.26.2 \
    && pip wheel --no-cache-dir --no-build-isolation --no-deps \
       -w /wheels scikit-surprise==1.1.3

# -----------------------------------------------------------------------------
# Stage 2: runtime image
# -----------------------------------------------------------------------------
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements first (for cache optimization)
COPY requirements.txt .

# Install dependencies, using the prebuilt scikit-surprise wheel
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --find-links /wheels -r requirements.txt \
    && rm -rf /wheels

# Copy application code
COPY app/ ./app/
COPY scripts/ ./scripts/
COPY models/ ./models/

# Expose port
EXPOSE 8000

# Health check (slim image has no curl, so use Python)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
