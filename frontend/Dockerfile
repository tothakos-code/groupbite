FROM node:lts-alpine as development

# make the 'app' folder the current working directory
WORKDIR /app

# copy both 'package.json' and 'package-lock.json' (if available)
COPY package*.json ./

# install project dependencies
RUN npm install

# copy project files and folders to the current working directory (i.e. 'app' folder)
COPY . .

EXPOSE 8080
CMD ["npm", "run", "serve"]

FROM node:lts-alpine as production

# make the 'app' folder the current working directory
WORKDIR /app

# install simple http server for serving static content
RUN npm install http-server

# copy both 'package.json' and 'package-lock.json' (if available)
COPY package*.json ./

# install project dependencies
RUN npm install

# copy project files and folders to the current working directory (i.e. 'app' folder)
COPY . .

# build app for production with minification
RUN npm run build

EXPOSE 8080
# prod
CMD [ "http-server", "dist" ]
