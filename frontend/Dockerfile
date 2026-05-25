FROM node:20.19.0-bookworm-slim

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . ./

EXPOSE 4200

CMD ["npm", "start"]
