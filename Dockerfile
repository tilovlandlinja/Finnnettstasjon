FROM python:3.9-slim

# Set the working directory
WORKDIR /usr/src/app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your script into the container
COPY finnnettstasjon.py .
COPY config.ini .
COPY nettstasjoner_frakart.csv .


# Run the Python script
CMD ["python", "./finnnettstasjon.py"]
#CMD ["/bin/sh"]
