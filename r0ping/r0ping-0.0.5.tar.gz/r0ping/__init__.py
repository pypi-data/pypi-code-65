import colorama
import os
import keyboard, random, os, string, sys, time, pickle, win32clipboard
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from colorama import Fore

def intro():
    print(f'''
{Fore.RED}    ▄████████ ███    █▄   ▄████████    ▄█   ▄█▄ 
   ███    ███ ███    ███ ███    ███   ███ ▄███▀ 
   ███    █▀  ███    ███ ███    █▀    ███▐██▀   
  ▄███▄▄▄     ███    ███ ███         ▄█████▀    
 ▀▀███▀▀▀     ███    ███ ███        ▀▀█████▄    
   ███        ███    ███ ███    █▄    ███▐██▄   
   ███        ███    ███ ███    ███   ███ ▀███▄ 
   ███        ████████▀  ████████▀    ███   ▀█▀ 
                                     ▀         
 {Fore.CYAN}discord.link/pimp
 {Fore.CYAN}invite.gg/pimp
 {Fore.CYAN}discord.lol/pimp{Fore.RESET}''')
 
def title():
    os.system('title fuck')
    
browser = webdriver.Firefox()

def discord():
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))

    os.system('cls')

    browser.get("https://www.fakemail.net")
    time.sleep(3)
    browser.find_element_by_xpath('/html/body/div[2]/div[2]/div[2]/div').click()
    time.sleep(2)
    win32clipboard.OpenClipboard()
    data = win32clipboard.GetClipboardData()
    win32clipboard.CloseClipboard()
    f = open("info/emails.txt", "a")
    f.write(f"Email: {data}" + '\n')
    f.close()

    usernames = [
        'Devils',
        'Devill'
    ]

    username = random.choice(usernames)

    password = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))

    os.system('cls')
    f = open("info/discord_info.txt", "a")
    f.write(f"Email:{data}, Username:{username}, Password:{password}, DOB:01/01/1998" + '\n')
    f.close()
    print(f'Email: {data}')
    print(f'Username: {username}')
    print(f'Password: {password}')

    browser.get("https://discord.com")
    time.sleep(5)
    browser.find_element_by_xpath('/html/body/div/div/div/div[1]/div[2]/div/div[2]/button').click()
    time.sleep(2)
    browser.find_element_by_xpath('/html/body/div/div/div/div[1]/div[2]/div/div[2]/form/input').send_keys(username)
    time.sleep(1)
    browser.find_element_by_xpath('/html/body/div/div/div/div[1]/div[2]/div/div[2]/form/button').click()
    time.sleep(12)
    # DOB:
    browser.find_element_by_xpath('/html/body/div/div[6]/div[2]/div/div/div[2]/div/div/div/form/div[3]/div[1]/div[1]/div/div/div/div/div[1]').click()
    browser.find_element_by_xpath('//*[@id="react-select-2-option-0"]').click()
    time.sleep(1)
    browser.find_element_by_xpath('//*[@id="app-mount"]/div[6]/div[2]/div/div/div[2]/div/div/div/form/div[3]/div[1]/div[2]/div/div/div/div/div[1]').click()
    browser.find_element_by_xpath('//*[@id="react-select-3-option-0"]').click()
    time.sleep(1)
    browser.find_element_by_xpath('//*[@id="app-mount"]/div[6]/div[2]/div/div/div[2]/div/div/div/form/div[3]/div[1]/div[3]/div/div/div/div/div[1]').click()
    browser.find_element_by_xpath('//*[@id="react-select-4-option-19"]').click()
    time.sleep(1)
    browser.find_element_by_xpath('//*[@id="app-mount"]/div[6]/div[2]/div/div/div[2]/div/div/div/form/div[4]/div/button').click()
    time.sleep(1)
    browser.find_element_by_xpath('//*[@id="app-mount"]/div[6]/div[2]/div/div/div[2]/button').click()
    # Claim your account:
    time.sleep(3)
    browser.find_element_by_xpath('//*[@id="app-mount"]/div[6]/div[2]/div/div/div[2]/form/div[1]/div/input').click()
    browser.find_element_by_xpath('//*[@id="app-mount"]/div[6]/div[2]/div/div/div[2]/form/div[1]/div/input').send_keys(data)
    time.sleep(2)
    browser.find_element_by_xpath('//*[@id="app-mount"]/div[6]/div[2]/div/div/div[2]/form/div[2]/div/input').click()
    browser.find_element_by_xpath('//*[@id="app-mount"]/div[6]/div[2]/div/div/div[2]/form/div[2]/div/input').send_keys(password)
    time.sleep(2)
    browser.find_element_by_xpath('//*[@id="app-mount"]/div[6]/div[2]/div/div/div[2]/form/button').click()
    time.sleep(4)
    browser.get("https://www.fakemail.net")
    time.sleep(0)
    print("All you gotta do is verify now!")