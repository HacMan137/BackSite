FROM python:3.11.3-bullseye

COPY ./gunicorn.sh /gunicorn.sh
COPY ./app /app
WORKDIR /app

RUN pip3 install -r ./requirements.txt

WORKDIR /
ENTRYPOINT ["./gunicorn.sh"]