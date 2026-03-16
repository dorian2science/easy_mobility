FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .

# Receive the build arg and expose it as an env var so Vite picks it up
ARG VITE_GOOGLE_CLIENT_ID
ENV VITE_GOOGLE_CLIENT_ID=$VITE_GOOGLE_CLIENT_ID

RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/templates/default.conf.template
EXPOSE 80
# nginx:alpine includes envsubst; the /docker-entrypoint.d/ mechanism
# auto-processes *.template files from /etc/nginx/templates/ at startup.
CMD ["nginx", "-g", "daemon off;"]
