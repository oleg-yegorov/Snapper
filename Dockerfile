FROM ubuntu:18.04

# install Phantomjs
USER root
RUN apt-get update && apt-get install -y curl
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash -
RUN apt-get update && apt-get install --no-install-recommends -y nodejs build-essential
RUN npm -g --unsafe-perm install phantomjs
ENV OPENSSL_CONF=/etc/ssl/

# Enable universe repository, install chromedriver
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository universe
RUN apt install -y chromium-chromedriver

# install python
RUN apt-get install -y python3.8 python3-pip

COPY MANIFEST.in README.md requirements.txt setup.py KVersion /snapper/
COPY snapper /snapper/snapper

WORKDIR /snapper

RUN python3.8 -m pip install --upgrade pip && python3.8 -m pip install .
RUN rm -rf /snapper

WORKDIR /

EXPOSE 8000

ENTRYPOINT ["snap", "-c", "/usr/local/snapper/config.yaml"]
