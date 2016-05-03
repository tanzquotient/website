#!/bin/sh

CMD="drop database tq_website; CREATE database tq_website DEFAULT CHARACTER SET utf8;"

echo $CMD | mysql -h 127.0.0.1 --port=3309 -u root -proot

