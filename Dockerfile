FROM ubuntu:22.04
COPY requirements.txt /app/
WORKDIR /app
RUN apt -y update && apt -y upgrade && apt -y install python3 python3-pip netcat && \
pip install -r requirements.txt
COPY . /app/