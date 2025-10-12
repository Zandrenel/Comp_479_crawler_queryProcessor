# Use the official Python base image
FROM python:3.12.4

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install Flask and other dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m nltk.downloader -d /root/nltk_data stopwords


# Copy the content of the local src directory to the working directory
COPY static/ .
RUN ls


EXPOSE 8000


# Specify the command to run on container start
CMD ["uwsgi", "--http", "127.0.0.1:8000", "--master", "-p", "4", "-w", "server:app"]