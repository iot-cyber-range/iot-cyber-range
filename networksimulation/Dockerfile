FROM python:3.9-alpine

WORKDIR /app

RUN pip install kubernetes requests flask

COPY . .

EXPOSE 8080

CMD ["python3", "app.py"]