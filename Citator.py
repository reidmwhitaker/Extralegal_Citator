import json
import re
import os
import csv
import math
from datetime import datetime


class Opinion:
    def __init__(self, name="", text = "", opinion_text="", date_decided = "", author = "", joining = "", type = "", id = ""):
        self.text = text
        self.type = type
        self.date_decided = date_decided
        self.author = author
        self.joining = joining
        self.id = id
        self.opinion_text = opinion_text
        self.name = name
        self.citations = []

class OpinionCluster:
    def __init__(self, opinions = "", scdb_id = "", scdb_votes_majority = "", scdb_votes_minority = "",
                 name = "", name_full = "", attorneys = "", id = "", cite = "", saliance = "", court="",jurisdiction="",
                 docket="",date=""):
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
        self.court = court
        self.jurisdiction = jurisdiction
        self.docket = docket
        self.date = date

class Reference:
    def __init__(self, type="", title="untitled", authors=[("no_author","")], date="n.d.", journal_title="", volume="", issue="",
                 notes="", annotations="", pages="",edition="", volume_title="",start_page="",original_cite="",url=""):
        self.title = title
        if len(self.title) > 100:
            self.title_long = self.title
            self.title = self.title[0:99]
        self.type = type
        self.authors = authors
        self.date = date
        self.edition = edition
        self.journal_title = journal_title
        self.volume = volume
        self.issue = issue
        self.page = pages
        self.url = url
        self.original_cite=original_cite
        self.file_name = self.authors[0][0] + "_" + self.title + "_(" + self.date + ")"
        self.file_name = self.file_name.replace("/","_slash_")
        if len(self.file_name) > 199:
            self.file_name_long = self.file_name
            self.file_name = self.file_name[0:199]+self.file_name[-6:-1]
        self.id = convertToNumber(self.file_name)
        self.notes = notes
        self.annotations = annotations
        self.volume_title=volume_title
        self.start_page=start_page
        #todo:handle situations where the reference is already created
        self.write_to_file()

    def write_to_file(self):
        dir = get_dir_ref()
        json_2_b = {}
        json_2_b['type'] = self.type
        json_2_b['title'] = self.title
        json_2_b['authors'] = self.authors
        json_2_b['date'] = self.date
        json_2_b['volume'] = self.volume
        json_2_b['issue'] = self.issue
        json_2_b['journal_title'] = self.journal_title
        json_2_b['volume_title'] = self.volume_title
        json_2_b['start_page']=self.start_page
        json_2_b['pages'] = self.page
        json_2_b['edition'] = self.edition
        json_2_b['url'] = self.url
        json_2_b['id'] = self.id
        json_2_b['notes'] = self.notes
        json_2_b['annotations'] = self.annotations
        json_2_b['original_citation'] = self.original_cite
        json_out = json.dumps(json_2_b, indent=4, separators=(',', ': '))
        doc = open(dir + "/" +self.file_name +  ".json", 'w')
        doc.write(json_out)
        doc.close()

class Author:
    def __init__(self,first_name="",last_name="",id=""):
        self.first_name=first_name
        self.last_name=last_name
        self.id=id

class Citation:
    def __init__(self, opinion, reference):
        self.opinion = opinion
        self.reference = reference
        self.id = str(self.opinion.id) + "_" + str(self.reference.id)
        self.opinion_id = self.opinion.id
        self.reference_id = self.reference.id

    def export(self):
        cite_link = {'opinion_id':self.opinion_id,'opinion_name':self.opinion.name,
                     'reference_id':self.reference_id,'reference_name':self.reference.title}
        return(cite_link)

def convertToNumber(s):
    return int.from_bytes(s.encode(), 'little')

def convertFromNumber(n):
    return n.to_bytes(math.ceil(n.bit_length() / 8), 'little').decode()

def json_to_cluster(json_string):
    parsed_json = json.loads(json_string)
    #id = parsed_json['id']
    #court = parsed_json['court']
    #jurisdiction = parsed_json['jurisdiction']
    #docket = parsed_json['docket_no']
    #date = parsed_json['decision_date']
    #name = parsed_json['case_name']
    try:
        parsed_json['case_name_short']
    except:
        pass
    else:
        name_short = parsed_json['case_name_short']
    #citation = parsed_json['citation_1']
    opinion_count = 1
    opinions = []
    while ("opinion_text_" + str(opinion_count)) in parsed_json:
        id_opin = parsed_json['id'] + "_" + str(opinion_count)
        opinions.append(Opinion(id=id_opin, name=name_short, opinion_text=parsed_json['opinion_text'+"_"+str(opinion_count)]))
        opinion_count = opinion_count + 1
    cluster = OpinionCluster(id=id,opinions=opinions)
    #cluster = OpinionCluster(id=id,court=court,jurisdiction=jurisdiction,docket=docket,date=date,name_full=name,
                            # name=name_short,cite=citation,opinions=opinions)
    return cluster

def find_citations(opinion):
    text = opinion.opinion_text
    references = []
    citations = []
    reporter_titles = ["U.S.", "U. S.", "F.Supp","Pa.","F.Supp."]

    #match = re.search(r'(?<!;\S)([A-Z])\.\s(\S.+?)\,\s([\sA-Za-z:]+?)\s(\d*\-?\d*)\s\(([0-9]{3,4})\)', text)

    #todo: Make sure I am actually saving mutliple author situations
    #matches = re.findall(r"(?:[\"'\.;]|see|See|cf\.|Cf\.|Accord|accord)\s+(?:([A-Za-z])?\.\s+?([A-Za-z]+?)\s+?\&\s+?)?([A-Za-z])?\.\s+?([A-Za-z]+?),\s+?([\sA-Za-z:',]+?)\s+?(\d*\-?\d+)\s+?\(([\s\S]*?)([0-9]{3,4})\)",
           #              text)
    matches = re.finditer(r"(?:([A-Za-z])?\.\s+?([A-Za-z]+?)\s+?\&\s+?)?([A-Za-z])?\.\s+?([A-Za-z]+?),\s+?([\sA-Za-z:',]+?)\s+?(\d*\-?\d+)\s+?\(([\sA-Za-z\.\d]*\s)?([0-9]{3,4})\)",
                         text)
    if matches:
        for match in matches:
            if not match.group(1):
                author = [(match.group(4), match.group(3))]
            else:

                author = [(match.group(2), match.group(1)),(match.group(4), match.group(3))]
            references.append(Reference(type="book",authors=author,title=match.group(5),
                                        date=match.group(8),pages=match.group(6),edition=match.group(7),original_cite=match.string[match.start(1):match.end(8)]))
            citations.append(Citation(opinion,references[-1]))

    matches = re.finditer(r"(?:([A-Za-z])?\.\s+?([A-Za-z]+?)\s+?\&\s+?)?([A-Za-z])?\.\s+?([A-Za-z]+?),\s+?([\sA-Za-z:',]+?),\s+in\s+([\sA-Za-z:',]+?)\s+(\d*),\s+(\d*\-?\d+)\s+?\(([\sA-Za-z\.\d]*\s)?([0-9]{4})\)",
                         text)
    if matches:
        for match in matches:
            if not match.group(2):
                author = [(match.group(4), match.group(5))]
            else:
                author = [(match.group(2), match.group(1)),(match.group(4), match.group(3))]
            references.append(Reference(type="book section",authors=author,title=match.group(5),date=match.group(10),pages=match.group(8),
                                        volume_title=match.group(6),start_page=match.group(7),edition=match.group(9),original_cite=match.string[match.start(1):match.end(10)]))
            citations.append(Citation(opinion,references[-1]))

    matches = re.finditer(r"[^\s].[;\.\"]\s*(?:(?:See)|(?:supra))?,?\s+([A-Za-z\d][\sA-Za-z:',]+?[A-Za-z\d])\s+?(\d*\-?\d+)\s+?\(([A-Za-z\d][\sA-Za-z\d\.]*\s)?([0-9]{4})\)", text)
    if matches:
        for match in matches:
            references.append(Reference(type="book",title=match.group(1),pages=match.group(2),edition=match.group(3),date=match.group(4),original_cite=match.string[match.start(1):match.end(4)]))
            citations.append(Citation(opinion,references[-1]))

    # matches = re.findall(r"(?:[\"'\.;]|see|See|cf\.|Cf\.|Accord|accord)\s+([A-Za-z]+),\s+([A-Za-z\.\s:',]+),\s+(\d+)\s+([A-Za-z\.\s]+)\s+(\d+)(?:,\s+(\d*\-?\d+))?\s+\(([\s\S]*?)([0-9]{3,4})\)",
        #                    text)
    #todo: fix indexing
    matches = re.finditer(
        r"(?:([A-Za-z]+?)\s+?\&\s+?)?(?:([A-Z])\.\s+)?([A-Za-z]+),\s+([^(see)][A-Za-z\d][\sA-Za-z:',\-\")]+?[A-Za-z\d]),\s+(\d+)\s+([A-Za-z\.\s]+)\s+(\d+)(?:,\s+(\d*\-?\d+))?\s+\(([\sA-Za-z\.\d]*?)([0-9]{4})\)",
        text)
        #r"(?:([A-Z])\.\s+)?([A-Za-z]+),\s+([^(see)][A-Za-z\d][\sA-Za-z:',\-\")]+?(?:v\.)?[\sA-Za-z:',\-\")]+?[A-Za-z\d]),\s+(\d+)\s+([A-Za-z\.\s]+)\s+(\d+)(?:,\s+(\d*\-?\d+))?\s+\(([\sA-Za-z\.\d]*?)([0-9]{3,4})\)",
        #text)
    if matches:
        for match in matches:
            if match.group(5) not in  reporter_titles:
                if not match.group(1):
                    author = [(match.group(3), match.group(2))]
                else:
                    author = [(match.group(3), match.group(2)), (match.group(1), match.group(1))]
                name = match.group(4)
                if author == [("Note","")]:
                    name = "Note, " + name
                    author = [("no_author","")]
                references.append(Reference(type="journal", authors=author, title=name, volume=match.group(5),
                                            journal_title=match.group(6), start_page=match.group(7), pages=match.group(8), edition=match.group(9),
                                            date=match.group(10),original_cite=match.string[match.start(1):match.end(10)]))
                citations.append(Citation(opinion, references[-1]))

    matches = re.finditer(
        r"([^\s]+),\s([^,]+),\s([^,]+),\s([A-Za-z]{3}.\s\d{1,2},\s[0-9]{3,4}),\sp.\s([A-Za-z0-9]+).", text)
    if matches:
        for match in matches:
            try:
                datetime.strptime(match.group(4),"%b. %d, %Y").isoformat()
            except:
                try:
                    datetime.strptime(match.group(4), "%B %d, %Y").isoformat()
                except:
                    date = str(datetime.strptime(match.group(4), "%Y").year)
                else:
                    date=datetime.strptime(match.group(4), "%B %d, %Y").isoformat()
            else:
                date=datetime.strptime(match.group(4),"%b. %d, %Y").isoformat()
            references.append(Reference(type="newspaper",authors=[(match.group(1),"")],date=date,journal_title=match.group(3),title=match.group(2),start_page=match.group(5),original_cite=match.string[match.start(1):match.end(5)]))
            citations.append(Citation(opinion, references[-1]))

    matches = re.finditer(
            r"([^\s]+),\s([^,]+),\s([^,]+),\s([A-Za-z]{3}.\s\d{1,2},\s[0-9]{3,4}),\sonline at ([A-Za-z://.0-9]+).\s",
        text
    )
    if matches:
        for match in matches:
            try:
                datetime.strptime(match.group(4),"%b. %d, %Y").isoformat()
            except:
                try:
                    datetime.strptime(match.group(4), "%B %d, %Y").isoformat()
                except:
                    date = str(datetime.strptime(match.group(4), "%Y").year)
                else:
                    date=datetime.strptime(match.group(4), "%B %d, %Y").isoformat()
            else:
                date=datetime.strptime(match.group(4),"%b. %d, %Y").isoformat()
            references.append(Reference(type="newspaper",authors=[(match.group(1),"")],date=date,journal_title=match.group(3),title=match.group(2),url=match.group(5),original_cite=match.string[match.start(1):match.end(5)]))
            citations.append(Citation(opinion, references[-1]))

    return citations

def get_dir(dir="./../Legal_Parser/Parsed_Cases"):
    #dir="./../parsed_cases_CAP"
    dir="./../Citator_Cases"
    os.makedirs(dir, exist_ok=True)
    return dir

def get_dir_ref(dir="./references"):
    os.makedirs(dir, exist_ok=True)
    return dir

def main():
    dir = get_dir()
    citations = []
    for file in os.listdir(dir):
        if file.endswith(".json"):
            print(dir + "/" + file)
            json_data = open(dir + "/" + file).read()
            opinion_cluster = json_to_cluster(json_data)
            for opinion in opinion_cluster.opinions:
                citations = citations + (find_citations(opinion))

    with open('./citations.csv','w') as csvfile:
        fieldnames = ['opinion_id', 'opinion_name','reference_id','reference_name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for cite in citations:
            writer.writerow(cite.export())

if __name__ == "__main__":
    main()
