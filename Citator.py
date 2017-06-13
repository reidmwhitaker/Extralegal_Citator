import json
from bs4 import BeautifulSoup
import re
import requests
import os
import warnings


class Opinion:
    def __init__(self, name="", text = "", opinion_text="", date_decided = "", author = "", joining = "", type = "", id = ""):
        self.text = text
        self.type = type
        self.date_decided = date_decided
        self.author = author
        self.joining = joining
        self.id = id
        self.opinion_text = ""
        self.name = name

class OpinionCluster:
    def __init__(self, opinions = "", scdb_id = "", scdb_votes_majority = "", scdb_votes_minority = "",
                 name = "", name_full = "", attorneys = "", id = "", cite = "", saliance = ""):
        self.opinions = opinions
        self.scdb_id = scdb_id
        self.scdb_votes_majority = scdb_votes_majority
        self.scdb_votes_minority = scdb_votes_minority
        self.name = name
        self.name_full = name_full
        self.attorneys = attorneys
        self.id = id
        self.cite = cite
        self.saliance = saliance

class Docket:
    def __init__(self, id = ""):
        self.id = id

class Judge:
    def __init__(self, name = "", party_appoint = ""):
        self.name = name
        self.party_appoint = party_appoint

class Reference:
    def __init__(self, title = "", author = "", date="", journal_title = "", volume = "", page = "", id=""):
        self.title = title
        self.author = author
        self.date = date
        self.journal_title = journal_title
        self.volume = volume
        self.page = page
        self.id = id

class Citation:
    def __init__(self, opinion="", reference="", id=""):
        self.opinion = opinion
        self.reference = reference
        self.id = id

def main():
    dir = get_dir()
    for file in os.listdir(dir):
        json_data = open(dir + "/" + file).read()
        parse_CL(json_data)
    print("end")

def parse_CL(json_CL):
    warnings.filterwarnings('ignore',message=r".*looks like a URL. Beautiful Soup is not an HTTP client. You should probably.*")
    data = json.loads(json_CL)
    cluster = BeautifulSoup(data['cluster'], 'html.parser').text
    id = re.match(r"http://www.courtlistener.com/api/rest/v3/clusters/(\d+)", cluster)
    cluster = OpinionCluster(id=id.group(1))
    opinion = Opinion()

    absolute = BeautifulSoup(data['absolute_url'], 'html.parser').text
    name = re.match(r"/opinion/(\d+)/(.*)/", absolute)
    opinion.name = name.group(1) + "_" + name.group(2)

    opinion.text = BeautifulSoup(data['html'], 'html.parser')
    cluster.opinion = opinion
    if data['html'] != "":
        opinion.text = BeautifulSoup(data['html'],'html.parser')
    else:
        return

    cites = []
    for tag in opinion.text.find_all('p', class_='case_cite'):
        cites.append(tag.text)
    opinion.cite = cites

    reduced_soup = opinion.text.find_all('div', class_="num")
    opinion_text = ""
    for tag in reduced_soup:
        opinion_text_soup = tag.find_all('p', class_="indent")
        for tag in opinion_text_soup:
            opinion_text = opinion_text + tag.prettify()
    footnotes = opinion.text.find_all('div', class_="footnote", id=re.compile("^fn\d+"))
    for tag in footnotes:
        opinion_text = opinion_text + tag.prettify()
    opinion.opinion_text = opinion_text

    os.makedirs("./parsed_cases/", exist_ok=True)
    doc = open("./parsed_cases/" + opinion.name + "_parsed", 'w')
    doc.write(opinion.opinion_text)
    doc.close()

def get_dir(dir="./../Citator_Cases"):
    return dir

def split_opinion(cluster, init_opinion):
    text_full_soup = init_opinion.text
    text = init_opinion.opinion_text
    split_text=text.split()

#Test parsing algorithm on *Daubert* as downloaded from CourtListener
def daubert_Test():
    json_data = open("./../Citator_Cases/Daubert.json").read()
    data = json.loads(json_data)
    cluster = BeautifulSoup(json.loads(json_data)['cluster'],'html.parser').text
    id = re.match(r"http://www.courtlistener.com/api/rest/v3/clusters/(\d+)", cluster)
    daubert = OpinionCluster(id=id.group(1))
    daubert_opinion = Opinion()
    daubert_opinion.text = BeautifulSoup(json.loads(json_data)['html'], 'html.parser')

    reduced_soup = daubert_opinion.text.find_all('div', class_="num")
    opinion_text = ""
    for tag in reduced_soup:
        opinion_text_soup = tag.find_all('p', class_="indent")
        for tag in opinion_text_soup:
            opinion_text = opinion_text + tag.prettify()
    footnotes = daubert_opinion.text.find_all('div', class_="footnote", id=re.compile("^fn\d+"))
    for tag in footnotes:
        opinion_text = opinion_text + tag.prettify()
    daubert_opinion.opinion_text = opinion_text

    doc = open('Daubert_final_reduced', 'w')
    doc.write(daubert_opinion.opinion_text)
    doc.close()

    cites = []
    for tag in daubert_opinion.text.find_all('p',class_='case_cite'):
        cites.append(tag.text)
    daubert.cite = cites

def find_citations():
    return null

if __name__ == "__main__":
    main()
