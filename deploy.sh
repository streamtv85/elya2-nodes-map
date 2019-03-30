#!/usr/bin/env bash

APP_NAME=elyamap

IMAGE=$REGISTRY/jora/elyamap-app

#pull the latest image
docker pull $IMAGE:latest

#stop the containers we are going to rebuild
docker container stop $APP_NAME

#remove all the containers which are not running
#docker rm $(docker ps -a -q)

#remove our container
docker rm $APP_NAME

#remove the image of currently running app
docker rmi $IMAGE:current


docker tag $IMAGE:latest $IMAGE:current

#run the container we need
docker run -d --name $APP_NAME --restart unless-stopped -p 8081:8050 $IMAGE:latest


