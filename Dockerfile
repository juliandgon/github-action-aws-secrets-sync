# Base image
FROM alpine:latest

# installes required packages for our script
RUN apk add --no-cache \
  bash \
  ca-certificates \
  curl \
  jq
  

# Install aws cli tool
RUN apk add --no-cache \
        python3 \
        py3-pip \
    && pip3 install --upgrade pip \
    && pip3 install --no-cache-dir \
        awscli \
    && rm -rf /var/cache/apk/*

RUN pip install boto==2.49.0 boto3==1.17.48 botocore==1.20.48 pyyaml==6.0


# Copies your code file  repository to the filesystem
COPY entrypoint.sh /entrypoint.sh
COPY sync-with-secretsmanager.py /sync-with-secretsmanager.py

# change permission to execute the script and
RUN chmod +x /entrypoint.sh /sync-with-secretsmanager.py

# file to execute when the docker container starts up
ENTRYPOINT ["/entrypoint.sh"]