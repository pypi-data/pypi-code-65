import smtplib
import csv
import re
import os
from email.message import EmailMessage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
import urllib.parse
import requests


class SmsMessage():
    def __init__(self,request_body:[str],path:str=None):
        # a dictionary that holds all the sms info. Will alwayse have Media, Body, From, and SmsMessageSid
        self.sms:dict = {'SmsMessageSid':str,} 
        self.sms:dict = {'Media':[],'Body':str,'From':str,'SmsMessageSid':str}
        # paths to all the img/video files
        self.img_paths = []

        # parse through all items in body and add all key and value pairs to dict
        for i in request_body:
            if 'MediaUrl' in i:
                media_type = ''
                url = urllib.parse.unquote(i.split("=")[1])

                try:
                    wildcard = re.findall('\d$',i.split("=")[0])[0]
                except:
                    wildcard = None

                if wildcard is not None:
                    for i in request_body:
                        if 'MediaContentType' in i:
                            if re.search('[{}]$'.format(wildcard),i.split("=")[0]) is not None:
                                media_type = i.split("=")[1]
                                # print('im in')
                                # print(media_type)
                                break
                else:
                    for i in request_body:
                        if 'MediaContentType' in i:
                            media_type = i.split("=")[1]

                print(media_type)
                media_obj = SmsMessageMedia(url,media_type)
                self.sms['Media'].append(media_obj)


            elif 'Body' in i:
                value = urllib.parse.unquote_plus(i.split("=")[1])
                self.sms['Body'] = value

            elif 'From' in i:
                value = urllib.parse.unquote_plus(i.split("=")[1])
                self.sms['From'] = value

            elif 'SmsMessageSid' in i:
                value = i.split("=")[1]
                self.sms['SmsMessageSid'] = value

            else:
                key = i.split("=")[0]
                value = i.split("=")[1]
                self.sms[key] = value

        # save all media sent from the message to specified path or ~home/user/from_number/media_file
        if path is None:
            current_home_dir = str(Path.home())
            x = 0
            path_to_file:str = current_home_dir + "/" + str(self.sms['From'][8:])
            if not os.path.isdir(path_to_file):
                os.mkdir(path_to_file)
            for media in self.sms['Media']:
                # print("!!!!!!{}!!!!!!!!!".format(media))
                if media.media_type:
                    # print("!!!!!!!{}!!!!!!!!!".format(path_to_file))
                    path_to_file = path_to_file + "/" + self.sms['SmsMessageSid'] + str(x) + ".jpg"
                    media.download_img(path=path_to_file)
                    self.img_paths.append(path_to_file)
                else:
                    path_to_file = path_to_file + "/" + self.sms['SmsMessageSid'] + str(x) + ".mp4"
                    media.download_img(path_to_file)
                    self.img_paths.append(path_to_file)
        else:
            x = 0
            path_to_file:str = current_home_dir + "/" + str(self.sms['From'][8:])
            for media in self.sms['Media']:
                if media.media_type:
                    path_to_file = path_to_file + "/" + self.sms['SmsMessageSid'] + str(x) + ".jpg"
                    media.download_img(path_to_file)
                    self.img_paths.append(path_to_file)
                else:
                    path_to_file = path_to_file + "/" + self.sms['SmsMessageSid'] + str(x) + ".mp4"
                    media.download_img(path_to_file)
                    self.img_paths.append(path_to_file)

    def __str__(self):
        if self.sms['From'] is not None:
            return("Message received from {}".format(self.sms['From']))
        else:
            return("Message has not been received yet!")

class SmsMessageMedia():
    def __init__(self, mediaUrl:str, mediaType:str=None):
        self.mediaUrl = mediaUrl
        self.mediaType = mediaType
    
    def download_img(self,path:str):
        source = open(path, 'wb')
        source.write(requests.get(self.mediaUrl).content)
        source.close()

    @property
    def media_type(self):
        if 'image' in self.mediaType:
            return True
        else:
            return False

    def __str__(self):
        return("URL for media in SmsMessage: {} of type {}".format(self.mediaUrl,self.mediaType))

class Email():
    def __init__(self,sender:str,receiver:str,subject:str):
        self.sender = sender
        self.receiver = receiver
        self.subject = subject

    def __str__(self):
        return("sending email from {}, to {}".format(self.sender,self.receiver))

    def send_email(self,sms_message:SmsMessage):
        try:
            msg = MIMEMultipart()
            msg['Subject'] = self.subject
            msg['From'] = self.sender
            msg['To'] = self.receiver
            msg.attach(MIMEText(sms_message.sms['Body'],'plain'))

            if len(sms_message.img_paths) != 0:
                for i in sms_message.img_paths:
                    attachment = MIMEApplication(open(i, "rb").read(), _subtype="txt")
                    attachment.add_header('Content-Disposition', "attachment", filename= i) 
                    msg.attach(attachment)


            gmail_server = smtplib.SMTP_SSL('smtp-relay.gmail.com',465)
            gmail_server.ehlo()
            gmail_server.sendmail(self.sender, self.receiver,msg.as_string())
            gmail_server.close()
            print(f"Email was succesfully sent to {self.receiver}")
            
        except smtplib.SMTPRecipientsRefused:
            print("When sending the email, the receiver(s) did not receive any email. Check the email format")
            pass
        except smtplib.SMTPHeloError:
            print("When sending the email, the server did not reply properly")
            pass
        except smtplib.SMTPSenderRefused:
            print(f"When sending the email, server did not accept from adress: {self.sender}")
            pass
        except smtplib.SMTPDataError as e:
            print(f"When sending the email, SMTP got an unexpected error: {e}")
            pass
        except Exception as e:
            print(f"When sending the email, an unexpected error occured: {e}")
            pass

class Csv():
    def __init__(self,filename=None):
        self.fields = ['from','message','path']
        self.filename = filename

        if filename is None:
            self.filename = "twillio.csv"
        
            with open(filename,'w') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(self.fields)
        else:
            with open(self.filename,'w') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(self.fields)


    def add_to_csv_file(self,sms_message:SmsMessage, filename=None):
        rows = [[sms_message.from_number, sms_message.body, sms_message.img_paths]]

        with open(self.filename,'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerows(rows)