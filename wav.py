import RPi.GPIO as GPIO
import time

TRIGER = 23
ECHO = 24

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIGER, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

startTime = time.time()
pressTime = 0

try:
    while True:
        GPIO.output(TRIGER, GPIO.LOW)
        time.sleep(0.1)
        GPIO.output(TRIGER, GPIO.HIGH)
        time.sleep(0.00002)
        GPIO.output(TRIGER, GPIO.LOW)
        
        while GPIO.input(ECHO) == GPIO.LOW:
            startTime = time.time()
        
        while GPIO.input(ECHO) == GPIO.HIGH:
            endTime = time.time()
        
        period = endTime - startTime
        dist1 = round(period * 1000000/58, 2)
        dist2 = round(period * 17241, 2)
        
        print("Dist1", dist1, "cm", ", Dist2", dist2,"cm")
        if dist1 < 10 and dist2<10:
            print("detect")
            correctTime = time.time() - detectTime
            print(correctTime)
            if(correctTime > 5):
                print("문닫힘")
                break;
        else:
            detectTime = time.time()
            
except:
    GPIO.cleanup()
        