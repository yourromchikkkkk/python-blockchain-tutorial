FROM node:23.1.0 AS builder

WORKDIR /app

COPY frontend/package*.json ./

RUN npm install

COPY frontend/public ./public/
COPY frontend/src ./src/

RUN npm run build

FROM nginx:alpine

COPY --from=builder /app/build /usr/share/nginx/html

COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
