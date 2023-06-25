FROM nginx:1.23.3-alpine-slim
COPY default.conf /etc/nginx/conf.d/default.conf
COPY htpasswd /etc/nginx/.htpasswd
CMD ["nginx", "-g", "daemon off;"]
