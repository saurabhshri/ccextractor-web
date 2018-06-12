"""
ccextractor-web | mail.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54+ccextractorweb[at]gmail.com
Link     : https://github.com/saurabhshri

"""

import requests

def send_simple_message(receiver, subject, body):
    from flask import current_app as app
    api_key = app.config['MAILGUN_PVT_API_KEY']
    domain = app.config['EMAIL_DOMAIN']
    sender = 'CCExtractor Web <no-reply@{domain}>'.format(domain=domain)
    return requests.post("https://api.mailgun.net/v3/{domain}/messages".format(domain=domain),
                         auth=("api", api_key),
                         data={"from": sender,
                               "to": receiver,
                               "subject": subject,
                               "text": body})
