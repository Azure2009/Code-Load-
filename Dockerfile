FROM python:3.12.6

RUN apt-get update && apt-get install -y docker.io

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]