#!/bin/bash
export PATH=$PATH:/usr/sbin:/sbin
sleep 1
echo ds3232 0x68 > /sys/class/i2c-adapter/i2c-2/new_device
sleep 1
hwclock -s --rtc=/dev/rtc1
