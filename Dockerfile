FROM python:3.10-alpine
COPY . /claim
WORKDIR /claim
# Install necessary packages using apk; handle any build dependencies
RUN apk update && \
  apk add --no-cache curl && \
  apk add --no-cache libressl-dev musl-dev gcc libffi-dev && \
  apk add --no-cache py3-pip && \
  apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev
# Assuming 'age' refers to a tool or library, you need to find the equivalent in Alpine or build from source
# If 'age' is a Python package, install it using pip
RUN curl -o metadata.json https://fluence-dao.s3.eu-west-1.amazonaws.com/metadata.json
RUN pip install -r python/requirements.txt
# Cleanup build dependencies
RUN apk del .build-deps

ENTRYPOINT ["python", "python/proof.py"]