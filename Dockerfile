FROM python:3.10
COPY ./ .
WORKDIR /
RUN apt update && apt install age
RUN curl -o metadata.json https://fluence-dao.s3.eu-west-1.amazonaws.com/metadata.json
RUN pip install -r python/requirements.txt

ENTRYPOINT ["python", "python/proof.py"]
