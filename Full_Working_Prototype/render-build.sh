#!/usr/bin/env bash
set -e
cd backend
pip install -r requirements.txt
cd ../engine
g++ -o engine_linux main.cpp
chmod +x engine_linux
