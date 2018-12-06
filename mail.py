"""
ccextractor-web | mail.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54+ccextractorweb[at]gmail.com
Link     : https://github.com/saurabhshri

"""

import requests
from flask import current_app as app
from logger import Logger
from config_parser import general_config

mail_logger = Logger(log_level=general_config['LOG_LEVEL'],
                     dir=general_config['LOG_FILE_DIR'],
                     filename="mail",
                     format='[%(asctime)s] [%(name)s] [%(levelname)s] [%(pathname)s#L%(lineno)d] | %(message)s\n\n',
                     console_level='DEBUG')
mail_log = mail_logger.get_logger("mail")


def get_api_url(domain):
    return "https://api.mailgun.net/v3/{domain}/messages".format(domain=domain)


def send_simple_message(receiver, subject, body):
    api_key = app.config['MAILGUN_PVT_API_KEY']
    domain = app.config['EMAIL_DOMAIN']

    sender = 'CCExtractor Web <no-reply@{domain}>'.format(domain=domain)

    response = requests.post(get_api_url(domain),
                             auth=("api", api_key),
                             data={"from": sender,
                                   "to": receiver,
                                   "subject": subject,
                                   "text": body})

    if response.status_code is not 200:
        mail_log.debug('\n[{response}] \nTO : {to}, \nfrom : {sender}, \nsubject : {subject}, \ntext: {text}'.format(response=response,
                                                                                                                     to=receiver,
                                                                                                                     sender=sender,
                                                                                                                     subject=subject,
                                                                                                                     text=body))
    else:
        mail_log.info('\n[{response}] \nTO : {to}, \nfrom : {sender}, \nsubject : {subject}, \ntext: {text}'.format(response=response,
                                                                                                                    to=receiver,
                                                                                                                    sender=sender,
                                                                                                                    subject=subject,
                                                                                                                    text=body))

    return response
