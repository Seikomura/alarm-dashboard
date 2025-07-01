FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py data_utils.py ./

# expose Dash app via gunicorn
CMD gunicorn --workers 2 --threads 2 --timeout 180 --bind 0.0.0.0:8000 app:server

EXPOSE 8000
