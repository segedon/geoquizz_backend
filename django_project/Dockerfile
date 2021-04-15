FROM python:3.8
ENV PYTHONUNBUFFERED=1
RUN apt-get update
RUN apt-get install -y binutils libproj-dev gdal-bin
RUN mkdir /code
COPY . /code
WORKDIR /code
RUN pip install poetry
RUN poetry install