FROM python:3.7-alpine3.8 as base
FROM base as builder
RUN apk --no-cache add --update alpine-sdk libffi libffi-dev postgresql-dev musl-dev librdkafka librdkafka-dev
RUN mkdir /install
WORKDIR /install
COPY ./requirements.txt /requirements.txt
RUN pip install --prefix="/install" -r /requirements.txt
FROM base
COPY --from=builder /install /usr/local
RUN apk --no-cache add --update g++ postgresql-dev
COPY ./ /app
WORKDIR /app

RUN python scripts/generate_certificates.py

CMD python walkoff.py -a
