"""
ccextractor-web | mail.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54+ccextractorweb[at]gmail.com
Link     : https://github.com/saurabhshri

"""

import requests
from flask import current_app as app

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
    return response
