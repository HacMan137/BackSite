FROM python:3.11.3-bullseye

COPY ./gunicorn.sh /gunicorn.sh
COPY ./package /package
WORKDIR /package

RUN pip3 install .

WORKDIR /
ENTRYPOINT ["./gunicorn.sh"]