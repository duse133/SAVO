import random
import time
import json
from huskylib import HuskyLensLibrary
import RPi.GPIO as GPIO
from datetime import datetime
import os
import threading

hl = HuskyLensLibrary("SERIAL", "/dev/ttyUSB0", 3000000)

algorthimsByteID = {
    "ALGORITHM_OBJECT_TRACKING": "0100",
    "ALGORITHM_FACE_RECOGNITION": "0000",
    "ALGORITHM_OBJECT_RECOGNITION": "0200",
    "ALGORITHM_LINE_TRACKING": "0300",
    "ALGORITHM_COLOR_RECOGNITION": "0400",
    "ALGORITHM_TAG_RECOGNITION": "0500",
    "ALGORITHM_OBJECT_CLASSIFICATION": "0600",
    "ALGORITHM_QR_CODE_RECOGNTITION": "0700",
    "ALGORITHM_BARCODE_RECOGNTITION": "0800",
}

commandList = ['knock()', 
               'setCustomName() #Random String & Cords', 
               'customText() #Random String & Cords', 
               'clearText()', 
               'requestAll()', 
               'saveModelToSDCard(1)', 
               'loadModelFromSDCard(1)', 
               'savePictureToSDCard()', 
               'count()',
               'learnedObjCount()',
               'saveScreenshotToSDCard()', 
               'blocks()', 
               'arrows()', 
               'learned()', 
               'learnedBlocks()', 
               'learnedArrows()', 
               'getObjectByID(1)', 
               'getBlocksByID(1)', 
               'getArrowsByID(1)', 
               'algorthim() #Random Choice', 
               'learn(1)', 
               'forget()', 
               'frameNumber()',
               ""
            ]

servo_pin = 18

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(servo_pin, GPIO.OUT)

pwm = GPIO.PWM(servo_pin,50)
pwm.start(0)

buzzer = 16
GPIO.setmode(GPIO.BCM)
GPIO.setup(buzzer, GPIO.OUT)
GPIO.setwarnings(False)




def get_timestamp():
    return datetime.now().strftime("%T%m%d_%H%M%S")

def get_password(prompt):
    try:
        return input(prompt)
    except NameError:
        raw_input(prompt)
        
picture_num = 1
count = 0
password = "654321"
def compare_passwords():
    password1 = get_password("Enter password: ") #사용자 입력 
    global count, picture_num, password
    
    p2_length = len(password)		#진짜 비밀번호 개수 

    imaginary_num = password1[len(password1)-p2_length:]		#허수 기능. 사용자가 마지막에 입력한 수로 
    
    if imaginary_num == password:
        print("Password match!")
        count = 0
        return True
    else:
        print("Password do not match. Please try again.")
        count += 1
        if count == 4 :
            #부저 5초 + 로그(사진, 해당시간) 남기기
            hl.savePictureToSDCard()
            print("사진 번호 " + str(picture_num)+ "저장")
            with open('./Log.txt', 'a') as file:
                file.write("사진 번호 : " +str(picture_num)+ " 찰영 시간 :"+str(get_timestamp())+ "\n")
                picture_num += 1
            Sound_Fail()
            print("비밀번호 많이 틀림")
            count =0
            
        return False
    
ex = 1

def printObjectNicely(obj):
    count=1
    if(type(obj)==list):
        for i in obj:
            print("\t "+ ("BLOCK_" if i.type=="BLOCK" else "ARROW_")+str(count)+" : "+ json.dumps(i.__dict__))
            count+=1
    else:
        print("\t "+ ("BLOCK_" if obj.type=="BLOCK" else "ARROW_")+str(count)+" : "+ json.dumps(obj.__dict__))
        

def angle_to_duty_cycle(angle):
    return angle / 18 + 2.5

TRIGER = 23
ECHO = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIGER,GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
def waves() :
    startTime = time.time()
    global flag_exit
    try:
        while True:
            if flag_exit : 
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
                        Close()
                else:
                    detectTime = time.time()
                  
    except:
        GPIO.cleanup()

t1 = threading.Thread(target=waves)
flag_exit = False

def Open():
    #try:
    global flag_exit
    flag_exit = True
    global Door
    Door = True
    pwm.ChangeDutyCycle(angle_to_duty_cycle(170))
    

    #except KeyboardInterrupt:
    #pwm.stop()
    #GPIO.cleanup()
   
def Close():
    global Door
    Door = False
    global flag_exit
    flag_exit = False
    pwm.ChangeDutyCycle(angle_to_duty_cycle(10))


def Sound_Success():
    pwm1 = GPIO.PWM(buzzer, 1)
    pwm1.start(50.0)
    
    pwm1.ChangeFrequency(262)
    time.sleep(0.3)
    pwm1.ChangeFrequency(294)
    time.sleep(0.3)
    pwm1.ChangeFrequency(330)
    time.sleep(0.3)
        
    pwm1.ChangeDutyCycle(0.0)
        
    pwm1.stop()
  #  GPIO.cleanup()

def Sound_Fail():				#한번이랑 여러번잉랑 소리 다르게 
    pwm1 = GPIO.PWM(buzzer, 262)
    pwm1.start(50.0)
    time.sleep(1)

    pwm1.stop()
    #GPIO.cleanup()

def Sound_init():
    pwm1 = GPIO.PWM(buzzer, 1)
    pwm1.start(50.0)
    
    pwm1.ChangeFrequency(262)
    time.sleep(0.3)
    pwm1.ChangeFrequency(294)
    time.sleep(0.3)
    
    
button_pin = 13

GPIO.setwarnings(False)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

Door = False
button_pressed_time = 0
is_button_pressed = False
def button_callback(channel):			#버튼 눌렀을대 초기화 or 문 강제 열기
    global Door, button_pressed_time, is_button_pressed

    
    print("Button pushed")
    if GPIO.input(button_pin) == GPIO.HIGH:
          button_pressed_time = time.time()
          print("누름")
          is_button_pressed = True
    else :
        print("버튼 때기")
        if is_button_pressed:
            press_duration = time.time() - button_pressed_time
            print(press_duration)
            if press_duration >= 5 :
                print("5초 넘음")
                Sound_init()
                init_password()
                #비밀번호 초기화
            else :
                if Door == False :
                    Door = True
                    Open()
                    time.sleep(1)
                else :
                    Door = False
                    print("문 닫힘")
                    Close()
                    time.sleep(1)
            is_button_pressed = False
            
button2_pin = 26
GPIO.setwarnings(False)
GPIO.setup(button2_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

button2_pressed_time = 0
is_button2_pressed = False
def face(self) :
    hl.learn(1)
    print("얼굴 등록")
    
    global button2_pressed_time, is_button2_pressed

    
    print("Button pushed")
    if GPIO.input(button2_pin) == GPIO.LOW:
          button2_pressed_time = time.time()
          print("누름")
          is_button2_pressed = True
    else :
        print("버튼 때기")
        
        if is_button2_pressed:
            press_duration = time.time() - button2_pressed_time
            print(press_duration)
            if press_duration >= 5 :
                print("5초 넘음")
                Sound_init()
                #얼굴 초기화
                hl.forget()
            is_button2_pressed = False

GPIO.add_event_detect(button2_pin, GPIO.BOTH, callback=face)
    

def init_password():
    global password
    hl.forget()
    password = input("비밀번호 값 입력")
    
    
    
GPIO.add_event_detect(button_pin, GPIO.BOTH, callback=button_callback)




def check() :
    ex = 1
        
    while(ex == 1):
        if compare_passwords():
            #부저 3초동안 알림음 발생
            time.sleep(2)
            #printObjectNicely(hl.requestAll()) #얼굴인식
            if(type(hl.requestAll())==list):
                
                i = None
                
                #print(dir(hl.requestAll()))
                for i in hl.requestAll() :
                    json.dumps(i.__dict__)
                
                if i is None:
                    print("얼굴 인식 실패")
                    Sound_Fail()
                    continue
                
                if 'learned' in i.__dict__:
                    learned_value = i.__dict__['learned']
                    #print(learned_value)
                    
                if learned_value == False:
                    print("얼굴 인식 실패")
                    Sound_Fail()
                    continue
                elif learned_value == True:
                    print("얼굴 인증 완료")
                    print("비밀번호 통과")
                    Sound_Success()
                    Open()
                    break

            else:
                print("객체 형식")

            ex = 1
            continue


if __name__ == "__main__":
    t1.start()
    while True :
        check()