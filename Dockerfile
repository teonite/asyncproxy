FROM python:3.5.1
MAINTAINER Kamil Chudy "kchudy@teonite.com"

COPY asyncproxy asyncproxy
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt
RUN rm requirements.txt

CMD ["python", "asyncproxy/asyncproxy.py"]
