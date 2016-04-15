#!/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/root/bin:/root/go/bin:/usr/local/go/bin:/root/bin
cd /root/live/
nohup python indeedDaily.py > /root/logs/nohupDaily.out
