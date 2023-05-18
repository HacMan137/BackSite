FROM python:3.11.3-bullseye

COPY ./job_daemon.sh /job_daemon.sh
COPY ./package /package
WORKDIR /package

RUN pip3 install .

WORKDIR /
ENTRYPOINT ["./job_daemon.sh"]