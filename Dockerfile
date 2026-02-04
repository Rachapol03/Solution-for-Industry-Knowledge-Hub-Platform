# Use an official Python runtime as a base image, e.g., python:3.12-slim
# Using a specific version (like 3.12) and a minimal variant (slim) is a best practice
FROM python:3.12-slim AS base

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install the Python dependencies
# The --no-cache-dir flag is recommended to prevent storing unnecessary cache data, reducing image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's source code into the container
COPY . .

# Expose the port the app runs on (change if your app uses a different port)
EXPOSE 5000

# Define the command to run your application when the container starts
# Use the exec form (JSON array) for CMD and ENTRYPOINT for better compatibility
CMD ["python", "app.py"]
