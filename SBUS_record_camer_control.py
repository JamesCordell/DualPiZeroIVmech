#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import datetime
import picamera
from collections import Counter

import logging
import logging.handlers

##############################
# Setup logging
##############################
log = logging.getLogger('OSDLog')
log.setLevel(logging.DEBUG)

handler = logging.handlers.SysLogHandler(address = '/dev/log')

log.addHandler(handler)
log.debug('OSD Log Started')

def getTimex():
    return time.time()

def getFileName():  # new
    return datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.h264")

GPIO.setmode(GPIO.BOARD)

import PIL
from PIL import Image, ImageDraw, ImageFont

Image.Image.tostring = Image.Image.tobytes

# Create empty images to store text overlays
textOverlayCanvas = Image.new("RGB", (704, 60))
textOverlayPixels = textOverlayCanvas.load()

# Use Roboto font (must be downloaded first)
font = ImageFont.truetype("/usr/share/fonts/truetype/roboto/Roboto-Regular.ttf", 20) 

img = Image.open('/root/record704x512.png')

#pad = Image.new('RGBA', (
#((img.size[0] + 31) // 32) * 32,
#((img.size[1] + 15) // 16) * 16,
#))
pad = Image.new('RGBA',(704,512))

pad.paste(img,(0,0),img)

import serial
import copy


class Rx:


  def __init__(self):
    self.openSerial()
    self.channels = []
    self.channelsLast = []
    self.newread = 1
    self.rssi = 0
    self.zeros = 0
    self.armed = 0
    self.rec = 0
    self.state = 0
    self.actions = []

    while self.newread == 1:
      if self.ser.inWaiting() > 0:
        self.channelsLast = self.ser.readline().split("\t")
        if len(self.channelsLast) == 16:
          self.newread = 0
          log.debug('initial read')
        else:
          self.newread = 1

  def openSerial(self):
    self.ser = serial.Serial(
    port='/dev/serial0',\
    baudrate=57600,\
    parity=serial.PARITY_NONE,\
    bytesize=serial.EIGHTBITS,\
    timeout=0)
    return

  def closeSerial(self):
    self.ser.close()

  def __del__(self):
    self.ser.close()

  def addAction(self,channelNumber,function,args,above,below,logMessage):
    self.actions.append( dict({ 'channelNumber':channelNumber,'function':function,'args':args,'above':above,'below':below,'logMessage':logMessage}) )
    return

  def getChannels(self):
    #run serial read until we have stable data
    self.openSerial()
    while self.newread == 1:
      if self.ser.inWaiting() > 0:
        self.channels = self.ser.readline().split("\t")
      
        if len(self.channels) == 16: 
          for a in self.actions[:]: 
	    if int( self.channels[ a['channelNumber'] ] ) >= int( a['above'] ) and \
               int( self.channels[ a['channelNumber'] ] ) < int( a['below'] ) and \
             ( int( self.channelsLast[ a['channelNumber'] ] ) <= int( a['above'] ) or \
               int( self.channelsLast[ a['channelNumber'] ] ) > int( a['below'] ) ):
              log.debug(a['logMessage'])
              if callable(a['function']):
                if callable(a['args']) :
                  try:
                    a['function']( a['args']() )
                  except:
                    log.debug('Already done.') 
                else:
                  try:
                    a['function']()
                  except:
                    log.debug('Already done.')
          self.newread = 0 #a successesful read of 16 channels now leave 
          self.channelsLast = copy.deepcopy(self.channels)
        else:
          self.newread = 1

    #log.debug(','.join(map(str,self.channels)))
    self.newread = 1 
    self.closeSerial()
    return
 
#print("connected to: " + ser.portstr)


with picamera.PiCamera() as camera:
  camera.vflip = True #camera is upside down
  camera.hflip = True
  camera.video_stabilization = True
  camera.start_preview()

  recPaused = 1 #don't start recording on startup.
  recPausedLastState = 1
  rx = Rx()
  rx.addAction(15,''                     ,''        ,1655,1655,'Rssi to low.')
  rx.addAction(15,''                     ,''        ,1   ,1654,'Rssi found.')
  rx.addAction(11,camera.start_recording,getFileName,1000,2000,'Recording on.')
  rx.addAction(11,camera.stop_recording,''          ,1   ,1000,'Recording off.')
  #copy channels so we have an initial first run history
	
  bottomOverlayImage = textOverlayCanvas.copy()
  bottomOverlay = camera.add_overlay(bottomOverlayImage.tobytes(), format='rgb', size=(704,60), layer=4, alpha=128, fullscreen=False, window=(0,0,704,60))
  try:
    while True:
  
      	camera.annotate_text = ''
        rx.getChannels()
        time.sleep(.5)	
          #o = camera.add_overlay(pad.tostring(),layer=3,size=pad.size) #, size=(1920,1080))

        #bottomOverlayImage = textOverlayCanvas.copy()
        #bottomText = "Alt: {0}m  Loc: {1:.5f}, {2:.5f}   Home: {3}m    Rec: {4}".format(gpsd.fix.altitude,gpsd.fix.latitude, gpsd.fix.longitude, distanceTraveled, timeActive)
        #bottomText = "Rec:"
        #drawBottomOverlay = ImageDraw.Draw(bottomOverlayImage)
        #drawBottomOverlay.text((50, 20), bottomText, font=font, fill=(255, 255, 255))
        #bottomOverlay.update(bottomOverlayImage.tobytes())

  except KeyboardInterrupt:
    log.debug('Exiting')
    GPIO.cleanup()
    camera.stop_preview()
    if camera.recording :
      camera.stop_recording()
