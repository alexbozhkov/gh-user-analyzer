FROM node:20.19.0-bookworm-slim

RUN apt-get update -qq && apt-get install -y -qq --no-install-recommends chromium \
  && rm -rf /var/lib/apt/lists/*

ENV CHROME_BIN=/usr/bin/chromium

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . ./

EXPOSE 4200

CMD ["npm", "start"]
