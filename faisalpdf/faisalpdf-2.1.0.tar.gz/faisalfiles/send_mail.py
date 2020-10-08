"""for sending mail ,iterative"""

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from pathlib import Path
from string import Template
import smtplib

t2 = Template(Path("t2.html").read_text())

message = MIMEMultipart()

"""str:entre you name in string"""
message["from"] = ""
message["to"] = "" #senders email
message["subject"] = ""

"""create your template"""
body = t2.substitute({"name":""}) 
message.attach(MIMEText(body,"html"))
message.attach(MIMEImage(Path("").read_bytes()))


with smtplib.SMTP(host="smtp.gmail.com", port=587) as smtp:
    smtp.ehlo()
    smtp.starttls()

    """enter your email,password"""
    smtp.login("","") 
    
    #smtp.send_message(message)
    
    # for x in range(1):
    #     smtp.send_message(message)
    print("sent")