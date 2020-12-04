#!/bin/bash

raspivid -t 0 -n -l -o tcp://0.0.0.0:8000
