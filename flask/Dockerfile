FROM python:3.11.2-slim

WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt

ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
