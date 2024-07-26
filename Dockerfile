FROM alpine:3.14 as development

# Set environment variables
ENV NODE_VERSION 14
ENV NPM_VERSION 7
ENV PYTHON_VERSION 3.9
ENV FLASK_DEBUG 1

# Update and install necessary packages
RUN apk update && \
    apk upgrade && \
    apk add --no-cache \
        nodejs=~${NODE_VERSION} \
        npm=~${NPM_VERSION} \
        python3=~${PYTHON_VERSION} \
        py3-pip \
        postgresql-dev \
        gcc \
        g++ \
        python3-dev \
        musl-dev \
        py3-wheel

RUN ln -sf /usr/bin/python${PYTHON_VERSION} /usr/bin/python

RUN node -v && npm -v && python -V && pip -V

WORKDIR /app/frontend

COPY frontend/package*.json ./

# install project dependencies
RUN npm install

# copy project files and folders to the current working directory (i.e. 'app' folder)
COPY frontend/ .

WORKDIR /app
COPY ./backend/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY ./backend/ /app

EXPOSE 8080
EXPOSE 5000

ENTRYPOINT [ "python" ]
CMD ["app.py" ]
#
# FROM node:lts-alpine as production
#
# ENV NODE_ENV $FALU_ENV
#
# # make the 'app' folder the current working directory
# WORKDIR /app
#
# # copy both 'package.json' and 'package-lock.json' (if available)
# COPY package*.json ./
#
# # install project dependencies
# RUN npm install
#
# # install simple http server for serving static content
# RUN npm install http-server
#
# # copy project files and folders to the current working directory (i.e. 'app' folder)
# COPY . .
#
# # build app for production with minification
# RUN npm run build
#
# EXPOSE 8080
# # prod
# CMD [ "./node_modules/.bin/http-server", "dist" ]
