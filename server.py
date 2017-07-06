import configparser
import smtplib
import os

config = configparser.ConfigParser()
config.read('config.ini')
MAIL = config['MAIL']['mail']

PASSWORD = os.environ.get('MAIL_PASSWORD', '')

server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10*60)
server.ehlo()
server.login(MAIL, PASSWORD)

def send_mail(stu_id, reg_code):
    sender = MAIL
    receiver = '{}@ntu.edu.tw'.format(stu_id.lower())
    message = """
    From: {sender}
    To: {receiver}
    Subject: NTUSC_vote_system

    Your register code is: {content}
    """.format(
        sender=sender,
        receiver=receiver,
        content=reg_code
    )
    server.sendmail(sender, receiver, message)
