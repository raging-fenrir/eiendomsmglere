# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

class Notar:

    def __init__(self, path):
        self.filename   = path+'/Notar/data/'+str(time.time())
        self.rootUrl    = 'http://notar.no'
        self.startUrl   = 'http://notar.no/Avansert-sok.aspx?pagesize=27&tab=1'
        self.prospectCounter = 0

    def __call__(self,firefox):

        self.firefox = firefox 
        self.firefox.get(self.startUrl)

        currentUrl = self.startUrl
        current = 0
        total = 1

        while current < total:
            time.sleep(5)
            current, total = self.getNumberOfPages()    
            try:
                nextPage = self.nextPage() 
            except:
                print("Last page")
                pass

            print("Page {} / {}".format(current,total))

            prospectUrls = self.getProspectUrls()

            self.prospectScrape(prospectUrls)
            self.firefox.get(nextPage)


    def nextPage(self):

        nextButton = self.firefox.find_element(By.LINK_TEXT,'Neste')
        
        return nextButton.get_attribute('href')

    def prospectScrape(self, urls):
        
        for url in urls:

            prospectDictionary = {}
            self.prospectCounter += 1

            prospectDictionary['url'] = url
            print("Prospect #{}".format(self.prospectCounter))
            self.firefox.get(url)

            time.sleep(2)

            try:
                prospectAvtal_Info = self.firefox.find_elements(By.CLASS_NAME,'avtal_info')
                for info in prospectAvtal_Info:
                    for element in info.text.split('\n'):
                        element = element.split(':')
                        if element[0] == '':
                            continue
                        else:
                            prospectDictionary[element[0]] = element[1]

            except Exception as e:
                print("prospectAvtal_info: \n",e)
                pass

            try:
                prospectFacilities = self.firefox.find_elements(By.CLASS_NAME,'lstfacilities')
                prospectDictionary['Facilities'] = prospectFacilities[0].text.split()

            except Exception as e:
                print("prospectFacilities: \n",e)
                pass

            try:
                priceEstimate = self.firefox.find_element(By.CLASS_NAME,'bigPris').text
            except Exception as e:
                print("priceEstimate: \n",e)
                pass

            try:
                alll = self.firefox.find_elements(By.CLASS_NAME,'right')
                check = False
                adress = False
                prospectDictionary['Adress'] = []

                for al in alll:
                    al = al.text.split('\n')
                    for a in al:
                        if "INFORMASJON" in a:
                            adress = True
                        elif "PRIS" in a:
                            adress = False
                            check = True
                        elif "FINANSIERING" in a:
                            check = False
                            break
                        if adress:
                            a = a.split()
                            if len(a)<2:
                                pass
                            else:
                                key = 'Adress'
                                value = " ".join(a)
                                prospectDictionary[key].append(value)

                        if check:
                            a = a.split()
                            if len(a) < 3 or a[0] == "kr":
                                pass
                            else:
                                key = a[0].replace(":","")
                                value = "".join(a[1::])
                                prospectDictionary[key] = value
        
            except Exception as e:
                print("alll: \n",e)
                pass

            self.writeInfo(prospectDictionary)

    def getProspectUrls(self):

        urlElements =\
                self.firefox.find_elements(By.XPATH,\
                "//*[contains(@id,'ctl00_ContentLeft_ComponentLoader2_ctl01___rptProperty_')]")
        urls = [] 
        urlCounter = 0
        for url in urlElements:
            url = url.get_attribute("href")
            if "javascript" in url:
                continue
            elif urlCounter > 0:
                if urls[urlCounter -1] == url:
                    continue
            urls.append(url)
            urlCounter += 1

        return urls

    def getNumberOfPages(self):
        
        pageNumberText = self.firefox.find_element(By.CLASS_NAME,'textPage').text.split()
        current, total = int(pageNumberText[1]),int(pageNumberText[3])
        return current, total

    def writeInfo(self,outDict):

        outFile = open(self.filename,'a')

        outFile.write(str(outDict)+'\n')

        outFile.close()

if __name__=='__main__':

    notar = Notar()
    notar()
