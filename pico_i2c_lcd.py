# pico_i2c_lcd.py
from lcd_api import LcdApi
from machine import I2C
import time

class I2cLcd(LcdApi):
    # Commands
    LCD_BACKLIGHT = 0x08
    LCD_NOBACKLIGHT = 0x00

    En = 0b00000100 # Enable bit
    Rw = 0b00000010 # Read/Write bit (we keep low)
    Rs = 0b00000001 # Register select bit

    def __init__(self, i2c, i2c_addr, num_lines, num_columns):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.num_lines = num_lines
        self.num_columns = num_columns
        self.backlight = self.LCD_BACKLIGHT
        time.sleep_ms(20)
        self.hal_write_init_nibble(0x03)
        time.sleep_ms(5)
        self.hal_write_init_nibble(0x03)
        time.sleep_ms(1)
        self.hal_write_init_nibble(0x03)
        self.hal_write_init_nibble(0x02)

        cmd = self.LCD_FUNCTION | self.FUNCTION_2LINES
        self.hal_write_command(cmd)
        cmd = self.LCD_DISPLAY_CTRL | self.DISPLAY_ON
        self.hal_write_command(cmd)
        self.clear()
        cmd = self.LCD_ENTRY_MODE | self.ENTRY_LEFT
        self.hal_write_command(cmd)

    def hal_write_init_nibble(self, nibble):
        byte = (nibble << 4)
        self.i2c.writeto(self.i2c_addr, bytearray([byte | self.backlight]))
        self.i2c.writeto(self.i2c_addr, bytearray([byte | self.En | self.backlight]))
        self.i2c.writeto(self.i2c_addr, bytearray([(byte & ~self.En) | self.backlight]))

    def hal_write_command(self, cmd):
        self.hal_write_byte(cmd, 0)

    def hal_write_data(self, data):
        self.hal_write_byte(data, self.Rs)

    def hal_write_byte(self, byte, mode):
        high = byte & 0xF0
        low = (byte << 4) & 0xF0
        self.i2c.writeto(self.i2c_addr, bytearray([high | mode | self.backlight]))
        self.i2c.writeto(self.i2c_addr, bytearray([high | mode | self.En | self.backlight]))
        self.i2c.writeto(self.i2c_addr, bytearray([(high | mode) & ~self.En | self.backlight]))
        self.i2c.writeto(self.i2c_addr, bytearray([low | mode | self.backlight]))
        self.i2c.writeto(self.i2c_addr, bytearray([low | mode | self.En | self.backlight]))
        self.i2c.writeto(self.i2c_addr, bytearray([(low | mode) & ~self.En | self.backlight]))