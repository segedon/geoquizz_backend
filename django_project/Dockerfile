FROM python:3.8
ENV PYTHONUNBUFFERED=1
RUN mkdir /code
COPY . /code
WORKDIR /code
RUN pip install poetry
RUN poetry install