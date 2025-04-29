import time
import machine
import random
from pico_i2c_lcd import I2cLcd
from mlx90614 import MLX90614

# --- Hardware Setup ---
# LCD (I2C0)
i2c_lcd = machine.I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)
# Temp Sensor (I2C1)
i2c_sensor = machine.I2C(1, sda=machine.Pin(10), scl=machine.Pin(11), freq=100000)

# Buttons
button1 = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_UP)
button2 = machine.Pin(3, machine.Pin.IN, machine.Pin.PULL_UP)
button3 = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)

# MOSFET Control (NEW)
mosfet_gate = machine.Pin(15, machine.Pin.OUT)
mosfet_gate.off()  # Start with MOSFET OFF

# Initialize LCD
lcd_devices = i2c_lcd.scan()
if not lcd_devices:
    print("No LCD found!")
    while True: pass
lcd = I2cLcd(i2c_lcd, lcd_devices[0], 2, 16)

# Initialize MLX90614
sensor = MLX90614(i2c_sensor)

# --- Functions ---
def clear_screen():
    lcd.clear()
    lcd.move_to(0, 0)
    time.sleep(0.05)

def wait_for_button():
    while True:
        if not button1.value(): return 1
        if not button2.value(): return 2
        if not button3.value(): return 3
        time.sleep(0.05)

def show_options():
    clear_screen()
    lcd.putstr("1:Apple 2:Kiwi")
    lcd.move_to(1, 0)
    lcd.putstr("3:Orange")

def decide(temp, choice):
    """Decision logic with MOSFET control"""
    decision = "Maybe"  # Default
    
    if temp < 22.0:
        decision = "Yes" if choice == 1 else "Maybe" if choice == 2 else "No"
    elif 22.0 <= temp <= 26.0:
        decision = "Maybe" if choice == 1 else "Yes" if choice == 2 else "Maybe"
    else:
        decision = "No" if choice == 1 else "Maybe" if choice == 2 else "Yes"
    
    # Control MOSFET based on decision (NEW)
    mosfet_gate.value(1 if decision == "Yes" else 0)
    return decision

def restart_program():
    """Reset after showing results"""
    time.sleep(5)  # Show decision for 5 seconds
    mosfet_gate.off()  # Turn off MOSFET
    machine.reset()  # Soft reboot

# --- Main Program ---
def main():
    # Measure temperature
    clear_screen()
    lcd.putstr("Measure temp")
    time.sleep(5)
    
    temps = [sensor.object_temp for _ in range(3)]
    user_temp = sum(temps) / len(temps)
    
    clear_screen()
    lcd.putstr(f"Temp: {user_temp:.1f}C")
    time.sleep(3)
    
    # Show options
    clear_screen()
    lcd.putstr("Pick what you")
    lcd.move_to(1, 0)
    lcd.putstr("resonate with")
    time.sleep(3)
    
    show_options()
    fruit_choice = wait_for_button()
    
    # Make decision
    decision = decide(user_temp, fruit_choice)
    
    # Show result
    clear_screen()
    lcd.putstr("Decision:")
    lcd.move_to(1, 0)
    lcd.putstr(decision)
    
    # Auto-restart (NEW)
    restart_program()

if __name__ == "__main__":
    main()


