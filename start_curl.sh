#!/bin/bash
IPV4=$(/bin/sed -n '1{p;q;}' /home/microlink/ip_cur)
MASKV4=$(/bin/sed -n '2{p;q;}' /home/microlink/ip_cur)
GATEV4=$(/bin/sed -n '3{p;q;}' /home/microlink/ip_cur)
/bin/sed -i 's/address.*/address '$IPV4'/; s/netmask.*/netmask '$MASKV4'/; s/gateway.*/gateway '$GATEV4'/' /etc/network/interfaces
/bin/sed -i 's/ServerName.*/ServerName '$IPV4'/' /etc/apache2/sites-available/web-ups1600.conf
/bin/sed -i 's/nameserver.*/nameserver '$GATEV4'/' /etc/resolv.conf
sleep 3
ip link set dev end0 up
service networking restart
sleep 2
curl $IPV4

