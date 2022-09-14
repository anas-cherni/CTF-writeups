import requests

url="http://web.chal.csaw.io:5010/"
session = requests.Session()

with session : 
    next_word='stuff'
    while True:
        response1= session.get(url+next_word)
        """print(session.cookies)"""
        try:
            startingIndex=response1.text.index('href="/')
            endText=response1.text[startingIndex:].index('">')
        except :
            print(response1.text)
            break
        print("next word:",response1.text[7+startingIndex:endText+startingIndex])
        next_word=response1.text[7+startingIndex:endText+startingIndex]



