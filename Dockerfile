FROM python:3.12-slim
WORKDIR /app
RUN apt -y update && apt -y install netcat-traditional && pip install uv
COPY requirements.txt /app/
RUN uv pip install --system -r requirements.txt
COPY . /app/