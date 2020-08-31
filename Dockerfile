FROM python:3.8
# FROM python:3.8-alpine

# RUN apk update \
#  && apk add gcc python3-dev linux-headers libffi-dev \
#  && rm -rf /var/cache/apk/*

COPY conf/pip.conf /etc

RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN mkdir ofertascx
WORKDIR ofertascx
COPY . .

CMD ["python", "ofertascx.py"]
