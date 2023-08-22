FROM python:3.8-alpine

RUN apk add postgresql-dev gcc python3-dev musl-dev

COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt

COPY . /app

ENV FLASK_DEBUG 1

ENTRYPOINT [ "python" ]
CMD ["app.py" ]
