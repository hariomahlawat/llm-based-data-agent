FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* tsconfig.json vite.config.js ./
COPY src ./src
COPY npm_cache /npm_cache
RUN if [ -d /npm_cache ]; \
    then npm ci --offline --cache /npm_cache; \
    else npm ci; \
    fi \
    && npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
