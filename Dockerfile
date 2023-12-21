FROM ubuntu:22.04

LABEL image.name="autoops"

WORKDIR /app

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y python3.9 python3-pip python3-pyqt5 python3-opencv

COPY requirements.txt .

RUN python3 -m pip install --upgrade pip && \
    pip3 install -r requirements.txt

COPY main.py .
COPY controllers controllers
COPY views views
COPY input input
COPY config config
COPY resources resources

RUN mkdir tmp

CMD ["sh"]
