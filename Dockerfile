FROM ubuntu:18.04

# Enable universe repository, install chromedriver
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository universe
RUN apt install -y chromium-chromedriver

RUN apt-get install -y python3.7 python3-pip

COPY MANIFEST.in README.md requirements.txt setup.py /snapper/
COPY snapper /snapper/snapper

WORKDIR /snapper

RUN python3.7 -m pip install --upgrade pip && python3.7 -m pip install .
RUN rm -rf /snapper

WORKDIR /

EXPOSE 8000

ENTRYPOINT ["snap", "-c", "/usr/local/snapper/config.yaml"]
