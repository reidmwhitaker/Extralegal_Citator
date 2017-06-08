import json
from bs4 import BeautifulSoup

json_data=open("./../Daubert.json").read()
data = json.loads(json_data)
daubert = {}
daubert['text'] = data['html']
print(daubert)