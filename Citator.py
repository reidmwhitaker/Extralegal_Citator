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
        self.citations = []

    def find_citation(self):
        match = re.search(r'(?<!;\S)([A-Z])\.\s(\S.+?)\,\s([\sA-Za-z:]+?)\s(\d*\-?\d*)\s\(([0-9]{3,4})\)',self.opinion_text)
        citations.apend()

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

#todo: is judge needed?
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

def find_citations():
    return null

if __name__ == "__main__":
    main()
