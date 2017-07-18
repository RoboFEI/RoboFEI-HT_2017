import argparse
import time
import cv2

# import the necessary packages
import imutils

import os
#import tarfile
import time
#import zipfile
from classify import *
import os
import cv2
import numpy as np
import sys

from servo import Servo

import Condensation

SERVO_PAN = 19
SERVO_TILT = 20

SERVO_TILT_VALUE = 705 # Posicao central inicial Tilt
SERVO_PAN_VALUE = 512 # Posicao central inicial Tilt










servo = None
servo = Servo(SERVO_PAN_VALUE, SERVO_TILT_VALUE)


class objectDetect():
    CountLostFrame = 0
    Count = 0
    kernel_perto = np.ones((39, 39), np.uint8)
    kernel_perto2 = np.ones((100, 100), np.uint8)
    kernel_medio = np.ones((22, 22), np.uint8)
    kernel_medio2 = np.ones((80, 80), np.uint8)
    kernel_longe = np.ones((12, 12), np.uint8)
    kernel_longe2 = np.ones((40, 40), np.uint8)
    kernel_muito_longe = np.ones((7, 7), np.uint8)
    kernel_muito_longe2 = np.ones((30, 30), np.uint8)
    mean_file = None
    labels = None
    net = None
    transformer = None
    status =1

    def __init__(self, net, transformer, mean_file, labels):
        self.mean_file = mean_file
        self.labels = labels
        self.net = net
        self.transformer = transformer

    def searchball(self, image, visionMask, visionMorph1, visionMorph2, visionMorph3):

        YUV_frame = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
        white_mask = cv2.inRange(YUV_frame[:,:,0], 200, 255)

        if visionMask:
            cv2.imshow('Frame Mascara', white_mask)

#        start2 = time.time()
        BallFound = False
        frame, x, y, raio, maskM = Morphology(self,image , white_mask,self.kernel_perto, self.kernel_perto2,1)
        if visionMorph1:
            cv2.imshow('Morfologia 1', maskM)
#        print "Search = ", time.time() - start2 
        if (x==0 and y==0 and raio==0):
            frame, x, y, raio, maskM = Morphology(self,image, white_mask,self.kernel_medio ,self.kernel_medio2,2)
            if visionMorph2:
                cv2.imshow('Morfologia 2', maskM)
            if (x==0 and y==0 and raio==0):
                frame, x, y, raio, maskM = Morphology(self,image, white_mask,self.kernel_longe , self.kernel_longe2,3)
                if visionMorph3:
                    cv2.imshow('Morfologia 3', maskM)
                if (x==0 and y==0 and raio==0):
                    frame, x, y, raio, maskM = Morphology(self,image, white_mask,self.kernel_muito_longe, self.kernel_muito_longe2,4)
                    if (x==0 and y==0 and raio==0):
                        self.CountLostFrame +=1
                        print("@@@@@@@@@@@@@@@@@@@",self.CountLostFrame)
                        if self.CountLostFrame==10:
                            BallFound = False
                            self.CountLostFrame = 0
                            print("----------------------------------------------------------------------")
                            print("----------------------------------------------------------------------")
                            print("----------------------------------------------------------------------")
                            print("--------------------------------------------------------Ball not found")
                            print("----------------------------------------------------------------------")
                            print("----------------------------------------------------------------------")
                            print("----------------------------------------------------------------------")
                            self.status = SearchLostBall(self)

        if (x!=0 and y!=0 and raio!=0):
            BallFound = True
        return frame, x, y, raio, BallFound, self.status

#Varredura
def SearchLostBall(self):

    if self.Count == 0:
        servo.writeWord(SERVO_PAN,30 , SERVO_PAN_VALUE - 350) #olha para a esquerda
        time.sleep(1)
        self.Count +=1
        return 0
    if self.Count == 1:
        servo.writeWord(SERVO_PAN,30, SERVO_PAN_VALUE)#olha para o centro
        time.sleep(1)
        self.Count +=1
        return 1
    if self.Count == 2:
        servo.writeWord(SERVO_PAN,30, SERVO_PAN_VALUE + 350)#olha para a direita 850- 440
        time.sleep(1)
        self.Count = 0
        return 2




def Morphology(self, frame, white_mask, kernel, kernel2, k):

    start3 = time.time()
    contador = 0

#    cv2.imshow('mask',white_mask)
    mask = cv2.morphologyEx(white_mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel2,1)
# Se a morfologia de perto k =1, recorta a parte de cima
    if k ==1:
        mask[0:200,:]=0
# Se a morfologia medio k =2, recorta a parte de baixo
    if k ==2:
        mask[650:,:]=0
# Se a morfologia de longe k =3, recorta a parte de baixo
    if k ==3:
        mask[450:,:]=0
# Se a morfologia de muito longe k = 4, recorta a parte de baixo
    if k ==4:
        mask[400:,:]=0


    ret,th1 = cv2.threshold(mask,25,255,cv2.THRESH_BINARY)

    _,contours,_ = cv2.findContours(th1, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        contador = contador + 1
        x,y,w,h = cv2.boundingRect(cnt)
            #Passa para o classificador as imagens recortadas-----------------------
        type_label, results = classify(cv2.cvtColor(frame[y:y+h,x:x+w], cv2.COLOR_BGR2RGB),
                                                           self.net, self.transformer,
                                                           mean_file=self.mean_file, labels=self.labels,
                                                           batch_size=None)
        #-----------------------------------------------------------------------

#            print results, type_label
    #       cv2.imshow('janela',images[0])
        if type_label == 'Ball':

            return frame, x+w/2, y+h/2, (w+h)/4, mask
        #=================================================================================================
#    print "CONTOURS = ", time.time() - start 
    return frame, 0, 0, 0, mask





