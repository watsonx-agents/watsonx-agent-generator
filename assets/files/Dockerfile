FROM python:3.12-slim-bullseye as builder

RUN pip install poetry==1.8.3

COPY ./app /app
WORKDIR /app
RUN poetry install

ENTRYPOINT [ "poetry", "run", "python", "{AGENT_NAME}/main.py" ]
