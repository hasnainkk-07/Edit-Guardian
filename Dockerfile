# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project into container
COPY . .

# Set environment variables (optional, override at runtime)
ENV PYTHONUNBUFFERED=1

# Run the module
CMD ["python3", "-m", "Anonymous"]
