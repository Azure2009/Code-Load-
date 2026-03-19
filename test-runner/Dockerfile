FROM python:3.12.6

WORKDIR /app
RUN pip install pytest

COPY code_tester.py /app
COPY test_solution.py /app

ENV PYTHONPATH=/app

CMD ["python", "code_tester.py"]
