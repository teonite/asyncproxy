[![TEONITE](http://teonite.com/img/inorbit_by_tnt.png)](http://teonite.com/) Build: [![Circle CI](https://circleci.com/gh/teonite/asyncproxy.svg?style=svg)](https://circleci.com/gh/teonite/asyncproxy) [![codecov.io](https://codecov.io/github/teonite/asyncproxy/coverage.svg?branch=master)](https://codecov.io/github/teonite/asyncproxy?branch=master) [![](https://badge.imagelayers.io/teonite/asyncproxy:latest.svg)](https://imagelayers.io/?images=teonite/asyncproxy:latest 'Get your own badge on imagelayers.io')

Async HTTP proxy
================

Simple asynchronous HTTP proxy with range query parameter support.

## Running using Docker

```
docker-compose pull
docker-compose up -d
```

To run the proxy on different port or address edit the environment section in docker-compose.yml.

## Usage
### Basic usage

```
curl -x http://<proxy_host>:<proxy_port> http://cdn3.sbnation.com/assets/3786371/DOGE-12.jpg -o doge.jpg
```

### Setting range query parameter

```
curl -x http://<proxy_host>:<proxy_port> http://cdn3.sbnation.com/assets/3786371/DOGE-12.jpg?range=bytes=0-9999 -o doge.jpg
```  
  
### Statistics
Statistics are presented as an HTML view. The view can be found at: 

```
http://<proxy_host>:<proxy_port>/stats
```

## Local development
### Install python requirements
Install package requirements using pip:

```
pip install -r requirements.txt
```

### Run locally
To start the proxy locally on default 8000 port run the following command: 

```
python asyncproxy/asyncproxy.py
```
    
### Run tests
To run tests execute the following command (libcurl required, minimum version 7.21.1):

```
python -m tornado.testing asyncproxy/tests.py
```

### Generate coverage report

```
coverage run -m tornado.testing asyncproxy/tests.py
```