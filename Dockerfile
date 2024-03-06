FROM python:3.9-alpine

WORKDIR /app

COPY temp-sensor.py .

RUN pip install --no-cache-dir flask

EXPOSE 5000

ENV FLASK_APP=temp-sensor.py
ENV FLASK_RUN_HOST=0.0.0.0

CMD ["flask", "run", "--no-reload"]
