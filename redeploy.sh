#!/bin/bash

GITOUT=$(git pull)
echo 
echo $GITOUT
while true; do
    read -p "Do you wish to redeploy NoahBot with these git changes? This will replace the image noahbot:latest [Y/n]: " yn
    case $yn in
        [Yy]* ) echo Deploying...; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer Y or n.";;
    esac
done
./discord.sh --webhook-url="https://discord.com/api/webhooks/954046692259422249/L5XcMDMdgiB6S04N3Q-fu1vWkw90y6_QD_oI4NBV9wrs_tFvRPCeokaKihkOhZWOxKNZ" --text=GITOUT
echo

CONTAINER=$(docker ps -a | grep noahbot | cut -d ' ' -f 1)
IMAGE=$(docker images | grep 'noahbot.*latest' | awk '{print $3}')

docker stop $CONTAINER && docker rm $CONTAINER
docker image rm $IMAGE

docker-compose build && docker-compose up -d && docker ps -a

CONTAINER=$(docker ps -a | grep noahbot:latest | cut -d ' ' -f 1)
docker logs -f $CONTAINER
