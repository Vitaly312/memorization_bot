FROM python:3.12-slim
COPY requirements.txt /app/
WORKDIR /app
RUN apt -y update && apt -y install netcat-traditional && pip install uv
RUN uv pip install --system -r requirements.txt
COPY . /app/