import digitalio
import board
from stm32loader.main import main
import time

stm_reset = digitalio.DigitalInOut(board.pin.PC3)
stm_reset.direction = digitalio.Direction.OUTPUT
stm_reset.value = False
stm_boot = digitalio.DigitalInOut(board.pin.PG8)
stm_boot.direction = digitalio.Direction.OUTPUT
stm_boot.value = False
stm_boot.value = True
time.sleep(1)
stm_reset.value = True
time.sleep(1)
stm_reset.value = False
time.sleep(1)
main("-p", "/dev/ttyS1", "-e", "-w", "-v", f'/home/microlink/gpio_b3.bin')
# result = main("-p", "/dev/ttyS1", "-e", "-w", "-v", f'/var/www/web-ups1600/static/files/upload/stm32.bin')
# if result == 'Verification OK':
#     print('Succses')
# else:
#     print('Error')
