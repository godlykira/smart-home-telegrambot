import RPi.GPIO as GPIO
import spidev  # import SPI library
from mfrc522 import SimpleMFRC522

import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


def get_moisture():
    """
    Get the moisture level by reading the input from GPIO 4.
    If GPIO 4 reads high, it indicates moisture presence, otherwise no moisture is detected.
    Returns the corresponding moisture status.
    """
    GPIO.setup(4, GPIO.IN)  # set GPIO 4 as input
    if GPIO.input(4):  # if read a high at GPIO 4, moisture present
        return "detected HIGH i.e. moisture"
    else:  # otherwise (i.e. read a low) at GPIO 4, no moisture
        return "detected LOW i.e. no moisture"


def current(queue):
    """
    A function to read the ADC values from SPI and return the values of LDR and potentiometer.
    """
    spi = spidev.SpiDev()  # create SPI object
    spi.open(0, 0)  # open SPI port 0, device (CS) 0

    def readadc(adcnum):
        # read SPI data from the MCP3008, 8 channels in total
        if adcnum > 7 or adcnum < 0:
            return -1
        spi.max_speed_hz = 1350000
        r = spi.xfer2([1, 8 + adcnum << 4, 0])
        # construct list of 3 items, before sending to ADC:
        # 1(start), (single-ended+channel#) shifted left 4 bits, 0(stop)
        # see MCP3008 datasheet for details
        data = ((r[1] & 3) << 8) + r[2]
        # ADD first byte with 3 or 0b00000011 - masking operation
        # shift result left by 8 bits
        # OR result with second byte, to get 10-bit ADC result
        return data

    while True:
        LDR_value = readadc(0)  # read ADC channel 0 i.e. LDR
        # print("LDR = ", LDR_value) #print result
        pot_value = readadc(1)  # read ADC channel 1 i.e. potentiometer
        # print("pot = ", pot_value) #print result

        result = {"LDR": LDR_value, "pot": pot_value}
        queue.put(result)

        time.sleep(1)


async def ultrasonic():
    """
    A function to perform ultrasonic measurements and return a condition based on the distance measured.
    """
    condition = True
    GPIO.setup(25, GPIO.OUT)  # GPIO25 as Trig
    GPIO.setup(27, GPIO.IN)  # GPIO27 as Echo
    GPIO.output(25, 1)
    time.sleep(0.00001)
    GPIO.output(25, 0)
    # measure pulse width (i.e. time of flight) at Echo
    StartTime = time.time()
    StopTime = time.time()
    while GPIO.input(27) == 0:
        StartTime = time.time()  # capture start of high pulse
    while GPIO.input(27) == 1:
        StopTime = time.time()  # capture end of high pulse
    ElapsedTime = StopTime - StartTime
    # compute distance in cm, from time of flight
    Distance = (ElapsedTime * 34300) / 2
    # distance=time*speed of ultrasound,
    # /2 because to & fro
    print(Distance)
    if Distance < 120:
        condition = True
        print(condition)
        return condition
    else:
        condition = False
        print(condition)
        print("2")
        return condition


async def register_card():
    reader = SimpleMFRC522()
    id = reader.read_id()
    print("id", id)
    return id


def light(state):
    """
    Function to control the state of a light based on the input state parameter.

    Parameters:
    state (bool): The state of the light, True for on and False for off.
    """
    if state is True:
        GPIO.setup(24, GPIO.OUT)  # set GPIO 24 as output
        GPIO.output(24, 1)  # output logic high/'1'
    else:
        GPIO.setup(24, GPIO.OUT)  # set GPIO 24 as output
        GPIO.output(24, 0)  # output logic low/'0'
