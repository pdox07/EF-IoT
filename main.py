from youtube_dl import YoutubeDL
from playsound import playsound
from quart import Quart, request
from kasa import SmartBulb
from helper import * 
import asyncio
from pytapo import Tapo
import cv2
import pyttsx3
import os
import RPi.GPIO as GPIO
import threading
import time



app = Quart(__name__)
bulb_model = "KL130B"
camera_model = "C100_DF98A3"

dev_1 = GPIO.LOW
dev_2 = GPIO.LOW
dev_3 = GPIO.LOW
flag  = False

channel_1, channel_2, channel_3 = 21, 20, 16

GPIO.setmode(GPIO.BCM)

def update_power():
    global dev_1, dev_2, dev_3, flag
    u_dev_1, u_dev_2, u_dev_3 =  dev_1, dev_2, dev_3

    while True:

        if dev_1 != u_dev_1:
            GPIO.setup(channel_1, GPIO.OUT)
            GPIO.output(channel_1, dev_1)
            u_dev_1 = dev_1

        if dev_2 != u_dev_2:
            GPIO.setup(channel_2, GPIO.OUT)
            GPIO.output(channel_2, dev_2)
            u_dev_2 = dev_2

        if dev_3 != u_dev_3:
            GPIO.setup(channel_3, GPIO.OUT)
            GPIO.output(channel_3, dev_3)
            u_dev_3 = dev_3
        
        if flag:
            break

        time.sleep(1)

    GPIO.cleanup()





@app.route("/",["GET"])
def conn():
    return "Pi is Reachable"


#==============================BULB============================
@app.route("/cstate",methods = ["POST"])
async def state():
    ip = get_device_ip(bulb_model)
    print(ip)
    bulb = SmartBulb(ip)
    await bulb.update()
    return {"status" : status(bulb.is_on)}

    
@app.route("/flipswitch",methods = ["POST"])
async def flip():
    ip = get_device_ip(bulb_model)
    bulb = SmartBulb(ip)
    await bulb.update()
    final_state = ''
    cstate = bulb.is_on
    if cstate:
        await bulb.turn_off()
        final_state = status(not cstate)
    else:
        await bulb.turn_on()
        final_state = status(not cstate)
    
    return {"status" : final_state}


@app.route("/hsinfo",methods = ["POST"])
async def hsinfo():
    ip = get_device_ip(bulb_model)
    bulb = SmartBulb(ip)
    await bulb.update()
    return {"data" : bulb.hw_info}

@app.route("/gsinfo",methods = ["POST"])
async def gsinfo():
    ip = get_device_ip(bulb_model)
    bulb = SmartBulb(ip)
    await bulb.update()
    data = {}
    data["alias"] = bulb.alias
    data["model"] = bulb.model
    data["rssi"] = bulb.rssi
    data["mac"] = bulb.mac
    data["trange"] = bulb.valid_temperature_range
    return {"data" : data}

@app.route("/emeter",methods = ["POST"])
async def ereading():
    ip = get_device_ip(bulb_model)
    bulb = SmartBulb(ip)
    await bulb.update()
    reading = bulb.emeter_realtime
    return {"reading" : reading}


@app.route("/color",methods = ["POST"])
async def setcolor():
    ip = get_device_ip(bulb_model)
    bulb = SmartBulb(ip)
    await bulb.update()

    form = await request.form
    h,s,v = form['h'],form['s'],form['v']

    await bulb.set_hsv(int(h), int(s), int(v))
    await bulb.update()
    return {"ccolor" : bulb.hsv}

@app.route("/bright",methods = ["POST"])
async def setbrightness():
    ip = get_device_ip(bulb_model)
    bulb = SmartBulb(ip)
    await bulb.update()

    form = await request.form
    bright = form['bright']

    await bulb.set_brightness(int(bright))
    await bulb.update()

    return {"cbrightness" : bulb.brightness}

@app.route("/ctemp",methods = ["POST"])
async def setcolortemp():
    ip = get_device_ip(bulb_model)
    bulb = SmartBulb(ip)
    await bulb.update()

    form = await request.form
    temp = form['temp']

    await bulb.set_color_temp(int(temp))
    await bulb.update()

    return {"ctemp" : bulb.color_temp}
#=======================================CAMERA=============================


#=========================GET============================
@app.route("/snap",methods = ["POST"])
def getpic():
    ip = get_device_ip(camera_model)
    user = "IOT_tapo" 
    password = "IITpassword"
    url = "rtsp://"+user+":"+password+"@"+ip+":554/stream2"
    video = cv2.VideoCapture(url) 
    check, frame = video.read()
    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    showPic = cv2.imwrite("filename.jpg",frame)
    video.release()
    cv2.destroyAllWindows()
    print (frame)
    return {"frame" : frame}

@app.route("/basic_info",methods = ["POST"])
def get_basicinfo():
    ip = get_device_ip(camera_model)
    user = "IOT_tapo" 
    password = "IITpassword"
    tapo = Tapo(ip, user, password)
    return tapo.getBasicInfo()

@app.route("/alarm_info",methods = ["POST"])
def get_alarm():
    ip = get_device_ip(camera_model)
    user = "IOT_tapo" 
    password = "IITpassword"
    tapo = Tapo(ip, user, password)
    return tapo.getAlarm()

@app.route("/privacy_info",methods = ["POST"])
def get_privacy():
    ip = get_device_ip(camera_model)
    user = "IOT_tapo" 
    password = "IITpassword"
    tapo = Tapo(ip, user, password)
    return tapo.getPrivacyMode()

@app.route("/motion_info",methods = ["POST"])
def get_motion():
    ip = get_device_ip(camera_model)
    user = "IOT_tapo" 
    password = "IITpassword"
    tapo = Tapo(ip, user, password)
    return tapo.getMotionDetection()

@app.route("/display_info",methods = ["POST"])
def get_display_info():
    ip = get_device_ip(camera_model)
    user = "IOT_tapo" 
    password = "IITpassword"
    tapo = Tapo(ip, user, password)
    return tapo.getOsd()

@app.route("/module_info",methods = ["POST"])
def get_module_spec():
    ip = get_device_ip(camera_model)
    user = "IOT_tapo" 
    password = "IITpassword"
    tapo = Tapo(ip, user, password)
    return tapo.getModuleSpec()

#=========================SET============================

@app.route("/display",methods = ["POST"])
async def set_osd():
    ip = get_device_ip(camera_model)
    user = "IOT_tapo" 
    password = "IITpassword"
    tapo = Tapo(ip, user, password)

    form = await request.form
    label = form['label']
    d_enb = form['dateEnabled']
    l_enb = form['labelEnabled']
    w_enb = form['weekEnabled']

    result = tapo.setOsd(label, dateEnabled=d_enb, labelEnabled=l_enb, weekEnabled=w_enb)
    err_code = result["error_code"]

    if err_code == 0:
        return {"message" : "on screen display set successfully"}
    else:
        return {"message" : "error occured"}


@app.route("/privacy",methods = ["POST"])
async def set_privacy():
    ip = get_device_ip(camera_model)
    user = "IOT_tapo" 
    password = "IITpassword"
    tapo = Tapo(ip, user, password)

    form = await request.form
    flag = form['enable']

    #Camera not working when its True
    result = tapo.setPrivacyMode(enabled=flag)
    err_code = result["error_code"]

    if err_code == 0:
        return {"message" : "privacy set successfully"}
    else:
        return {"message" : "error occured"}

@app.route("/mode",methods = ["POST"])
async def set_mode():
    ip = get_device_ip(camera_model)
    user = "IOT_tapo" 
    password = "IITpassword"
    tapo = Tapo(ip, user, password)

    form = await request.form
    mode = form['mode']

    # when condition is on : Camera = Blackk & White
    result = tapo.setDayNightMode(mode)
    err_code = result["error_code"]

    if err_code == 0:
        return {"message" : "mode set successfully"}
    else:
        return {"message" : "error occured"}

@app.route("/motion_not",methods = ["POST"])
async def set_motion_not():                            ########## NOT WORKING ###############
    ip = get_device_ip(camera_model)
    user = "IOT_tapo" 
    password = "IITpassword"
    tapo = Tapo(ip, user, password)

    form = await request.form
    flag = form['enable']
    try:
        sense = form['sensitivity']
        # Motion detection is off, when enabled=false
        result = tapo.setMotionDetection(enabled=flag, sensitivity=sense)
    except:
        # Motion detection is off, when enabled=false
        result = tapo.setMotionDetection(enabled=flag)
        
    err_code = result["error_code"]

    if err_code == 0:
        return {"message" : "motion set successfully"}
    else:
        return {"message" : "error occured"}

#=========================ASSISTANT==========================

@app.route("/speak",methods = ["POST"])
async def speak():
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    form = await request.form
    sentence = form['sentence']
    voice = form['gender']
    if voice == "male":
        v = voices[0].id
    else:
        v = voices[1].id
     
    engine.setProperty('voice', v)
    engine.say(sentence)
    #engine.save_to_file('Hello World', 'test.mp3')
    engine.runAndWait()
    return {"result" : "Sentence spoken successfully"}



@app.route("/play",methods = ["POST"])
async def play():
    # "https://www.youtube.com/watch?v=m9zhgDsd4P4"
    form = await request.form
    url = form['url']

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    info = YoutubeDL({'format':'worst'}).extract_info(url,download=False)
    fname = info['title']+"-"+info["id"]+".mp3"
    os.system('mpg321 '+fname+' &')
    return {"result" : "Audio played successfully"}

@app.route("/flip_power",methods = ["POST"])
async def switch_device():

    global dev_1, dev_2, dev_3

    form = await request.form
    dev = form['device']
    power = int(form['power'])

    if dev == "dev_1":
        dev_1 = GPIO.HIGH if power else GPIO.LOW
    elif dev == "dev_2":
        dev_2 = GPIO.HIGH if power else GPIO.LOW
    elif dev == "dev_3":
        dev_3 = GPIO.HIGH if power else GPIO.LOW

    return {"Message" : dev+" power updated"}



if __name__ == "__main__":
    try:
        t1 = threading.Thread(target=update_power)
        t1.start()
        app.run(host="127.0.0.1", port=8080, debug=True)
        flag = True
        t1.join()
    except KeyboardInterrupt:
        flag= True
        t1.join()

