import digitalio
import board
import smbus
from stm32loader.main import main
import time
import os


def lcd_init():
    # Initialise display
    _e = False
    try:
        lcd_byte(0x30, LCD_CMD)  # 110000 Initialise
    except BlockingIOError as _err:
        _e = False
    else:
        lcd_byte(0x02, LCD_CMD)  # 000010 Initialise
        # lcd_byte(0x32, LCD_CMD)  # 110010 Initialise
        # lcd_byte(0x06, LCD_CMD)  # 000110 Cursor move direction
        lcd_byte(0x0C, LCD_CMD)  # 001100 Display On,Cursor Off, Blink Off
        lcd_byte(0x28, LCD_CMD)  # 101000 Data length, number of lines, font size
        lcd_byte(0x01, LCD_CMD)  # 000001 Clear display
        lcd_byte(LCD_LINE_1, LCD_CMD)  # 10000000 переход на 1 строку
        time.sleep(E_DELAY)
        _e = True
    finally:
        return _e


def lcd_byte(bits, mode):
    # Send byte to data pins
    # bits = the data
    # mode = 1 for data
    #        0 for command
    bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
    bits_low = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT
    # High bits
    bus.write_byte(I2C_ADDR, bits_high)
    lcd_toggle_enable(bits_high)
    # Low bits
    bus.write_byte(I2C_ADDR, bits_low)
    lcd_toggle_enable(bits_low)


def lcd_toggle_enable(bits):
    # Toggle enable
    time.sleep(E_DELAY)
    bus.write_byte(I2C_ADDR, (bits | ENABLE))
    time.sleep(E_PULSE)
    bus.write_byte(I2C_ADDR, (bits & ~ENABLE))
    time.sleep(E_DELAY)


def lcd_string(message, line):
    if lcd_error:
        # Send string to display
        message = message.ljust(LCD_WIDTH, " ")
        lcd_byte(line, LCD_CMD)
        for i in range(LCD_WIDTH):
            lcd_byte(ord(message[i]), LCD_CHR)


# Initialise display
# Define some device parameters
I2C_ADDR = 0x27  # I2C device address
LCD_WIDTH = 16  # Maximum characters per line

# Define some device constants
LCD_CHR = 1  # Mode - Sending data
LCD_CMD = 0  # Mode - Sending command
# LCD_SETCGRAMADDR = 0x40
LCD_LINE_1 = 0x80  # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0  # LCD RAM address for the 2nd line

LCD_BACKLIGHT = 0x08  # On
# LCD_BACKLIGHT = 0x00  # Off

ENABLE = 0b00000100  # Enable bit

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

START_CURL_SH = ["IPV4=$(/bin/sed -n '1{p;q;}' /home/microlink/ip_cur)\n",
                 "MASKV4=$(/bin/sed -n '2{p;q;}' /home/microlink/ip_cur)\n",
                 "GATEV4=$(/bin/sed -n '3{p;q;}' /home/microlink/ip_cur)\n",
                 "/bin/sed -i '0,/address.*/s//address '$IPV4'/; s/netmask.*/netmask '$MASKV4'/; s/gateway.*/gateway "
                 "'$GATEV4'/' /etc/network/interfaces\n",
                 "/bin/sed -i 's/ServerName.*/ServerName '$IPV4'/' /etc/apache2/sites-available/web-ups1600.conf\n",
                 "/bin/sed -i 's/nameserver.*/nameserver '$GATEV4'/' /etc/resolv.conf\n",
                 "sleep 1\n",
                 "service networking restart\n",
                 "sleep 5\n",
                 "/sbin/ethtool -s end0 speed 100 duplex full autoneg off\n",
                 "sleep 5\n",
                 "curl $IPV4\n",
                 "sleep 2\n",
                 "curl $IPV4\n"]


bus = smbus.SMBus(0)
lcd_error = lcd_init()
lcd_string('Update process..', LCD_LINE_1)
lcd_string('Step 2 - wait...', LCD_LINE_2)

os.system("sudo /sbin/apachectl stop")
time.sleep(20)
stm_reset = digitalio.DigitalInOut(board.pin.PC3)
stm_reset.direction = digitalio.Direction.OUTPUT
stm_reset.value = False
stm_boot = digitalio.DigitalInOut(board.pin.PG8)
stm_boot.direction = digitalio.Direction.OUTPUT
stm_boot.value = False
stm_boot.value = True
time.sleep(0.5)
stm_reset.value = True
time.sleep(1)
stm_reset.value = False
time.sleep(0.5)
main("-p", "/dev/ttyS1", "-e", "-w", "-v", f'/var/www/web-ups1600/static/files/upload/stm32.bin')
stm_boot.value = False
time.sleep(0.5)
stm_reset.value = True
time.sleep(1)
stm_reset.value = False
with open(f"/home/microlink/start_curl.sh", 'w') as curl_f:
    curl_f.writelines(START_CURL_SH)
os.system("sudo /sbin/reboot")
