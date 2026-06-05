# Use official lightweight Python image
FROM python:3.12-slim

# Create user with UID 1000 (Hugging Face requires running as user with UID 1000)
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:${PATH}"

# Set the working directory
WORKDIR /app

# Copy dependency definition and install packages
COPY --chown=user backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir --user -r backend/requirements.txt

# Copy all source files
COPY --chown=user . .

# Expose Hugging Face default port
EXPOSE 7860

# Start FastAPI application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
