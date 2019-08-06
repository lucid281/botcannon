# Pull base image.
FROM ubuntu:latest

ARG redis_ver=5.0.5

# Install Redis.
RUN \
  sed -i 's/# \(.*multiverse$\)/\1/g' /etc/apt/sources.list && \
  apt-get update && \
  apt-get -y upgrade && \
  apt-get install -y build-essential software-properties-common && \
  apt-get install -y zsh curl git htop man unzip vim wget && \
  rm -rf /var/lib/apt/lists/*

RUN \
  cd /tmp && \
  mkdir redis-build && \
  cd redis-build && \
  wget https://github.com/antirez/redis/archive/$redis_ver.tar.gz && \
  tar xvzf $redis_ver.tar.gz && \
  cd redis-$redis_ver && \
  make -j 3 && \
  make install && \
  cp -f src/redis-sentinel /usr/local/bin && \
  rm -rf /tmp/redis-build*

COPY redis.conf /etc/redis.conf


# Define mountable directories.
VOLUME ["/data"]

# Define working directory.
WORKDIR /data/redis

USER 1000
# Define default command.
 CMD ["redis-server", "/etc/redis.conf", "--protected-mode no"]

# Expose ports.
EXPOSE 6379
