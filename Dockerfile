FROM python:3.12-slim

# Set working directory
WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y graphviz && apt-get clean

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY app ./app

# Run Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
