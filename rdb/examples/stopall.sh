#!/bin/bash

docker rm -f $(docker ps -a | cut -c -20 | tail --lines=+2)
