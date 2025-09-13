#!/bin/bash

# Install Chrome
apt-get update
apt-get install -y wget unzip xvfb libxi6 libgconf-2-4

# Download Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt install -y ./google-chrome-stable_current_amd64.deb
