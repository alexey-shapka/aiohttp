FROM python:3.9

WORKDIR /app

ADD . app/

RUN pip3.9 install -r app/requirements.txt

EXPOSE 8080
EXPOSE 5432
