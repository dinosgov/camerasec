from multiprocessing.sharedctypes import Value
import cv2
import time 
import datetime
import smtplib
import sys
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from email.message import EmailMessage
import winsound
import speech_recognition as sr
import pyaudio
import pywhatkit
from gtts import gTTS
from playsound import playsound

cap = cv2.VideoCapture(0)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_fullbody.xml")

detection = False
detection_stopped_time = None
timer_started = False
SECONDS_TO_RECORD_AFTER_DETECTION = 5

frame_size = (int(cap.get(3)), int (cap.get(4)))
fourcc = cv2.VideoWriter_fourcc(*"mp4v")

def speech(text):
    print(text)
    language = "el"
    output = gTTS(text=text , lang=language, slow=False)

    output.save("./output.mp3")
    playsound("./output.mp3")


def speech2(text):
    print(text)
    language = "el"
    output = gTTS(text=text , lang=language, slow=False)

    output.save("./output2.mp3")
    playsound("./output2.mp3")

def get_audio():
    recorder = sr.Recognizer()
    with sr.Microphone() as source:
        print("Παρακαλώ Απάντησε")
        audio = recorder.listen(source)

    text = recorder.recognize_google(audio)
    print(f"You said:{text}")
    return text

def email_alert(subject, body, to):
    msg = EmailMessage()
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to

    user = "yourmail@gmail.com"
    password = "generate one"
    
    server = smtplib.SMTP("smtp.gmail.com",587)
    server.starttls()
    server.login(user,password)
    server.send_message(msg)




if __name__ == '__main__':
    speech('Θέλεις ηχητικό συναγερμό; Αν ναι απάντα με γιές αλλιώς με νόου')
    value = get_audio()
    sunagermos = value
    speech2('Θέλεις λάιβ ειδοποίηση στο μέιλ σου; Αν ναι απάντα με γιές αλλιώς με νόου')
    value = get_audio()
    notification = value
    while True:
        _, frame = cap.read()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.2, 3)
        bodies = face_cascade.detectMultiScale(gray, 1.2, 3)
        if len(faces) + len(bodies) > 0:
            if detection:
                timer_started = False
            else:
                detection = True
                current_time = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
                out = cv2.VideoWriter(f"{current_time}.mp4",fourcc, 20, frame_size)
                print("Started Recording!")

                if sunagermos == ("yes"):
                    winsound.PlaySound("alert.wav", winsound.SND_ASYNC | winsound.SND_ALIAS )
                if notification == ("yes"):
                    email_alert("subject", "message", "yourmail@gmail.com")
        elif detection:
            if timer_started:
                if time.time() - detection_stopped_time >= SECONDS_TO_RECORD_AFTER_DETECTION:
                    detection = False
                    timer_started = False
                    out.release()
                    print("Stop Recording!")
            else:
                timer_started = True
                detection_stopped_time = time.time()
                
    
        if detection:
            out.write(frame)
        

        #for(x, y, width, height) in bodies:
            #cv2.rectangle(frame, (x, y), (x + width, y + height), (255, 0, 0), 3)

        cv2.imshow("Camera", frame)


        if cv2.waitKey(1) == ord('q'):
            break

    out.release()
    cap.release()
    cv2.destroyAllWindows()