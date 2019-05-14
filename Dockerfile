# Base image.
FROM python:3-slim

COPY requirements.txt /app/

# Update pip and download all dependencies.
RUN pip install -r /app/requirements.txt