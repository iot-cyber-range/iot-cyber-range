FROM python:3.9-alpine

WORKDIR /app

COPY humidity-sensor.py .

RUN pip install --no-cache-dir flask

EXPOSE 5000

CMD ["python3", "humidity-sensor.py"]