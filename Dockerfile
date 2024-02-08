FROM python:3.10

RUN pip install --upgrade pip
RUN pip install fastapi sqlalchemy sqlmodel psycopg2 uvicorn bcrypt

COPY ./api /api

WORKDIR /api

ENTRYPOINT "uvicorn" "--host" "0.0.0.0" "main:app"
