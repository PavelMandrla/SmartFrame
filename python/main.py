#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
from os.path import join
import logging
import time
import waveshare_epd.epd5in65f as epd5in65f
from waveshare_epd.epd5in65f import EPD_WIDTH, EPD_HEIGHT, display_busy
from threading import Thread

import time
import subprocess
from PIL import Image,ImageDraw

import RPi.GPIO as GPIO
import time

PIN_LEFT= 21
PIN_RIGHT = 20
PIN_MID = 16
PIN_TURN_SWITCH = 14

C_MOUNT_DIR = '/mnt/usb/'
C_SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__) /)
C_DITHER_PATH = join(C_SCRIPT_DIR, 'dither')
C_PIC_PATH = join(C_SCRIPT_DIR, 'image.bmp')


logging.basicConfig(level=logging.DEBUG)
current_image = ''

def is_in_portrait_mode():
    # val = GPIO.input(PIN_TURN_SWITCH)
    # return val != 0
    return False

def get_img_list():
    return [f for f in [join(C_MOUNT_DIR, p) for p in os.listdir(C_MOUNT_DIR)] if os.path.isfile(f)]

def get_prev_img_path(curr_path):
    img_list = get_img_list()
    try:
        if len(img_list) == 0:
            return ''
        
        index = img_list.index(curr_path)
        return img_list[index - 1]
    except ValueError as e:
        return img_list[0]
    
def get_next_img_path(curr_path):
    img_list = get_img_list()
    try:
        if len(img_list) == 0:
            return ''
        index = img_list.index(curr_path)

        if index + 1  >= len(img_list):
            return img_list[0]
        
        return img_list[index + 1]
    except ValueError as e:
        return img_list[0]
    
def display_image(path):

    if is_in_portrait_mode():
        W = EPD_HEIGHT
        H = EPD_WIDTH
    else:
        W = EPD_WIDTH
        H = EPD_HEIGHT

    try:
        logging.info('dithering')
        dithering_thread = Thread(target=lambda path: subprocess.run([C_DITHER_PATH, path, C_PIC_PATH, str(W), str(H)]), args=[path])
        dithering_thread.start()

        epd = epd5in65f.EPD()
        logging.info("init and Clear")
        epd.init()
        epd.Clear()

        dithering_thread.join()

        img = Image.new('RGB', (H, W), 0xffffff)
        img = Image.open(C_PIC_PATH)

        if is_in_portrait_mode():
            img = img.rotate(90, expand=True)

        logging.info("Display bpm image")

        epd.busy_pin
        epd.display(epd.getbuffer(img))
        epd.sleep()
        epd.Dev_exit()

    except IOError as e:
        logging.info(e)

    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        epd5in65f.epdconfig.module_exit()
        exit()

def press_left(channel):
    global current_image
    logging.info("left button pressed")
    current_image = get_prev_img_path(current_image)
    logging.info(current_image)
    display_image(current_image)

def press_right(channel):
    global current_image
    logging.info("right button pressed")
    current_image = get_next_img_path(current_image)
    logging.info(current_image)
    display_image(current_image)

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_LEFT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_RIGHT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_MID, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_TURN_SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.add_event_detect(PIN_LEFT, GPIO.FALLING, callback=press_left, bouncetime=50)
GPIO.add_event_detect(PIN_RIGHT, GPIO.FALLING, callback=press_right, bouncetime=50)

GPIO.wait_for_edge(PIN_MID, GPIO.FALLING)
logging.info("shutting down")

GPIO.cleanup()