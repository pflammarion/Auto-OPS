FROM python:3.9

LABEL image.name="autoops"

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

CMD ["sh"]
