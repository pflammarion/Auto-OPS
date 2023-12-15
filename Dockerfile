FROM ubuntu:latest

LABEL image.name="autoops"

WORKDIR /app

RUN apt-get update && \
    apt-get install -y python3.9 python3-pip

COPY requirements.txt .

# Install Python dependencies
RUN python3 -m pip install --upgrade pip && \
    pip3 install -r requirements.txt

COPY . .

CMD ["sh"]

# docker build -t autoops .
# docker run -v "$(pwd):/app" -w /app -it autoops bash start.sh
