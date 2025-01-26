FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt /app/

RUN apt-get update && apt-get install -y \
  build-essential \
  libpq-dev
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

CMD ["python", "-m", "app.main"]
