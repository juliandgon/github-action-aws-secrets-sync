# Base image
FROM julgon/alpinelinux-python-boto3:latest

USER root
# Copies your code file  repository to the filesystem
COPY entrypoint.sh ./entrypoint.sh
COPY sync-with-secretsmanager.py ./sync-with-secretsmanager.py

# change permission to execute the script
RUN chmod +x ./entrypoint.sh ./sync-with-secretsmanager.py

USER app
# file to execute when the docker container starts up
ENTRYPOINT ["sh","/home/app/project/entrypoint.sh"]