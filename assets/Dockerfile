FROM quay.io/sclorg/python-312-minimal-c9s as builder

RUN pip install poetry==1.8.3

COPY ./app /app
WORKDIR /app
RUN poetry install

ENTRYPOINT [ "poetry", "run", "python", "{AGENT_NAME}/main.py" ]
