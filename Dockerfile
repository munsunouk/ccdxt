FROM ubuntu:bionic

ENV DEBIAN_FRONTEND noninteractive

ADD ./ /ccdxt
WORKDIR /ccdxt

# Update packages (use us.archive.ubuntu.com instead of archive.ubuntu.com — solves the painfully slow apt-get update)
# RUN sed -i 's/archive\.ubuntu\.com/us\.archive\.ubuntu\.com/' /etc/apt/sources.li


# Miscellaneous deps
RUN apt-get update && apt-get install -y --no-install-recommends curl git

#gcc
RUN apt-get -y install gcc mono-mcs && \
    rm -rf /var/lib/apt/lists/*

#python
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip python3-dev libpython3.8-dev libevent-dev
# RUN pip3 install --upgrade setuptools
RUN pip3 install 'web3==5.31.0'
RUN pip3 install 'eth-tester==0.7.0b1'

# #mongodb
# RUN apt-get install -y mongodb-org

## Remove apt sources
RUN apt-get -y autoremove && apt-get clean && apt-get autoclean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*