from time import sleep, time
import threading
import os
from datetime import datetime
import RPi.GPIO as GPIO
import screen
import chars
import routine

ENVIRONMENT_NAME = "WATCH_ROUTINE_DATA"
UPDATE_TRIGGER = "/var/www/UPDATE_DATA"

D = 11
C = 13
B = 15
A = 19
G = 21
DI = 23
CLK = 33
LAT = 32

PIR = 7

clock_view = True

def place_dashes(view, top):
    #show placeholders if the requested weather data is not available
    view = chars.place_character(view, "-", chars.TYPE_SMALL, {"top": top, "left": 9})
    view = chars.place_character(view, "-", chars.TYPE_SMALL, {"top": top, "left": 13})
    return view

def weather_digits(view, text, top):
    digits = abs(int(text))

    #limiting the number of characters shown
    if digits < 10:
        digits = "0" + str(digits)
    elif digits > 99:
        digits = "99"
    else:
        digits = str(digits)

    #show numbers
    view = chars.place_character(view, int(digits[0]), chars.TYPE_SMALL, {"top": top, "left": 9})
    view = chars.place_character(view, int(digits[1]), chars.TYPE_SMALL, {"top": top, "left": 13})
    return view


def render_view(env_data):
    #screen off
    view = [1] * (screen.LINES * screen.LINES)

    #if there is no available data turn the screen off
    if env_data.find(";") == -1 or len(env_data.split(';')) != 3:
        return view

    #parsing the data
    data = env_data.split(';')

    #first view, the clock
    if clock_view:
        data = data[0]        
        if data.find("=") == -1:
            data = time()
        else:
            data = data.split('=')
            data = time() - int(float(data[0])) + int(float(data[1]))
        data = datetime.fromtimestamp(data).strftime("%H%M")

        for i in range(0, 4):
            view = chars.place_character(view, int(data[i]), chars.TYPE_BIG, {"top": 9 * int(i / 2), "left": 8 * (i % 2)})
    #second view, the temperatures 
    else:
        weather = data[1]
        temperature = data[2]

        #interior temperature, given by the sensor
        view = chars.place_character(view, "i", chars.TYPE_SMALL, {"top": 1, "left": 1})
        #if cannot get sensor data, show placeholder
        if temperature != "":
            if int(temperature) < 0:
                view = chars.place_character(view, "-", chars.TYPE_SMALL, {"top": 2, "left": 5})
            view = weather_digits(view, temperature, 2)
        else:
            view = place_dashes(view, 2)

        #exterior temperature, given by the internet
        view = chars.place_character(view, "o", chars.TYPE_SMALL, {"top": 9, "left": 1})
        if weather != "":
            if int(weather) < 0:
                view = chars.place_character(view, "-", chars.TYPE_SMALL, {"top": 10, "left": 5})
            view = weather_digits(view, weather, 10)
        else:
            view = place_dashes(view, 9)

    return view

def routine_thread():
    #creating new thread for routine checks, to check if the time or the temperatures changed meanwhile
    thread = threading.Thread(target=routine.main, args=())
    thread.start()

def main():
    global clock_view

    #led matrix class init
    led = screen.LEDMatrix(D, C, B, A, G, DI, CLK, LAT)

    #init the pir sensor pins
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(PIR, GPIO.IN)

    #init data get from the routine process and the variable which contains the message
    env_data = ""
    screen_data = [1] * (screen.LINES * screen.LINES)

    #taking the data from the routine process, blocking execution only on initialization
    if ENVIRONMENT_NAME in os.environ:
        env_data = os.environ[ENVIRONMENT_NAME]

    #initial rendering of the screen
    screen_data = render_view(env_data)

    #time variables init
    last_env_check = time() #checking environment variable with contains routine data
    last_routine = time() #checking time since last routine check
    last_view_change = time() #alternating the two views, clock and temperatures
    last_motion = time() #time passed since last motion detection
    last_motion_check = time() #time since last check of pir sensor

    active_screen = True #variable which sets the screen on if it detects motion and off if not
    screen_off_view = [1] * (screen.LINES * screen.LINES)

    try:
        while True:
            active_screen = True
            current_time = time()

            if current_time - last_motion_check > 1: #checking the pir sensor every second
                last_motion_check = current_time
                if GPIO.input(PIR) == True:
                    last_motion = current_time

            if current_time - last_motion > 10: # 10 seconds - max time to keep the screen on even if no motion is detected
                active_screen = False #turning the screen off if no motion is detected for more than 10 seconds

            if current_time - last_env_check > 2.5: # 2.5 seconds - checking the environment variable for changes
                last_env_check = current_time
                if env_data != os.environ[ENVIRONMENT_NAME]: # if something changed, change the displayed info
                    env_data = os.environ[ENVIRONMENT_NAME]
                    screen_data = render_view(env_data)

                if os.path.exists(UPDATE_TRIGGER): #if the settings changed from the web server, refresh the info
                    os.remove(UPDATE_TRIGGER)
                    last_routine = current_time
                    routine_thread()

            if active_screen and current_time - last_routine > 300: # 5 minutes - routine checkings - resync time and weather with the APIs
                last_routine = current_time
                routine_thread()

            if active_screen and current_time - last_view_change > 6: # 6 seconds - alternating the views
                last_view_change = current_time
                clock_view = not clock_view # changing the view
                screen_data = render_view(env_data) # refresh the screen

            if active_screen:
                led.Draw(screen_data) # if it's on, draw the data
            else:
                led.Draw(screen_off_view) # ... else, draw an empty screen

            sleep(0.001)

    except KeyboardInterrupt:
        GPIO.cleanup()
        exit(0)

main()
