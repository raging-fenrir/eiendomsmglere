# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyvirtualdisplay import Display
from multiprocessing import Process
import time



class Scrape:

    def __init__(self):
        self.display = Display(visible=0, size=(800,600))
        self.rootUrl = 'https://www.eiendomsmegler1.no'
        self.startUrl = 'https://www.eiendomsmegler1.no/bolig/kjoepe-bolig/'+\
                'boliger/?rows=25&sort=1&page=1&CATEGORY=homes&lat=&lon='
        self.filename = str(time.time())
        self.prospectCounter = 0

    def __call__(self):
        print("Starting virtual display")
        self.display.start()
        print("Starting browser...")
        self.page = webdriver.Firefox()
        print("Connecting to page...")
        self.page.get(self.startUrl)
        print("Connected")
        print("Starting the scrape...")

        current = 0
        total = 1
        
        while current < total:
            self.wait()
            current, total = self.getNumberOfPages()

            print("Page {} /  {}".format(current,total))

            prospectUrls = self.getProspectUrls()
            p = Process(target=self.prospectScrape, args=(prospectUrls,))
            p.start()
            #self.prospectScrape(prospectUrls)
            p.join()
            self.nextPageMain()
            time.sleep(5)

        print("Quitting page")
        self.page.quit()
        print("Quitting display")
        self.display.stop()


    def prospectScrape(self, prospectUrls):

        urls = [url.get_attribute('data-url') for url in prospectUrls] 

        prospectPage = webdriver.Firefox()

        for url in urls:
            self.prospectCounter += 1
                
            print("Prospect #{}".format(self.prospectCounter))

            prospDict = {}
            url = self.rootUrl + url
            prospDict['url'] = url

            prospectPage.get(url)
             
            try:
                WebDriverWait(prospectPage,10).until(\
                        EC.presence_of_all_elements_located((By.CLASS_NAME,'prospect-table')))
            except Exception as e:
                print(e)

            try:
                prospectTable = prospectPage.find_elements(By.TAG_NAME,'td')
                for key,value in zip(prospectTable[:-2:2],prospectTable[1::2]):

                    if value.text == "": 
                        continue
                    else:
                        prospDict[key.text] = value.text
            except Exception as e:
                print(e)

            try:

                prospectIntro = prospectPage.find_element(By.CLASS_NAME,'prospect-intro')
                prospDict['ProspectInfo'] = prospectIntro.text

            except Exception as e:
                print(e)

             
            self.writeInfo(prospDict)
            time.sleep(2) 

        prospectPage.quit()

    def getNumberOfPages(self):
        
        xpath = '//*[@id="aspnetForm"]/main/div[1]/div/div[6]/div/div'
        pages = self.page.find_element_by_xpath(xpath).text.strip().split()
        current, total = int(pages[1]), int(pages[-1])
        return current, total

    def nextPageMain(self):
        
        nextButton = self.page.find_element_by_link_text('Neste')
        nextButton.click() 

    def getProspectUrls(self):
        
        urlElements = self.page.find_elements_by_class_name('images-list')
        return urlElements

    def wait(self):
        try:
            WebDriverWait(self.page,10).until(\
                    EC.presence_of_all_elements_located((By.CLASS_NAME,'images-list')))
        except:
            print("Timeout on wait")
            pass
            

    def writeInfo(self,outDict):

        outFile = open(self.filename,'a')

        #for outDict in outListDict:
        outFile.write(str(outDict)+'\n')

        outFile.close()


if __name__=='__main__':
    
    
    eiendomsmegler1 = Scrape()
    eiendomsmegler1()
