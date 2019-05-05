#!/bin/bash

DIR=$(cd $(dirname "$0") && pwd)
addr=""

# Kill all running docker containers
docker rm -f $(docker ps -a | cut -c -20 | tail --lines=+2) 2> /dev/null

mkdir -p $DIR/shared

getaddr() {
    addr="$(docker inspect --format='{{.NetworkSettings.IPAddress}}' $1)"
}

build() {
    docker build -t $1 $DIR/$2 || exit 1
}

run() {
    docker run -dP -v $DIR/shared:/shared $*
}

shell() {
    docker run -it -v $DIR/shared:/shared $* /bin/bash
}

######################
# Build everybody

for D in web worker; do
    mkdir -p $DIR/$D/rdb
    cp ../setup.py $DIR/$D/rdb
    cp -r ../rdb $DIR/$D/rdb
done

build web web
build worker worker
build listener ../rdb/listener

######################
# First set up the listener

run -p 0.0.0.0:5000:5000 --name listener listener
getaddr listener
echo listener=$addr > $DIR/shared/addresses

#####################
# Now set up the other guys

# run -p 127.0.0.1:5002:5000 --name worker worker
run -p 0.0.0.0:4444:4444 --name worker worker
getaddr worker
echo worker=$addr >> $DIR/shared/addresses

run -p 0.0.0.0:5001:5000 --name web web
getaddr web
echo web=$addr >> shared/addresses

# docker exec -it worker /bin/bash
