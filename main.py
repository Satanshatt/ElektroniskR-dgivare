import time
import machine
import random
from mlx90614 import MLX90614

# --------------------- BEFORE RUNNING --------------------- # 
# CHECK THAT THE PINS FOR LED AND BUTTONS ARE CORRECT        #
# ENSURE THAT THE SWITCHES ON THE BOARD ARE IN CORRECT STATE # 
# MICRO CONTROLLER MUST BE CONNECTED TO COMPUTER TO          #
# PRINT TO TERMINAL                                          #
# ENSURE THAT ALL FILES IN REPOSITORY ARE UPLOADED TO THE PI #
# WITH THE EXACT SAME NAME AS IN THE REPOSITORY!             #
# ---------------------------------------------------------- # 


# --- Hardware Setup ---

# Buttons
button1 = machine.Pin(7, machine.Pin.IN, machine.Pin.PULL_UP)
button2 = machine.Pin(8, machine.Pin.IN, machine.Pin.PULL_UP)
button3 = machine.Pin(9, machine.Pin.IN, machine.Pin.PULL_UP)

# Initialize LED pins
# Initialize LED pins and force them OFF immediately
greenLED = machine.Pin(15, machine.Pin.OUT, value=0)  # Starts OFF
redLED = machine.Pin(14, machine.Pin.OUT, value=0)    # Starts OFF
blueLED = machine.Pin(13, machine.Pin.OUT, value=0)   # Starts OFF

# Temp Sensor (I2C1)
i2c_sensor = machine.I2C(1, sda=machine.Pin(10), scl=machine.Pin(11), freq=100000)

# Initialize Temperature sensor
sensor = MLX90614(i2c_sensor)

# --- Helper Functions --- #

def wait_for_button():
    while True:
        if not button1.value(): return 1
        if not button2.value(): return 2
        if not button3.value(): return 3
        time.sleep(0.05)

def turn_LED_ON():
    blueLED.on()
    redLED.on()
    greenLED.on()

def turn_LED_OFF():
    blueLED.off()
    redLED.off()
    greenLED.off()

def clear_terminal():
    print("\033[2J\033[H", end="")
    #Function to clear the terminal, must be tested, don't know if it works 

def user_menu():
    while True:  
        turn_LED_ON()
        print("Press button on robot to start\n")

        button_push = wait_for_button()

        if button_push:
            turn_LED_OFF()

            while True:
                blueLED.on()  
                print("Think of a yes/no question\n")
                print("Press any button when ready\n")
        
                button_push = wait_for_button()
                if button_push:
                    blueLED.off()
                    return None

def get_random_line(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()  # Read all lines into a list
        random_line = random.choice(lines).strip()  # Pick a random line and remove \n
    return random_line

def comment_temp(temp):
    if temp < 25.0:      #luften ger typ temp 24
        print("Cold blooded?\n")
        time.sleep(1)
        print("Now included in my calculations...\n")
        time.sleep(2)
        clear_terminal()

    elif 25.0 <= temp <= 26.0: 
        print("Middle blooded?\n")
        time.sleep(1)
        print("Now included in my calculations...\n")
        time.sleep(2)
        clear_terminal()

    else:
        print("Warm blooded?\n")
        time.sleep(1)
        print("Now included in my calculations...\n")
        time.sleep(2)
        clear_terminal()

def decide(temp, choices):
    """Decision logic with MOSFET control using all three choices"""
    decision = "Maybe"  # Default
    
    # Simple example: count how many times each choice was selected
    choice_counts = {1:0, 2:0, 3:0}
    for choice in choices:
        choice_counts[choice] += 1
    
    if temp < 22.0:
        decision = "Yes" if choice_counts[1] > 1 else "Maybe" if choice_counts[2] > 1 else "No"
    elif 22.0 <= temp <= 26.0:
        decision = "Maybe" if choice_counts[1] > 1 else "Yes" if choice_counts[2] > 1 else "Maybe"
    else:
        decision = "No" if choice_counts[1] > 1 else "Maybe" if choice_counts[2] > 1 else "Yes"
    
    # Control MOSFET based on decision
    greenLED.value(1 if decision == "Yes" else 0)
    redLED.value(1 if decision == "No" else 0)
    blueLED.value(1 if decision == "Maybe" else 0)
    return decision

def restart_program():
    """Reset after showing results"""
    time.sleep(5)  # Show decision for 5 seconds
    clear_terminal()
    turn_LED_OFF()
    machine.reset()  # Soft reboot (check if needed)

# --- Main Function --- #

def main():
    user_menu()

    clear_terminal()

    # Measure temperature
    print("Place finger above oval\n")
    time.sleep(2)
    print("Measuring temperature...\n")
    time.sleep(3)
    
    temps = [sensor.object_temp for _ in range(3)]
    user_temp = sum(temps) / len(temps)
    
    print(f"Temp: {user_temp:.1f}C\n")
    time.sleep(3)

    comment_temp(user_temp)

    # Three rounds of selections
    choices = []
    for round_num in range(3):
        clear_terminal()
        print(f"Round {round_num + 1}: Pick what you resonate with\n")
        time.sleep(3)

        random_line = get_random_line("selections.txt")
        option1, option2, option3 = random_line.split(',')
        
        print(f"1:{option1}\n")
        print(f"2:{option2}\n")
        print(f"3:{option3}\n")

        choices.append(wait_for_button())

    # Make decision based on temperature and all three choices
    decision = decide(user_temp, choices)
    
    # Show result
    clear_terminal()
    print("Decision:" + decision)
    
    restart_program()

if __name__ == "__main__":
    main()

