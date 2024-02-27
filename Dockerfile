FROM python:3.10
COPY ./ .
WORKDIR /
RUN apt update && apt install age
RUN pip install -r python/requirements.txt --require-hashes

ENTRYPOINT ["python", "python/proof.py"]
