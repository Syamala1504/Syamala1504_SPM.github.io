import smtplib
from smtplib import SMTP
from email.message import EmailMessage
def sendmail(to,subject,body):
    server=smtplib.SMTP_SSL('smtp.gmail.com',465)
    server.login('dimpu.syam.1504@gmail.com','avbb lvgm ktpk zesw')
    msg=EmailMessage()
    msg['FROM']='dimpu.syam.1504@gmail.com'
    msg['SUBJECT']=subject
    msg['TO']=to
    msg.set_content(body)
    server.send_message(msg)
    server.close()