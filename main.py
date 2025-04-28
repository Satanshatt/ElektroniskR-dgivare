import time
import machine
from pico_i2c_lcd import I2cLcd
from mlx90614 import MLX90614

# Setup I2C0 for LCD (GP0, GP1)
i2c_lcd = machine.I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)

# Setup I2C1 for MLX90614 sensor (GP10, GP11)
i2c_sensor = machine.I2C(1, sda=machine.Pin(10), scl=machine.Pin(11), freq=100000)

# Buttons setup
button1 = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_UP)
button2 = machine.Pin(3, machine.Pin.IN, machine.Pin.PULL_UP)
button3 = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)

# Initialize LCD
lcd_devices = i2c_lcd.scan()
if not lcd_devices:
    print("No LCD found!")
    while True:
        pass
lcd = I2cLcd(i2c_lcd, lcd_devices[0], 2, 16)

# Initialize MLX90614
sensor = MLX90614(i2c_sensor)

def clearScreen():
    lcd.clear()
    lcd.move_to(0, 0)
    time.sleep(0.05)

def wait_for_button():
    """Wait for one of the three buttons to be pressed."""
    while True:
        if not button1.value():
            return 1
        if not button2.value():
            return 2
        if not button3.value():
            return 3
        time.sleep(0.05)

def show_options():
    clearScreen()
    lcd.putstr("1:Apple 2:Kiwi")
    lcd.move_to(1, 0)  # move_to(col, row)
    lcd.putstr("3:Orange")

def decide(temp, fruit_choice):
    """Decision based on finger temperature."""
    if temp < 22.0:
        if fruit_choice == 1:
            return "Yes"
        elif fruit_choice == 2:
            return "Maybe"
        else:
            return "No"
    elif 22.0 <= temp <= 26.0:
        if fruit_choice == 1:
            return "Maybe"
        elif fruit_choice == 2:
            return "Yes"
        else:
            return "Maybe"
    else:
        if fruit_choice == 1:
            return "No"
        elif fruit_choice == 2:
            return "Maybe"
        else:
            return "Yes"

# --- Program start ---

# Step 1: Measure temperature
clearScreen()
lcd.putstr("Measure temp")
time.sleep(2)

# Average 3 readings for stability
temps = []
for _ in range(3):
    temps.append(sensor.object_temp)
    time.sleep(0.5)

user_temp = sum(temps) / len(temps)

clearScreen()
lcd.putstr(f"Temp: {user_temp:.1f}C")
time.sleep(3)

# Step 2: Ask first question
clearScreen()
lcd.putstr("Pick a fruit")
time.sleep(2)

show_options()

# Step 3: Wait for fruit choice
fruit_choice = wait_for_button()

# Step 4: Make decision
decision = decide(user_temp, fruit_choice)

# Step 5: Show result
clearScreen()
lcd.putstr("Decision:")
lcd.move_to(1, 0)
lcd.putstr(decision)

# Also print to console
print(f"User Temp: {user_temp:.2f}C")
print(f"Fruit Choice: {fruit_choice}")
print(f"Decision: {decision}")

# Done
while True:
    time.sleep(1)

