from .route import web
from flask import render_template, request, Response
import re
import requests
import os

url = os.environ.get("URL_BOT")
CSP= [
"base-uri 'self'",
"frame-ancestors 'none'",
"img-src 'self'",
"object-src 'none'",
"script-src 'self' 'unsafe-eval' https://*.google.com/ https://kit.fontawesome.com/",
"style-src 'self' 'unsafe-inline' https://fonts.googleapis.com/",
]


def use_regex(input_text):
    pattern = re.compile(r"http://webadmin:5000/", re.IGNORECASE)
    return pattern.match(input_text)


@web.route('/', defaults={'name': ''})
@web.route('/<name>',methods = ['GET'])
def home(name):
    if not name:
        name = "samurai"
    resp = Response((render_template("dashboard.html", name=name)))
    resp.headers['Content-Security-Policy'] = ';'.join(CSP)
    return resp



@web.route('/report',methods = ['GET'])
def report():
    return render_template("dashboard_report.html")


@web.route('/visit',methods = ['POST'])
def visit():
    if request.method == "POST":
        title = request.form['title']
        description = request.form['description']
        link = request.form['link']
        if not use_regex(link):
            return "wrong url format"

        obj = {'url': link}
        #send to bot
        x = requests.post(url, json = obj)
        if (x.content == b'OK'):
            return "success!"

    return "failed to visit"
