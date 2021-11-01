FROM python:3.8.10


WORKDIR /usr/src/app


ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip pipenv flake8
COPY Pipfile* ./
RUN pipenv install --system --ignore-pipfile


COPY . .


#RUN flake8 ignore=E501,F401 .
