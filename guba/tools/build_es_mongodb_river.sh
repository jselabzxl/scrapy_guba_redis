#!/bin/bash

curl -XPUT 'http://172.17.13.207:9200/_river/test_river_guba_post/_meta' -d '{
  "type": "mongodb",
  "mongodb": { 
    "servers":
    [
      { "host": "172.17.13.207", "port": "27020" }
    ],
    "db": "guba", 
    "collection": "post_stock_600010"
  }, 
  "index": { 
    "name": "600010",
    "type": "94_27020"
  }
}'
