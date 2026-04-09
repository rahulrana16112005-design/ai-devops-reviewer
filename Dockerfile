FROM ubuntu:latest   # ❌ latest tag

RUN apt-get update && apt-get install -y python3

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt   # ❌ no cache control

ENV PASSWORD=admin123   # ❌ secret in env

CMD ["python3", "app.py"]
