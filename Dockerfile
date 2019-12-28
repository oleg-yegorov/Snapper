FROM python:3.8

USER root
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash -
RUN apt-get update && apt-get install --no-install-recommends -y nodejs build-essential
RUN npm -g --unsafe-perm install phantomjs
ENV OPENSSL_CONF=/etc/ssl/

COPY MANIFEST.in README.md requirements.txt setup.py /snapper/
COPY snapper /snapper/snapper

WORKDIR /snapper

RUN python3.8 -m pip install --upgrade pip && python3.8 -m pip install .
RUN rm -rf /snapper

WORKDIR /

EXPOSE 8000

ENTRYPOINT ["snap", "-c", "/usr/local/snapper/config.yaml"]
