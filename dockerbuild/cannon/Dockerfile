FROM python:3.7-buster

# stuff for python packages and 'system'
RUN \
  sed -i 's/# \(.*multiverse$\)/\1/g' /etc/apt/sources.list && \
  apt-get update && \
  apt-get -y upgrade && \
  apt-get install -y build-essential software-properties-common ca-certificates gcc && \
  apt-get install -y bash curl git htop man unzip vim wget docker.io && \
  rm -rf /var/lib/apt/lists/*
# copy/rename script bc to run as ./botcannon and copy source
COPY botcannon-script /home/developer/botcannon

# Replace 1000 with your user / group id
RUN export uid=1000 gid=1000 && \
    mkdir -p /home/developer && \
    echo "developer:x:${uid}:${gid}:Developer,,,:/home/developer:/bin/bash" >> /etc/passwd && \
    echo "developer:x:${uid}" >> /etc/group && \
    echo "dialout:x:20:developer" >> /etc/group && \
    echo "docker:x:127:developer" >> /etc/group && \
#    echo "developer ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/developer && \
#    chmod 0440 /etc/sudoers.d/developer && \
    chown ${uid}:${gid} -R /home/developer && \
    chmod +x /home/developer/botcannon

# limit container exec to a user matching your uid
USER developer

ENV HOME "/home/developer"
ENV PYTHONPATH "/usr/src/:$PYTHONPATH"  # prefer /usr/src
ENV PATH "~/.local/bin/:$PATH"

# Setup BotCannon's dependencies
COPY botcannon/requirements.txt /home/developer/requirements.txt
RUN pip3 install --user -r /home/developer/requirements.txt

# Setup BotCannon and your bot's dependencies
COPY bot-requirements.txt /home/developer/bot-requirements.txt
RUN pip3 install --user -r /home/developer/bot-requirements.txt

WORKDIR /home/developer
