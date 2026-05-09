FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

EXPOSE 19006 8081 19000 19001 19002

CMD ["npm", "run", "start:docker"]