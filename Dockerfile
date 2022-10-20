FROM ubuntu:bionic

ENV DEBIAN_FRONTEND noninteractive

ADD ./ /ccdxt
WORKDIR /ccdxt

# Miscellaneous deps
RUN apt-get update && apt-get install -y --no-install-recommends curl git

#gcc
RUN apt-get -y install gcc mono-mcs && \
    rm -rf /var/lib/apt/lists/*

#python
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip python3-dev libpython3.8-dev libevent-dev
# RUN pip3 install --upgrade setuptools

# set the working directory in the container
WORKDIR /code

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip3 install -r requirements.txt

# RUN pip3 install 'web3'

# #mongodb
RUN apt-get install -y mongodb-org

## Remove apt sources
RUN apt-get -y autoremove && apt-get clean && apt-get autoclean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*