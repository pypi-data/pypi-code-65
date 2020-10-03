__title__ = 'kakaomail'
__license__ = 'MIT'
__author__ = 'Kyunghoon (aloecandy@gmail.com)'
__version__ = '0.1.3'


import smtplib
from email.mime.text import MIMEText


sender=''
pw=''
def login(yourID,password):
    """
    check id,pw are correct
    store id,pw
    """
    global sender
    global pw
    
    sender=yourID+'@kakao.com'
    pw=password
    
    s=smtplib.SMTP_SSL("smtp.kakao.com",465)
    try:
        s.login( sender , pw ) 
        s.quit()
        return True
    except:
        print('KakaoMail: Failed to login')
        s.quit()
        return False
    
    
def send(recipient,subject,text):
    print('KakaoMail:\n\t'+'From: '+sender+
        '\tTo: '+recipient+
        '\tSubject: '+subject+
        '\tText:'+text)
    
    msg = MIMEText(text.encode('utf-8'),_charset='utf-8') 
    
    msg['Subject'] =subject
    msg['From'] = sender
    msg['To'] = recipient

    s=smtplib.SMTP_SSL("smtp.kakao.com",465)
    s.login( sender , pw ) 
    s.sendmail( sender, recipient, msg.as_string() ) 
    s.quit()
    print('KakaoMail: sent mail')
    