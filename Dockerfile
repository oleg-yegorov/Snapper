FROM python:3.7

# Install Google Chrome
RUN curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo "deb [arch=amd64]  http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
    RUN apt-get -y update && apt-get -y install google-chrome-stable=77.0.3865.90-1

# Install ChromeDriver
RUN wget https://chromedriver.storage.googleapis.com/77.0.3865.40/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip && rm chromedriver_linux64.zip
RUN mv chromedriver /usr/bin/chromedriver
RUN chmod +x /usr/bin/chromedriver

COPY MANIFEST.in README.md requirements.txt setup.py /snapper/
COPY snapper /snapper/snapper

WORKDIR /snapper

RUN pip install --upgrade pip && pip install .
RUN rm -rf /snapper

WORKDIR /

EXPOSE 8000

ENTRYPOINT ["snap", "-c", "/usr/local/snapper/config.yaml"]
