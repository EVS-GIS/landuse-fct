FROM python:3.11.2-bullseye

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install -r requirements.txt
RUN pip install GDAL==3.4.3