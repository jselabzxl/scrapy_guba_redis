#!/bin/bash

curl -XPUT 'http://219.224.135.94:9200/_river/test_river_guba_post/_meta' -d '{
  "type": "mongodb",
  "mongodb": { 
    "servers":
    [
      { "host": "219.224.135.94", "port": "27020" }
    ],
    "db": "guba", 
    "collection": "post_stock_600010"
  }, 
  "index": { 
    "name": "600010",
    "type": "94_27020"
  }
}'
