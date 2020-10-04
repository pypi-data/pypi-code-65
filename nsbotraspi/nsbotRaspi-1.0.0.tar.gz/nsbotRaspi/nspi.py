from selenium import webdriver
from time import sleep
import schedule
import datetime
import requests

class MetarSpeciTaf:
    def __init__(self, line_token='', time_stop=''):
        self.driver = None
        self.line_token = line_token
        self.time_stop = time_stop # UTC Time
        self.code_metarspeci = 'initial_code'
        self.code_taf = 'initial_code'
        self.hr = 'time'
        
    def send_Line(self, msg):
        # Function for sending code to Line application
        while True:
            url = 'https://notify-api.line.me/api/notify'
            token = self.line_token
            headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer '+token}
            r = requests.post(url, headers=headers , data = {'message':msg})
            if r.status_code == 200:
                break
            else:
                sleep(60)
                continue
    
    def setupDriver(self):
        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)
    
    def run_bot(self):
        self.send_Line('Online...')
        self.driver.get("https://nsweb.tmd.go.th/#showMetars")
        sleep(10)
        self.driver.execute_script("window.open('https://nsweb.tmd.go.th/#showTAFs','new window')")
        
        while self.hr != self.time_stop:
            
            sleep(30)
            dt = datetime.datetime.utcnow()
            self.hr = dt.strftime('%H')
            
            self.driver.switch_to_window(self.driver.window_handles[0])
            sleep(15)
            try:
                list_of_elements = self.driver.find_elements_by_xpath('//p[@class="js-metar"]')
                stations = [station.text for station in list_of_elements];
                find_vtse = [i for i in stations if "VTSE" in i]
                read = find_vtse[0]
            
                if read == self.code_metarspeci:
                    pass
                else:
                    self.code_metarspeci = read
                    self.send_Line(self.code_metarspeci)
                    print(self.code_metarspeci)

            except Exception as e:
                print("METAR or SPECI error: " ,e)
                pass
            
            self.driver.switch_to_window(self.driver.window_handles[1])
            sleep(15)
            try:
                list_of_elements_taf = self.driver.find_elements_by_xpath('//p[@class="js-taf"]')
                stations_taf = [station_taf.text for station_taf in list_of_elements_taf];
                find_vtse_taf = [i for i in stations_taf if "VTSE" in i]
                read_taf = find_vtse_taf[0]
            
                if read_taf == self.code_taf:
                    pass
                else:
                    self.code_taf = read_taf
                    self.send_Line(self.code_taf)
                    print(self.code_taf)
                
            except Exception as p:
                print("TAF error: ", p)
                pass
        
        self.driver.quit()
        self.send_Line('Offline...')