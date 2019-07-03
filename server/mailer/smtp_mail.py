#!/usr/bin/python
# -*- coding: utf-8 -*-
import smtplib as smtp
from getpass import getpass

#with open("users.pickle", "rb") as f:
#    data_new = pickle.load(f)
class SMTP:
    def __init__(self, from_mail, password):
        self.from_mail = from_mail
        self.password = password


    def send_message(self, to_mail, message, subject):
        email = self.from_mail
        password = self.password
        dest_email = to_mail
        subject = subject
        email_text = message
        message = 'From: {}\nTo: {}\nSubject: {}\n\n{}'.format(email,
                                                               dest_email,
                                                               subject,
                                                               email_text)

        server = smtp.SMTP_SSL('smtp.yandex.com')
        server.set_debuglevel(1)
        server.ehlo(email)
        server.login(email, password)
        #server.auth_plain()
        server.sendmail(email, dest_email, message)
        server.quit()
