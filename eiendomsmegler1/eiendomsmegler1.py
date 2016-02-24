# -*- coding: utf-8 -*-
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time



class eiendomsmegler1:

    def __init__(self, path):

        self.filename = path+'/eiendomsmegler1/data/'+str(time.time())
        self.rootUrl = 'https://www.eiendomsmegler1.no'
        self.startUrl = 'https://www.eiendomsmegler1.no/bolig/kjoepe-bolig/'+\
                'boliger/?rows=25&sort=1&page=1&CATEGORY=homes&lat=&lon='
        self.prospectCounter = 0

    def __call__(self, firefox):

        self.firefox = firefox
        self.firefox.get(self.startUrl)

        current = 0
        total = 1
        
        while current < total:
            self.wait()
            current, total = self.getNumberOfPages()
            currentUrl = self.firefox.current_url

            print("Page {} /  {}".format(current,total))

            prospectUrls = self.getProspectUrls()
            self.prospectScrape(prospectUrls)

            
            try:
                self.firefox.get(currentUrl)
                self.wait()
                self.nextPage() 
            except Exception as e:
                print("Could not hit the button")
                print(e)
                pass
            time.sleep(5)

    def nextPage(self):
        
        nextButton = self.firefox.find_element_by_link_text('Neste')
        nextButton.click() 

    def prospectScrape(self, prospectUrls):

        urls = [url.get_attribute('data-url') for url in prospectUrls] 

        for url in urls:
            self.prospectCounter += 1
                
            print("Prospect #{}".format(self.prospectCounter))

            prospDict = {}
            url = self.rootUrl + url
            prospDict['url'] = url

            self.firefox.get(url)
             
            try:
                WebDriverWait(self.firefox,10).until(\
                        EC.presence_of_all_elements_located((By.CLASS_NAME,'prospect-table')))
            except Exception as e:
                print("WebDriverWait")
                print(e)

            try:
                prospectTable = self.firefox.find_elements(By.TAG_NAME,'td')
                for key,value in zip(prospectTable[:-2:2],prospectTable[1::2]):

                    if value.text == "": 
                        continue
                    else:
                        prospDict[key.text] = value.text
            except Exception as e:
                print("prospectTable")
                print(e)

            try:

                prospectIntro = self.firefox.find_element(By.CLASS_NAME,'prospect-intro')
                prospDict['ProspectInfo'] = prospectIntro.text

            except Exception as e:
                print("prospectIntro")
                print(e)

             
            self.writeInfo(prospDict)
            time.sleep(2) 


    def getNumberOfPages(self):
        
        xpath = '//*[@id="aspnetForm"]/main/div[1]/div/div[6]/div/div'
        pages = self.firefox.find_element_by_xpath(xpath).text.strip().split()
        current, total = int(pages[1]), int(pages[-1])

        return current, total


    def getProspectUrls(self):
        
        urlElements = self.firefox.find_elements_by_class_name('images-list')
        return urlElements

    def wait(self):
        try:
            WebDriverWait(self.firefox,10).until(\
                    EC.presence_of_all_elements_located((By.CLASS_NAME,'images-list')))
        except Exception as e:
            print("Timeout on wait")
            print(e)
            pass
            

    def writeInfo(self,outDict):

        outFile = open(self.filename,'a')

        outFile.write(str(outDict)+'\n')

        outFile.close()


if __name__=='__main__':
    
    
    eiendomsmegler1 = Scrape()
    eiendomsmegler1()
