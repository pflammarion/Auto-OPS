FROM ubuntu:latest

LABEL image.name="autoops"

WORKDIR /app

RUN apt-get update && \
    apt-get install -y python3.9 python3-pip

COPY . /app

RUN python3 -m pip install --upgrade pip && \
    pip3 install -r requirements.txt

