FROM ubuntu:latest

LABEL image.name="autoops"

WORKDIR /app

RUN apt-get update && \
    apt-get install -y python3.9 python3-pip

RUN mkdir -p ./tmp

COPY requirements.txt .
COPY controllers .
COPY start.sh .
COPY main.py .

# Install Python dependencies
RUN python3 -m pip install --upgrade pip && \
    pip3 install -r requirements.txt

COPY . .

RUN chmod -R 777 ./tmp

CMD ["sh"]

