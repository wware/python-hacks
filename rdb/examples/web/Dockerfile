FROM ubuntu:14.04
MAINTAINER Will Ware <wware@alum.mit.edu>

RUN apt-get update -y
RUN apt-get install -y python-virtualenv python-pip git

RUN sudo echo "America/New_York" > /etc/timezone
RUN sudo dpkg-reconfigure -f noninteractive tzdata

COPY rdb /rdb
RUN pip install -e /rdb

RUN pip install requests

COPY templates /templates
COPY static /static
COPY go.py /

EXPOSE 5000
CMD ["/usr/bin/python", "/go.py"]
