FROM python:3.11.2-bullseye

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install gdal
RUN pip install --no-cache-dir -r requirements.txt