FROM python:3.11.2-slim

WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt

# NOTE: Running gunicorn with 3 workers listening on port 8000
#       Need to bind server to all IPs (0.0.0.0) so other containers can connect
#       Module for the program is called 'app' and variable is called 'app'
#
ENTRYPOINT ["gunicorn", "-w", "3", "-b", "0.0.0.0:8000", "app:app"]
