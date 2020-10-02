from altall import *
from fbsingle import *
from instasingle import *
from instaall import *
from goimg import *
from trading_image import *
from twsingle import *
from wpmsg import *


# In[6]:
 #1  ALTNEWS
class Scrape:
    def altnews():
        df=pd.DataFrame(columns=['title','link','date','text','category'])
        count=0
        urls=retrieve_url()
        urls=[url for url_set in urls for url in url_set]
        for url in urls:
            url=str(url).replace('\n','')
            r = requests.get(url) 
            soup = BeautifulSoup(r.content, 'html.parser')
            all_text =soup.find_all('p')
            date=soup.find("span",class_="updated")
            date=date.text
            title=soup.find('h1',class_="entry-title h1")
            title=title.text
            for txt in all_text:
                txt=txt_reterive(txt.text)
                if len(txt)>50:
                    df.loc[count]=[title,url,date,txt,'fake']
                    print("Writing Row {} data ".format(count))
                    count+=1
        return df


 #2 INSTAALL
    def insta_profile(id_name):
        query='https://www.instagram.com/'+id_name+'/'
        browser=webdriver.Chrome('./chromedriver')
        browser.get(query)
        total_urls=[]
        print("Retrieving ..............")
        n_posts=int(browser.find_element_by_class_name('g47SY ').text)
        iteration=0
        while iteration<=n_posts//24+1:
            page=browser.page_source
            soup=BeautifulSoup(page,'lxml')
            tags=soup.find_all('img',class_='FFVAD')
            track=tags[-1]['src']
            if track not in total_urls:
                total_urls.extend(tags)
            try:
                browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
                time.sleep(2)
                iteration+=1
            except:
                exit()
        print("Started downloading .........")
        total_urls=set(total_urls)
        for i,url in enumerate(total_urls):
            image=Image.open(urllib.request.urlopen(url['src']))
            try:
                caption=url['alt']
            except:
                caption='No caption'
            try:
                image.save(id_name+'/'+caption[:20]+str(i)+'.jpg')
            except:
                os.makedirs(id_name)
                image.save(id_name+'/'+caption[:20]+'.jpg')
    #         print(i)
        return total_urls

 #3 Facebook single post scrapping function

    def fb_post(URL):
        r = requests.get(URL) 
        soup = BeautifulSoup(r.content, 'html.parser')
        meta=soup.find_all('meta')
        if len(meta)<8:
            raise Exception('Something Went Wrong !!')
        else:
            for i,j in enumerate(meta):
                if i==6 and str(j).find("og:description"):
                    desc=str(j).split('"')[1].replace('\n','').replace('  ',' ')
                elif i==7 and str(j).find("og:image"):
                    image=str(j).split('"')[1]
                    image=str(image).replace('amp;','')
                elif i==8 and str(j).find("og:url"):
                    url=str(j).split('"')[1]
                    url=str(url).replace('amp;','')
        return desc,image,url
 #4 Google image 

    def google_image(query):
    # 5    query=input()
        try:
            find(query)
        except:
            pass
        save_images(total_urls,titles,query)
        clean_garbage_files(query)
 # 5 Instagram single post scrapper 
    def insta_post(url):
        URL=url
        print('Trying with : {}'.format(URL))
        text,image='',''
        with requests.Session() as session:
            r = requests.get(URL) 
            soup = BeautifulSoup(r.content, 'html.parser')
            json_data=soup.find('script',attrs={'type':"application/ld+json"})
            try:
                lst=list(json_data.children)
                lst=lst[0].replace('\n','').strip()
                json_=json.loads(lst)
    #             print(json_)
                text=json_['caption']
                url=json_['mainEntityofPage']['@id']
            except:
                text=soup.title.text
            lst_str=soup.find('meta',attrs={'property':"og:image"})
            image=str(lst_str).split('" property="og:image"')[0].split('<meta content="')[1].strip().replace('amp;','')
        return text,image


 #6 Trading Images 

    def trade(name,t='month'):
        """arg t: month,hour,week,minute"""
        global sleep_time
        URL = 'https://tradingview.com/chart/'      
        browser = webdriver.Chrome('./chromedriver') 
        browser.get(URL)
        #time.sleep(sleep_time)
        search_name(browser,sleep_time,name)
        period(browser,t='hour')
        img_name=save_image(browser,name)
        return img_name


 # 7 Twitter Single Image Scrapper 

    def twit_post(url):
        URL=url.replace('twitter.com','mobile.twitter.com')
        print('Trying with : {}'.format(URL))
        text,image,url='','',''
        with requests.Session() as session:
            try:
                r = requests.get(URL) 
                soup = BeautifulSoup(r.content, 'html.parser')
                text=soup.find('div',attrs={'class':"dir-ltr"})
                text_val=text.text
                url= str(text).split('data-url="')[1].split('"')[0]
                image=soup.find('div',attrs={'class':"media"}).find('img')
                image=str(image).split('src="')[1].split(':small')[0]
            except :
                pass
        return text_val,image,url


 # 8 Whatsapp messaging 

    def whatsapp():
        driver = webdriver.Chrome('./chromedriver') 
        driver.get("https://web.whatsapp.com/")
        agreement=input('did you scanned your web.whatsapp QR code y/n')
        if agreement =='y':
            while True:
                target=input("Enter receiver name : ")
                message=input("Enter message : ")
                n=int(input("Enter no. of time : "))
                try:
                    time.sleep(2)
                    search=driver.find_element_by_xpath('//*[@id="side"]/div[1]/div/label/div/div[2]')
                    search.send_keys(target)
                    time.sleep(2)
                    search.send_keys(Keys.ENTER)
                    send_message(target,message,n)
                except:
                    print('receiver name does not exist in your contact ')
                    try:
                        page=driver.current_url
                        print(target+" does not exist in your account ")
                    except:
                        print('Web.whatsapp.com closed ')
                        return

