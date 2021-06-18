import os
import json
import requests
import urllib
import time
import Adafruit_DHT
import RPi.GPIO as GPIO

#CONFIG_PATH = os.path.dirname(os.path.realpath(__file__)) + "/settings.json"
CONFIG_PATH = "/var/www/settings.json"
DHT11BCM = 18 #DHT11 DATA GPIO TYPE PIN
DHT11BOARD = 12 #DHT11 DATA BOARD TYPE PIN

#internet request function
def request(url):
    try:
        response = requests.get(url, timeout=2)
    except:
        return False

    #logging
    print("Cerere la " + url + " cu raspunsul " + str(response.status_code))

    if response.status_code >= 200 and response.status_code < 300:
        #return the response if the request is successful
        return response.text
    else:
        #returning False if something wrong happened
        return False

def find_weather(location):
    #request to wttr.in to get informations about chosen location
    res = request("http://wttr.in/" + urllib.parse.quote(location, safe='') + "?format=%t")

    if res is False or len(res) > 10:
        #if the request was unsuccessful
        return ""
    else:
        #parsing the number before the special character
        return res.split('°')[0]

def get_temperature():
    #reading temperature data from the DHT11, 5 retries, 0.5 delay between retries
    h, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, DHT11BCM, 5, 0.5)

    #logging
    print("Temperatura citita de la senzor " + str(temperature))

    #returning temperature if the reading was correct
    if temperature is not None:
        return str(int(temperature))
    else:
        return ""

def get_time():
    #reading the time from the ntp server
    res = request("http://worldtimeapi.org/api/ip")
    #storing the system timestamp
    unix = time.time()

    if res is not False:
        #server response - json parsing
        content = json.loads(res)
        
        if "unixtime" in content:
            unix = int(float(content["unixtime"]))

    #sending the system timestamp - ntp server response pair, to get the offset between the two
    return str(int(time.time())) + "=" + str(unix)


def main():
    clock = ""
    weather = ""
    temperature = ""

    #init pins for DHT11
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(DHT11BOARD, GPIO.IN)

    #getting the interior temperature
    temperature = get_temperature()

    #if configuration exists, displaying with the current settings
    if os.path.exists(CONFIG_PATH):
        #reading config
        config = open(CONFIG_PATH, "r", encoding="utf-8")
        config = json.loads(config.read())
        
        #if the weather location is specified
        if "locatie" in config:
            weather = find_weather(config["locatie"])
        else:
            weather = find_weather("")

        #if the internet sync is on or a custom time is specified
        if "sincronizare" not in config or ("sincronizare" in config and config["sincronizare"] == "true"):
            clock = get_time()
        elif "ora" in config and config["ora"].find(";") != -1:
            parts = config["ora"].split(';')
            #sending the system - custom time pair
            clock = parts[0] + "=" + parts[1]
    #if configuration doesn't exist, display with default settings
    else:
        weather = find_weather("")
        clock = get_time()

    #sending data to environment variable for main thread processing
    os.environ["WATCH_ROUTINE_DATA"] = clock + ";" + weather + ";" + temperature

    #logging
    print(os.environ["WATCH_ROUTINE_DATA"])


main()