FROM nginx:alpine

# Copiamos los frontends
COPY ./get-test /usr/share/nginx/html/get-test
COPY ./post-test /usr/share/nginx/html/post-test

# Configuramos NGINX
COPY ./nginx/default.conf /etc/nginx/conf.d/default.conf