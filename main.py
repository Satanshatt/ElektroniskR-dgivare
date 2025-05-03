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
button1 = machine.Pin(7, machine.Pin.IN, machine.Pin.PULL_UP)
button2 = machine.Pin(8, machine.Pin.IN, machine.Pin.PULL_UP)
button3 = machine.Pin(9, machine.Pin.IN, machine.Pin.PULL_UP)

# MOSFET Control (NEW)
greenLED = machine.Pin(15, machine.Pin.OUT)
redLED = machine.Pin(14, machine.Pin.OUT)
blueLED = machine.Pin(13, machine.Pin.OUT)

# Start with MOSFET OFF to turn all LED off 
redLED.off()
greenLED.off()
blueLED.off()

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

def turnLEDOff():
    redLED.off()
    greenLED.off()
    blueLED.off()

#generates a random set of options and returns the 3 options as 3 separate variables 
def generateOptions(optionList):
    randomInt = random.randint(0, len(optionList) - 1)
    options = optionList[randomInt]  # Get the list of options at the specified index
    option1, option2, option3 = None, None, None  # Initialize the three variables

    # Sort the options into option1, option2, option3
    # Assuming the options are ordered and should be assigned directly:
    if len(options) >= 1:
        option1 = options[0]  # First option
    if len(options) >= 2:
        option2 = options[1]  # Second option
    if len(options) >= 3:
        option3 = options[2]  # Third option

    return option1, option2, option3
  
#Reads from file once, returns a list with lists with the different sets of options e.g [1: kiwi, lemon, mango], [2: blue, black, green]
def read_options_from_file(filename):
    optionsList = [] #Create an empty list which will contain lists of the different options 
    with open(filename + '.txt', 'r') as file: #open the file with all options with format "kiwi,lemon,lime"
    # Read each line in the file
        for line in file: 
            options = [] #Create an empty list to store the options in
            for word in line.split(","): #Split the line by commas 
                options.append(word.strip()) #add each word to the options list 
            optionsList.append(options) #add list with options to the optionsList

    return optionsList

#Helper function to display 3 options on the screen 
def display_options(option1, option2, option3):
    clear_screen()
    lcd.putstr("1:" + option1 + " 2:" + option2)
    lcd.move_to(1,0)
    lcd.putstr("3:" + option3) #longest word must be the third to fit on screen 

def make_decision(temp, decisions):
    """Decision logic with MOSFET control, influenced by temperature and three random user decisions."""
    decision = "Maybe"  # Default
    
    # Extract the three user decisions (which can be random words)
    decision1, decision2, decision3 = decisions
    
    # Example logic based on the temperature and the random decisions
    if temp < 22.0:
        # If the first decision is longer than 5 characters, assign "Yes"
        if len(decision1) > 5:
            decision = "Yes"
            greenLED.on()
        elif len(decision2) > 5:
            decision = "Maybe"
            blueLED.on()
        else:
            decision = "No"
            redLED.on()
    
    elif 22.0 <= temp <= 26.0:
        # If the second decision starts with a vowel, assign "Yes"
        if decision2[0].lower() in 'aeiou':  # Check if first letter is a vowel
            decision = "Yes"
            greenLED.on()
        elif len(decision3) > 4:
            decision = "Maybe"
            blueLED.on()
        else:
            decision = "No"
            redLED.on()
    
    else:
        # If the third decision contains the letter 'a', assign "Yes"
        if 'a' in decision3.lower():
            decision = "Yes"
            greenLED.on()
        elif len(decision1) > 3:
            decision = "Maybe"
            blueLED.on()
        else:
            decision = "No"
            redLED.on()

    # Control MOSFET based on final decision (Yes/No logic)
    greenLED.value(1 if decision == "Yes" else 0)
    
    return decision

def restart_program():
    """Reset after showing results"""
    time.sleep(5)  # Show decision for 5 seconds
    turnLEDOff()  # Turn off MOSFET
    return
    machine.reset()  # Soft reboot


#helper function which handles a user interaction and returns the users temperature and then their three answers 
def userInteraction(optionsList):
    clear_screen()
    lcd.putstr("Measure temp")
    time.sleep(5)
    
    temps = [sensor.object_temp for _ in range(3)]
    time.sleep(0.1) #small delay added in between readings
    user_temp = sum(temps) / len(temps)
    
    clear_screen()
    lcd.putstr(f"Temp: {user_temp:.1f}C")
    time.sleep(3)
    
    #loop used to ask the user 3 questions 
    user_answers = []
    i = 0 
    for i in range(3):
        user_choice = askQuestion(optionsList)
        user_answers.append(user_choice)
    
    return user_answers, user_temp
    

#helper function to ask the user a question and then return their answer 
def askQuestion(optionsList):
    # Show options
    clear_screen()
    lcd.putstr("Pick what you")
    lcd.move_to(1, 0)
    lcd.putstr("resonate with")
    time.sleep(3)

    option1, option2, option3 = generateOptions(optionsList)
    display_options(option1, option2, option3)
    user_choice = wait_for_button()
    if user_choice == 1:
        return option1
    elif user_choice == 2:
        return option2
    else:
        return option3

#helper function to display the decision on the screen 
def display_decision(decision):
    # Show result
    clear_screen()
    lcd.putstr("Decision:")
    lcd.move_to(1, 0)
    lcd.putstr(decision)

#Main program should open file and initialize the user loop, User loop should run over and over 
def main(): 

    optionsList = read_options_from_file("selections")
    runUserLoop = True

    while(runUserLoop):
        user_answers, user_temp = userInteraction(optionsList)
        decision = make_decision(user_temp, user_answers)
        display_decision(decision)
        restart_program()
        #TODO: Add a force restart function so we exit the loop if necessarry 

if __name__ == "__main__":
    main()
