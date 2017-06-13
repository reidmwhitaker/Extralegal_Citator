import json
from bs4 import BeautifulSoup
import re

json_data=open("./../Citator_Cases/Daubert.json").read()
data = json.loads(json_data)
daubert = {}
daubert['text'] = data['html']
daubert['soup'] = BeautifulSoup(daubert['text'], 'html.parser')

doc = open('Daubert_text','w')
doc.write(daubert['soup'].get_text())
doc.close()

doc = open('Daubert_html','w')
doc.write(daubert['soup'].prettify())
doc.close()

doc = open('Daubert_reduced','w')
daubert['reduced_soup']=daubert['soup'].find_all('div',class_="num")
for tag in daubert['reduced_soup']:
    doc.write(tag.prettify())
doc.close()

new_data_raw=open("./Daubert_reduced").read()
new_data=BeautifulSoup(new_data_raw, 'html.parser')
final_text=new_data.find_all('p',class_="indent")
doc = open('Daubert_final_reduced','w')
for tag in final_text:
    doc.write(tag.prettify())
daubert['footnotes']=daubert['soup'].find_all('div',class_="footnote", id=re.compile("^fn\d+"))
for tag in daubert['footnotes']:
    doc.write(tag.prettify())
doc.close

doc = open('Daubert_tags','w')
for tag in daubert['soup'].find_all(True):
    doc.write(tag.name + '\n\n')
doc.close()