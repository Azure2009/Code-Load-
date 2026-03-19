FROM python:3.12.6
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]