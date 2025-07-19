# Use a lightweight Python base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt first to leverage Docker's build cache.
COPY requirements.txt .

# Install Python dependencies. --no-cache-dir reduces image size.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Declare that the container will listen on port 8501
EXPOSE 8501

# Command to run the Streamlit application.
CMD [ "streamlit", "run", "main.py", "--server.port", "8501", "--server.address", "0.0.0.0" ]