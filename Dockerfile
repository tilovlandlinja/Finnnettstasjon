FROM python:3.9-slim

# Set the working directory
WORKDIR /usr/src/app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your script into the container
COPY finnnettstasjon.py .

# Run the Python script
CMD ["python", "./finnnettstasjon.py"]
