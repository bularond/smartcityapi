#!/usr/bin/python
# -*- coding: utf-8 -*-
import pickle
import smtplib

#with open("users.pickle", "rb") as f:
#    data_new = pickle.load(f)

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# create message object instance
msg = MIMEMultipart()
#asd

message = "Thank you"

# setup the parameters of the message
password = "C5vCGdtVi_64c7"
msg['From'] = "no-repy@gradintegra.com"
msg['To'] = "djalil6789@gmail.com"
msg['Subject'] = "Subscription"

# add in the message body
msg.attach(MIMEText(message, 'plain'))

#create server
server = smtplib.SMTP('smtp.yandex.ru: 465')

server.starttls()

# Login Credentials for sending the mail
server.login(msg['From'], password)

# send the message via the server.
server.sendmail(msg['From'], msg['To'], msg.as_string())

server.quit()
