FROM python:3.7
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

COPY .token main.py ./
COPY ./bot ./bot
COPY ./private_messages_bot ./private_messages_bot
COPY ./wordlist ./wordlist
COPY ./assets ./assets

ENTRYPOINT ["python3"]
CMD ["main.py"]
