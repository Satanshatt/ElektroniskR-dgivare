# lcd_api.py
import time

class LcdApi:
    LCD_CLR = 0x01
    LCD_HOME = 0x02
    LCD_ENTRY_MODE = 0x04
    LCD_DISPLAY_CTRL = 0x08
    LCD_SHIFT = 0x10
    LCD_FUNCTION = 0x20
    LCD_CGRAM = 0x40
    LCD_DDRAM = 0x80

    ENTRY_RIGHT = 0x00
    ENTRY_LEFT = 0x02
    ENTRY_SHIFT_INC = 0x01
    ENTRY_SHIFT_DEC = 0x00

    DISPLAY_ON = 0x04
    DISPLAY_OFF = 0x00
    CURSOR_ON = 0x02
    CURSOR_OFF = 0x00
    BLINK_ON = 0x01
    BLINK_OFF = 0x00

    FUNCTION_8BIT = 0x10
    FUNCTION_4BIT = 0x00
    FUNCTION_2LINES = 0x08
    FUNCTION_1LINE = 0x00
    FUNCTION_5x10DOTS = 0x04
    FUNCTION_5x8DOTS = 0x00

    def __init__(self, num_lines, num_columns):
        self.num_lines = num_lines
        self.num_columns = num_columns
        self.cursor_x = 0
        self.cursor_y = 0
        self.init_lcd()

    def init_lcd(self):
        raise NotImplementedError

    def hal_write_command(self, cmd):
        raise NotImplementedError

    def hal_write_data(self, data):
        raise NotImplementedError

    def clear(self):
        self.hal_write_command(self.LCD_CLR)
        time.sleep_ms(2)

    def home(self):
        self.hal_write_command(self.LCD_HOME)
        time.sleep_ms(2)

    def move_to(self, row, col):
        addr = col & 0x3F
        if row & 1:
            addr += 0x40
        self.hal_write_command(self.LCD_DDRAM | addr)

    def putchar(self, char):
        self.hal_write_data(ord(char))

    def putstr(self, string):
        for char in string:
            self.putchar(char)