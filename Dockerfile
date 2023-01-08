FROM python:3

WORKDIR /usr/src/app

COPY simulation/main.py main.py

ENTRYPOINT [ "python", "./main.py" ]