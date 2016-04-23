#!/bin/bash
sudo apt-get update
sudo apt-get install python-dev python-pip libxml2-dev libxslt1-dev zlib1g-dev libffi-dev libssl-dev redis-server
sudo pip install Scrapy scrapy_redis
