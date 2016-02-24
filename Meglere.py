#-*- coding: utf-8 -*-
#!../bin/python
from pyvirtualdisplay import Display
from selenium import webdriver
import time
import os
from eiendomsmegler1.eiendomsmegler1 import eiendomsmegler1
from Notar.Notar import Notar


class Meglere:

    def __init__(self):

        self.display    = Display(visible=0, size=(800,600))
        self.display.start()

        self.firefox    = webdriver.Firefox()
        self.path       = os.getcwd()
    
    def __call__(self, megler):
        
        megler(self.firefox)
        

    def terminate(self):

        self.firefox.quit()
        self.display.stop()


if __name__=='__main__':

    meglere             = Meglere()
    NotarInst           = Notar(meglere.path)
    eiendomsmegler1Ins  = eiendomsmegler1(meglere.path)

    print("Notar scrape starting...")
    meglere(NotarInst)
    print("eiendomsmegler1 scrape starting...")
    meglere(eiendomsmegler1Inst)

    meglere.terminate()

