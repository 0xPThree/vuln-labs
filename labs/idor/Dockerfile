FROM node:14

WORKDIR /app

# Copy only package files first to leverage Docker cache
COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 3000

CMD ["node", "index.js"]