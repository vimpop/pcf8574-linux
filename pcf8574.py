# make sure to modrpobe i2c-dev
import io
import sys
import fcntl
from time import sleep


I2C_SLAVE = 0x0703
i2caddr = int(sys.argv[1],base=16)

dev = "/dev/i2c-" + sys.argv[2]
#                    D7  D6  D5  D4 LED  E   RW  RS
# uint8 bit contents: x   x   x   x   x   x   x   x

# virtual maps
D0_MASK = (1 << 0)
D1_MASK = (1 << 1)
D2_MASK = (1 << 2)
D3_MASK = (1 << 3)
# physical maps
D4_MASK = (1 << 4)
D5_MASK = (1 << 5)
D6_MASK = (1 << 6)
D7_MASK = (1 << 7)

LED_MASK = (1 << 3)
EN_MASK = (1 << 2)
RS_MASK = (1 << 0)

bus = io.open(dev, "wb", buffering=0)


def write_enable(value):
    value = value | LED_MASK
    bus.write(bytearray([value | EN_MASK]))
    bus.write(bytearray([value & ~EN_MASK]))


def write_command(value, rs=0):
    if rs:
        msb = ((value << 4) & 0xf0) | RS_MASK
        lsb = ((value) & 0xf0) | RS_MASK
    else:
        msb = ((value << 4) & 0xf0) & ~RS_MASK
        lsb = ((value) & 0xf0) & ~RS_MASK
    write_enable(lsb)
    write_enable(msb)


def lcd_print(string):
    for x in string:
        write_command(ord(x), 1)


def lcd_set_cursor(col, row):
    row_offsets = [0x00, 0x40]
    if(row > 2):
        row = 1
    write_command(D7_MASK | (col + row_offsets[row]))  # set DRAMADDR to the respective value


fcntl.ioctl(bus, I2C_SLAVE, i2caddr)
# following figure 24, page 46 of HD44780U datasheet(HD44780_v0.0.pdf)
write_enable(D4_MASK | D5_MASK)  # function set attempt 1
sleep(0.045)
write_enable(D4_MASK | D5_MASK)  # function set attempt 2
sleep(0.045)
write_enable(D4_MASK | D5_MASK)  # function set attempt 3
sleep(0.0015)
write_enable(D5_MASK)  # function set 4-bit
write_command(D5_MASK | D3_MASK | D2_MASK)  # function set lines and character font
write_command(D3_MASK)  # display cursor off, reset
write_command(D0_MASK)  # display clear
write_command(D2_MASK | D1_MASK)  # entry mode set
# init end
write_command(D3_MASK | D2_MASK)  # display on, cursor off,blinking off


lcd_set_cursor(0, 0)
lcd_print("Hello World!")
lcd_set_cursor(0, 1)
lcd_print("btw i use arch")