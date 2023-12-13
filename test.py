import requests

url = 'http://localhost:3000/predict'
files = open('tumpeng_menoreh.003.jpg', 'r')

res = requests.post(url, files=files)

print(res.text)
