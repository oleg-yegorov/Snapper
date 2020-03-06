FROM nginx:alpine
RUN rm /etc/nginx/conf.d/default.conf
COPY http_redirect.conf /etc/nginx/conf.d
COPY js_redirect.html /usr/share/nginx/html
COPY meta_redirect.html /usr/share/nginx/html
