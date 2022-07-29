import cv2
import requests, socket

DDNS = "hal9000-server.ddns.net"



cap = cv2.VideoCapture('http://{}:8081'.format(DDNS))

while(True):
    ret, frame = cap.read()
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break