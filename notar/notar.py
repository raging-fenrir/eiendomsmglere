import requests
import bs4
import lxml
import lxml.html
import time

class Scrape:

    def __init__(self, rootUrl, startPageUrl):
        self.filename = str(time.time())

        self.nextPageUrls = [rootUrl+startPageUrl]
        self.rootUrl = rootUrl
        page = 0
        while True:
            try:
                soup = self.getSoup(self.nextPageUrls[page])
                nextPage = soup.select('a.next')[0]['href']
                print(nextPage)
                page += 1
            except:
                break
            self.nextPageUrls.append(nextPage)

    def __call__(self):

        for i,page in enumerate(self.nextPageUrls):
            prospectUrls = self.findProspectUrls(page)
            print("Starting on page {}".format(i))
            for j,prospectUrl in enumerate(prospectUrls):
                print("Prospect #{}".format(j))
                try:
                    self.prospectScrapeLxml(prospectUrl)
                except:
                    continue
                time.sleep(60)
            print("Done with page {}".format(i))

    def writeInfo(self,outDict):

        outFile = open(self.filename,'a')

        #for outDict in outListDict:
        outFile.write(str(outDict)+'\n')

        outFile.close()

    def prospectScrapeBS4(self, url):

        prospectInfo = {'url':url}

        soup = self.getSoup(url)
        outer = soup.select('section.contenttab')

        for content in outer:
            headers = content.select('div.box-content-heading')
            texts = content.select('div.box-content-text')
            for headers,text in zip(headers,texts):
                prospectInfo[headers.text.strip()] = text.text.strip()

        keyInfo = soup.select('section.avtal_info')
        for keys in keyInfo:
            try:
                print(keys)
                print('-'*80)
            except:
                continue
            # for key in keys:
            #     try:
            #         print(key.text.strip())
            #     except:
            #         continue
                # print(type(key))
                # print('-'*80)

        return prospectInfo

    def prospectScrapeLxml(self,url):

        rootXPath =\
                '//*[@id="ctl00_ContentBody_ComponentLoader3_ctl00___propertyDetail_container"]/section[2]'
        prospectInfo = {'url':url}
        response = requests.get(url)
        prospectPage = lxml.html.fromstring(response.content)

        adress = prospectPage.xpath(rootXPath+'/p[1]/text()')
        adress = adress[0].strip()+', '+adress[1].strip()
        prospectInfo['adress'] = adress
        
        try:
            price = {'prisantydning':prospectPage.xpath(rootXPath+'/p[4]/span')[0].text.strip()}
        except:
            try:
                price = {'prisantydning':prospectPage.xpath(rootXPath+'/p[3]/span')[0].text.strip()}
            except:
                price = {}

        for i in [7,8,9,10]:
            try:
                key = \
                        prospectPage.xpath(rootXPath+'/p[{}]'.format(i))[0].text.strip()[:-1]
                value = \
                        prospectPage.xpath(rootXPath+'/p[{}]/span'.format(i))[0].text.strip()
                price[key] = value
            except:
                continue
        prospectInfo['price'] = price
            

        eiendomstype = prospectPage.xpath(rootXPath+'/section[2]/text()')
        eiendomstypeDict = {}
        for text in eiendomstype:
            temp = text.strip().split(':')
            try:
                eiendomstypeDict[temp[0].strip()] = temp[1].strip()
            except:
                continue

        try:
            prospectInfo['eiendomstype'] = eiendomstypeDict
            matrikkelinfo = prospectPage.xpath(rootXPath+'/section[4]/text()')
            matrikkelDict = {}
            for text in matrikkelinfo:
                temp = text.strip().split(':')
                try:
                    matrikkelDict[temp[0].strip()] = temp[1].strip()
                except:
                    continue
            prospectInfo['matrikkelinfo'] = matrikkelDict
        except:
            pass

        try: 
            fasiliteter = prospectPage.xpath(rootXPath+'/ul/li/text()')
            fascilities = ''
            for fasi in fasiliteter:
                fascilities += fasi+' '
            prospectInfo[fasiliteter] = fascilities
        except:
            pass
        
        self.writeInfo(prospectInfo)
        
    def findProspectUrls(self, url):

        prospectUrls = []
        soup = self.getSoup(url)
        sections = soup.select('section.product')
        for section in sections[0]:
            try:
                prospectUrls.append(self.rootUrl+section.a['href'])
            except:
                continue
        return prospectUrls

    def getSoup(self,url):

        response = requests.get(url)
        soup = bs4.BeautifulSoup(response.text,"lxml")
        return soup




if __name__=='__main__':

    # rootUrl = 'https://www.eiendomsmegler1.no/bolig/kjoepe-bolig/boliger/'
    # pageUrl = '?rows=25&sort=1&page=1&CATEGORY=homes&lat=&lon='
    # houseUrl = 'bolig/?propertyid='
    rootUrl = "http://notar.no"
    startPageUrl = "/Avansert-sok.aspx?pagesize=27&tab=1"

    notar = Scrape(rootUrl,startPageUrl)
    notar()
