## set base image ##
FROM python:3.6.8-slim-stretch


## set work folder, if the folder isn't exist, it will auto create the new one ##
WORKDIR  /WebTester


## copy current files to WebTester ##
#ADD . /WebTester
ADD requirements.txt /WebTester

## install gcc libev-dev ##
RUN apt-get update
RUN apt-get -y install gcc
RUN apt-get -y install libev-dev
RUN apt-get install -y iputils-ping



## install python package ##
RUN pip3 install -r requirements.txt


EXPOSE 60001



