import json
import re
import os
import csv
import math
from datetime import datetime
import pickle

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

    def add_citation(self, citation):
        self.citations = self.citations.append(citation)

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

class InvalidCitationError(Exception):
    """Exception raised when trying to create invalid citations and references

    Attributes:
       expression -- invalid expression that causes the error"""
    def __init__(self, expression):
        self.expression = expression

class Reference:
    def __init__(self, type="", title="untitled", authors=[("no_author","")], date="n.d.", journal_title="", volume="", issue="",
                 notes="", annotations="", pages="",edition="", volume_title="",start_page="",original_cite="",
                 full_cite="",url="",citations=[], count=1):
        self.title = title
        if len(self.title) > 100:
            self.title_long = self.title
            self.title = self.title[0:99]
        self.type = type
        self.authors = authors
        date_fixed = self.get_date(date)
        self.date = date_fixed
        self.edition = edition
        self.journal_title = journal_title
        self.volume = volume
        self.issue = issue
        self.page = pages
        self.url = url
        self.original_cite=original_cite
        self.full_cite = full_cite
        self.notes = notes
        self.annotations = annotations
        self.volume_title=volume_title
        self.start_page=start_page
        self.citations = citations
        self.citation_count = count

        self.verify()
        self.correct()

        self.file_name = self.authors[0][0] + "_" + self.title + "_(" + self.date + ")"
        self.file_name = self.file_name.replace("/","_slash_")
        if len(self.file_name) > 199:
            self.file_name_long = self.file_name
            self.file_name = self.file_name[0:199]+self.file_name[-6:-1]
        self.id = convertToNumber(self.file_name)

        #todo:handle situations where the reference is already created
        self.save()

    def __eq__(self):
        return self.id

    def __hash__(self):
        return self.id

    def verify(self):
        if self.title == "Brief for Petitioners":
            raise InvalidCitationError("Brief!")
        reporter_titles = ["U.S.", "U. S.","F. 2d","Cl. Ct.","Ct. Cl.","F. Supp.","So. 2d","A. 2d","F. C. C. 2d",
                           "F. 3d","P. 2d","Eng. Rep.","USPQ 2d","N. L. R. B.","How.","F. M. S. H. R. C.",
                           "Fed. Reg.","F. L. R. A.","Cranch","N. W. 2d","S. E. 2d","N. C.","F 2d","F 3d",
                           "N. E. 2d","Wall.","Wheat.","Dallas","Pet.","Black"]
        if self.journal_title in reporter_titles:
            raise InvalidCitationError("Law reporter--not a journal")
        for title in reporter_titles:
            if title in self.journal_title:
                raise InvalidCitationError("Law reporter--not a journal")
        if "; id." in self.journal_title:
            #print(self.journal_title)
            raise InvalidCitationError("'; id.'")

    def get_date(self, date_raw):
        if date_raw == 'n.d.':
            date_return = "no_date"
        else:
            try:
                datetime.strptime(date_raw, "%b. %d, %Y").isoformat()
            except:
                try:
                    datetime.strptime(date_raw, "%B %d, %Y").isoformat()
                except:
                    try:
                        datetime.strptime(date_raw, "%b. %d,%Y").isoformat()
                    except:
                        try:
                            datetime.strptime(date_raw, "%b. %d %Y").isoformat()
                        except:
                            try:
                                datetime.strptime(date_raw, "%B %d,%Y").isoformat()
                            except:
                                if date_raw:
                                    if "Art." in date_raw:
                                        raise InvalidCitationError("Art. is not a Month")
                                try:
                                    str(datetime.strptime(date_raw, "%Y").year)
                                except:
                                    raise InvalidCitationError("Not a valid date")
                                else:
                                    date_return = str(datetime.strptime(date_raw, "%Y").year)
                            else:
                                date_return = datetime.strptime(date_raw, "%B %d,%Y").isoformat()
                        else:
                            date_return = datetime.strptime(date_raw, "%b. %d %Y").isoformat()
                    else:
                        date_return = datetime.strptime(date_raw, "%b. %d,%Y").isoformat()
                else:
                    date_return = datetime.strptime(date_raw, "%B %d, %Y").isoformat()
            else:
                date_return = datetime.strptime(date_raw, "%b. %d, %Y").isoformat()
        return date_return

    def save(self):
        dir=get_dir_ref(dir = "/Volumes/WD My Passport/LILProject/References")
        new_reference = True
        pk1_file = open(dir + "/references.pk1", 'rb')
        reference_list = pickle.load(pk1_file)
        #print(reference_list)
        pk1_file.close()

        if self.id in reference_list:
            new_reference = False
        if new_reference:
            #print("new!")
            self.write_to_file()
        else:
            #print("save to update!")
            self.update()

    def update(self):
        ref_dir = get_dir_ref(dir = "/Volumes/WD My Passport/LILProject/References")
        file_name = self.file_name
        doc = open(ref_dir + "/" + file_name +  ".json", 'r+').read()
        data = json.loads(doc)
        count = data["citation_count"]
        self.citation_count = count + 1
        #print("update!")
        self.write_to_file()

    def add_citatioin(self, citation):
        self.citations = self.citations.append(citation)

    def write_to_file(self):
        dir = get_dir_ref(dir = "/Volumes/WD My Passport/LILProject/References")
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
        json_2_b['full_cite'] = self.full_cite
        json_2_b['citation_count'] = self.citation_count
        json_out = json.dumps(json_2_b, indent=4, separators=(',', ': '))
        doc = open(dir + "/" +self.file_name +  ".json", 'w')
        doc.write(json_out)
        doc.close()

        pk1_file = open(dir + "/references.pk1",'r+b')
        reference_list = pickle.load(pk1_file)
        reference_list[self.id] = self.file_name
        pk1_file.close()
        pk1_file = open(dir + "/references.pk1",'wb')
        pickle.dump(reference_list, pk1_file, -1)
        pk1_file.close()

    def correct(self):
        if "Dictionary" in self.title:
            self.type = "Dictionary"
        if self.journal_title in ["N. Y. Times","N.Y. Times","New York Times"]:
            #todo: use NYT search api
            pass
        if self.authors == [("also","")] or self.authors  == [("Also","")]:
            self.authors = [("no_author","")]
        if self.title == "e.g.":
            self.title = self.journal_title
            self.journal_title = ""
        if self.authors == [("Note", "")]:
            self.title = "Note, " + self.title
            self.authors = [("no_author", "")]
        if self.title.lower().startswith("press release"):
            self.type="press_release"
        if self.authors[-1][1] == " See" or self.authors[-1][1] == "See":
            self.authors[-1] = (self.authors[-1][0],"")
        return(self)

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
        cite_link = {'opinion_name':self.opinion.name,'reference_name':self.reference.title,
                     'opinion_id':self.opinion_id,'reference_id':self.reference_id}
        return(cite_link)

    def update(self):
        self.opinion_id = self.opinion.id
        self.reference_id = self.reference.id
        return self

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
    cluster = OpinionCluster(id=id,opinions=opinions, name=name_short)
    #cluster = OpinionCluster(id=id,court=court,jurisdiction=jurisdiction,docket=docket,date=date,name_full=name,
                            # name=name_short,cite=citation,opinions=opinions)
    return cluster

def find_potential_citations(opinion):
    text = opinion.opinion_text
    potential_citations = ""
    matches = re.finditer(r"(([^\)]{1,100})\(([A-Za-z\d][\sA-Za-z\d\.]*\s)?([0-9]{4})\))", text)
    for match in matches:
        potential_citations = potential_citations + "\n\n" + match.group(1)
    matches = re.finditer(r"(([^\)]{1,100})\s\d+-\d+)", text)
    for match in matches:
        potential_citations = potential_citations + "\n\n" + match.group(1)
    matches = re.finditer(r"(([^\)]{1,100})\s[A-Za-z]{3}.\s\d{1,2},?\s[0-9]{3,4})", text)
    for match in matches:
        potential_citations = potential_citations + "\n\n" + match.group(1)
    return potential_citations

#Takes an opinion as input and finds citations in the text of that opinion.
#Returns a list of citations
#Also saves new corresponding references to file
#Currently looks for journal articles, newspapers, books, and similarly formatted citations
def find_citations(opinion, as_citations=False, testing=False):

    def create_citations(references, opinion):
        citations = []
        if len(references) > 0:
            for reference in references:
                citations.append(Citation(opinion,reference))
        return(citations)

    def append_reference(references, full_cite, original_cite, author, date, title, type, flag_error=False, volume="",
                         pages="", edition="", start_page="", journal_title="", volume_title=""):
        try:
            references.append(Reference(type=type, authors=author, date=date, title = title, volume_title=volume_title,
                                        original_cite=original_cite, full_cite=full_cite, journal_title=journal_title,
                                        volume=volume, pages=pages, edition=edition, start_page=start_page))
        except InvalidCitationError:
            if flag_error:
                print("Invalid citation!")
        else:
            pass
        return references

    def find_books(text, opinion):
        if testing:
            print("Looking for Books")
        references = []
        rev_text = text[::-1]

        # todo: Make sure I am actually saving mutliple author situations
        # todo: could check to see if items without pages are (unpagenated)

        #Special Pagination
        matches = re.finditer(r"(((?:\d+\*(?:(?:-)|(?:\s\u2014\s)))?\d+)\*\s?([\w\s']+),([\w]+)\s(\.[A-Z])\s(\d+)?)",
                              rev_text)
        if matches:
            for match in matches:
                full = match.group(1)
                original = match.group(1)[::-1]
                date = "n.d."
                if match.group(5):
                    authors = [(match.group(4)[::-1],match.group(5)[::-1])]
                else:
                    authors = [(match.group(4)[::-1],"")]
                title = match.group(3)[::-1]
                pages = match.group(2)[::-1]
                if match.group(6):
                    vol = match.group(6)[::-1]
                else:
                    vol = ""
                type = "book"
                if title.strip() != "at":
                    references = append_reference(references=references, flag_error=print_errors, type=type, title=title,
                                              date=date, volume=vol,
                                              author=authors, pages=pages, full_cite=full,
                                              original_cite=original)

        #See Generally Books
        matches = re.finditer(r"(\)(?:\.de )?(\d{3,4})\s*([^\(]*)\(\s+([a-z][\w\s':,]+[A-Z])\s*,([\w]+[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?)?\s*(?:(?:(?:&\s)|(?:dna\s)),?([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?)?\s*)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(\d+)?)",
            rev_text)
        if matches:
            for match in matches:
                date = match.group(2)[::-1]

                if match.group(6):
                    authors = [(match.group(5)[::-1],match.group(6)[::-1])]
                else:
                    authors = [(match.group(5)[::-1],"")]
                if match.group(8):
                    if match.group(9):
                        authors = [(match.group(8)[::-1], match.group(9)[::-1])] + authors
                    else:
                        authors = [(match.group(8)[::-1],"")] + authors
                if match.group(11):
                    if match.group(12):
                        authors = [(match.group(11)[::-1], match.group(12)[::-1])] + authors
                    else:
                        authors = [(match.group(11)[::-1],"")] + authors
                if match.group(14):
                    if match.group(15):
                        authors = [(match.group(14)[::-1], match.group(15)[::-1])] + authors
                    else:
                        authors = [(match.group(14)[::-1],"")] + authors
                if match.group(17):
                    if match.group(18):
                        authors = [(match.group(17)[::-1], match.group(18)[::-1])] + authors
                    else:
                        authors = [(match.group(17)[::-1],"")] + authors
                if match.group(20):
                    if match.group(21):
                        authors = [(match.group(20)[::-1], match.group(21)[::-1])] + authors
                    else:
                        authors = [(match.group(20)[::-1],"")] + authors

                type = "book"
                full = match.group(1)
                original = match.group(1)[::-1]
                vol = ""
                if match.group(23):
                    vol = match.group(23)[::-1]
                title = match.group(4)[::-1]
                edition = ""
                if match.group(3):
                    edition = match.group(3)[::-1]

                references = append_reference(references=references, flag_error=print_errors, type=type, title=title, date=date,
                                              author=authors, volume=vol, full_cite=full, edition=edition, original_cite=original)

        #Complex Pagination 1
        matches = re.finditer(r"(\)(?:\.de )?(\d{3,4})\s*([^\(]*)\(\s*([\w\-\.]+\.[A-Z])\s+([\w\s':,]+[A-Z])\s*,([\w]+[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?)?\s*(?:(?:(?:&\s)|(?:dna\s)),?([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?)?\s*)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(\d+)?)",
                              rev_text)
        for match in matches:
            date = match.group(2)[::-1]

            if match.group(7):
                authors = [(match.group(6)[::-1], match.group(7)[::-1])]
            else:
                authors = [(match.group(6)[::-1], "")]
            if match.group(9):
                if match.group(10):
                    authors = [(match.group(9)[::-1], match.group(10)[::-1])] + authors
                else:
                    authors = [(match.group(9)[::-1], "")] + authors
            if match.group(12):
                if match.group(13):
                    authors = [(match.group(12)[::-1], match.group(13)[::-1])] + authors
                else:
                    authors = [(match.group(12)[::-1], "")] + authors
            if match.group(15):
                if match.group(16):
                    authors = [(match.group(15)[::-1], match.group(16)[::-1])] + authors
                else:
                    authors = [(match.group(15)[::-1], "")] + authors
            if match.group(18):
                if match.group(19):
                    authors = [(match.group(18)[::-1], match.group(19)[::-1])] + authors
                else:
                    authors = [(match.group(18)[::-1], "")] + authors
            if match.group(21):
                if match.group(22):
                    authors = [(match.group(21)[::-1], match.group(22)[::-1])] + authors
                else:
                    authors = [(match.group(21)[::-1], "")] + authors

            type = "book"
            full = match.group(1)
            original = match.group(1)[::-1]
            vol = ""
            if match.group(24):
                vol = match.group(24)[::-1]
            pages = ""
            if match.group(4):
                pages = match.group(4)[::-1]
            title = match.group(5)[::-1]
            edition = ""
            if match.group(3):
                edition = match.group(3)[::-1]
            if testing:
                print(original)
            references = append_reference(references=references, flag_error=print_errors, type=type, title=title,
                                          date=date,
                                          author=authors, volume=vol, pages=pages, full_cite=full, edition=edition,
                                          original_cite=original)

        #Basic Multivolume books
        matches = re.finditer(r"(\)(?:\.de )?(\d{3,4})\s*([^\(]*)\(\s*((?:(?:\w+ ,)?(?:\w+ ,)?(?:\w+ ,)?\w+ \.nn?(?: dna)? ,)?(?:\d+(?:-\d+)?)?\s*(?:,\d+(?:-\d+)?)?\s*(?:,\d+(?:-\d+)?)?\s*(?:,\d+(?:-\d+)?)?\s*(?:,\d+(?:-\d+)?)?)\s+([\w\s':,]+[A-Z])\s*,([\w]+[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?)?\s*(?:(?:(?:&\s)|(?:dna\s)),?([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?)?\s*)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(\d+)?)",
                              rev_text)
        if matches:
            for match in matches:
                date = match.group(2)[::-1]

                if match.group(7):
                    authors = [(match.group(6)[::-1],match.group(7)[::-1])]
                else:
                    authors = [(match.group(6)[::-1],"")]
                if match.group(9):
                    if match.group(10):
                        authors = [(match.group(9)[::-1], match.group(10)[::-1])] + authors
                    else:
                        authors = [(match.group(9)[::-1],"")] + authors
                if match.group(12):
                    if match.group(13):
                        authors = [(match.group(12)[::-1], match.group(13)[::-1])] + authors
                    else:
                        authors = [(match.group(12)[::-1],"")] + authors
                if match.group(15):
                    if match.group(16):
                        authors = [(match.group(15)[::-1], match.group(16)[::-1])] + authors
                    else:
                        authors = [(match.group(15)[::-1],"")] + authors
                if match.group(18):
                    if match.group(19):
                        authors = [(match.group(18)[::-1], match.group(19)[::-1])] + authors
                    else:
                        authors = [(match.group(18)[::-1],"")] + authors
                if match.group(21):
                    if match.group(22):
                        authors = [(match.group(21)[::-1], match.group(22)[::-1])] + authors
                    else:
                        authors = [(match.group(21)[::-1],"")] + authors

                type = "book"
                full = match.group(1)
                original = match.group(1)[::-1]
                vol = ""
                if match.group(24):
                    vol = match.group(24)[::-1]
                pages = ""
                if match.group(4):
                    pages = match.group(4)[::-1]
                title = match.group(5)[::-1]
                edition = ""
                if match.group(3):
                    edition = match.group(3)[::-1]
                references = append_reference(references=references, flag_error=print_errors, type=type, title=title, date=date,
                                              author=authors, volume=vol, pages=pages, full_cite=full, edition=edition, original_cite=original)

        #Book with sections
        matches = re.finditer(r"(\)(?:\.de )?(\d{3,4})\s*([^\(]*)\( ((?:\d+ .nn? ?(?:dna )?,)?(?:(?:(?:\d+ )?seton dna ,)?[\d\.-]+ (?:ot [\d\.-]+ )?.p?p ,)?(?:[\w'\.\[\]]+ ?¶ )?(?:\d+ ,)?(?:\d+ ,)?(?:\d+ ,)?(?:\d+ ,)?(?:\d+ ,)?(?:,?[\w\-\:\.\[\]\(\)]+ ?§§?)(?: ?,\d+ \.hc)?)\s*([\w\s':,]+[A-Z])\s*,([\w]+[A-Z0-9])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?)?\s*(?:(?:(?:&\s)|(?:dna\s)),?([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?)?\s*)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(\d+)?)",
                              rev_text)
        if matches:
            for match in matches:
                date = match.group(2)[::-1]

                if match.group(7):
                    authors = [(match.group(6)[::-1], match.group(7)[::-1])]
                else:
                    authors = [(match.group(6)[::-1], "")]
                if match.group(9):
                    if match.group(10):
                        authors = [(match.group(9)[::-1], match.group(10)[::-1])] + authors
                    else:
                        authors = [(match.group(9)[::-1], "")] + authors
                if match.group(12):
                    if match.group(13):
                        authors = [(match.group(12)[::-1], match.group(13)[::-1])] + authors
                    else:
                        authors = [(match.group(12)[::-1], "")] + authors
                if match.group(15):
                    if match.group(16):
                        authors = [(match.group(15)[::-1], match.group(16)[::-1])] + authors
                    else:
                        authors = [(match.group(15)[::-1], "")] + authors
                if match.group(18):
                    if match.group(19):
                        authors = [(match.group(18)[::-1], match.group(19)[::-1])] + authors
                    else:
                        authors = [(match.group(18)[::-1], "")] + authors
                if match.group(21):
                    if match.group(22):
                        authors = [(match.group(21)[::-1], match.group(22)[::-1])] + authors
                    else:
                        authors = [(match.group(21)[::-1], "")] + authors

                type = "book"
                full = match.group(1)
                original = match.group(1)[::-1]
                vol = ""
                if match.group(24):
                    vol = match.group(24)[::-1]
                pages = ""
                if match.group(4):
                    pages = match.group(4)[::-1]
                title = match.group(5)[::-1]
                edition = ""
                if match.group(3):
                    edition = match.group(3)[::-1]
                references = append_reference(references=references, flag_error=print_errors, type=type, title=title,
                                              date=date,
                                              author=authors, volume=vol, pages=pages, full_cite=full, edition=edition,
                                              original_cite=original)

        #Books with Paragraphs
        matches = re.finditer(r"(\)(?:\.de )?(\d{3,4})\s*([^\(]*)\( ((?:\w+ .nn? ?(?:dna )?,)?(?:(?:(?:\d+ )?seton dna ,)?[\d\.-]+ (?:ot [\d\.-]+ )?.p?p ,)?(?:[\w'\.\[\]]+ ?¶ ?)(?:-\d+)?(?: ?,\d+ \.hc)?)\s*([\w\s':,]+[A-Z])\s*,([\w]+[A-Z0-9])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?)?\s*(?:(?:(?:&\s)|(?:dna\s)),?([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?)?\s*)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(\d+)?)",
                              rev_text)
        if matches:
            for match in matches:
                date = match.group(2)[::-1]

                if match.group(7):
                    authors = [(match.group(6)[::-1], match.group(7)[::-1])]
                else:
                    authors = [(match.group(6)[::-1], "")]
                if match.group(9):
                    if match.group(10):
                        authors = [(match.group(9)[::-1], match.group(10)[::-1])] + authors
                    else:
                        authors = [(match.group(9)[::-1], "")] + authors
                if match.group(12):
                    if match.group(13):
                        authors = [(match.group(12)[::-1], match.group(13)[::-1])] + authors
                    else:
                        authors = [(match.group(12)[::-1], "")] + authors
                if match.group(15):
                    if match.group(16):
                        authors = [(match.group(15)[::-1], match.group(16)[::-1])] + authors
                    else:
                        authors = [(match.group(15)[::-1], "")] + authors
                if match.group(18):
                    if match.group(19):
                        authors = [(match.group(18)[::-1], match.group(19)[::-1])] + authors
                    else:
                        authors = [(match.group(18)[::-1], "")] + authors
                if match.group(21):
                    if match.group(22):
                        authors = [(match.group(21)[::-1], match.group(22)[::-1])] + authors
                    else:
                        authors = [(match.group(21)[::-1], "")] + authors

                type = "book"
                full = match.group(1)
                original = match.group(1)[::-1]
                vol = ""
                if match.group(24):
                    vol = match.group(24)[::-1]
                pages = ""
                if match.group(4):
                    pages = match.group(4)[::-1]
                title = match.group(5)[::-1]
                edition = ""
                if match.group(3):
                    edition = match.group(3)[::-1]
                references = append_reference(references=references, flag_error=print_errors, type=type, title=title,
                                              date=date,
                                              author=authors, volume=vol, pages=pages, full_cite=full, edition=edition,
                                              original_cite=original)

        #No author books with sections
        matches = re.finditer(r"(\)(?:\.de )?(\d{3,4})\s*([^\(]*)\( ((?:\d+ .nn? ?(?:dna )?,)?(?:(?:(?:\d+ )?seton dna ,)?[\d\.-]+ (?:ot [\d\.-]+ )?.p?p ,)?(?:[\w'\.\[\]]+ ?¶ )?(?:\d+ ,)?(?:\d+ ,)?(?:\d+ ,)?(?:\d+ ,)?(?:\d+ ,)?(?:,?[\w\-\:\.\[\]\(\)]+ ?§§?)(?: ?,\d+ \.hc)?)\s*([\w\s':,]+[A-Z])\s?(?:(?:[.;\"])|ee[Ss]|arpu[Ss]|osla ee[Ss]|eht ni|eht htiw)(?!([a-z]{1,2})?[A-Z])(?![A-Za-z]+\s\d))", rev_text)
        if matches:
            for match in matches:
                full = match.group(1)
                original = match.group(1)[::-1]
                date = match.group(2)[::-1]
                type="book"
                author=[("no_author","")]
                title = match.group(5)[::-1]
                vol = ""
                if match.group(6):
                    vol = match.group(6)[::-1]
                pages = ""
                if match.group(4):
                    pages = match.group(4)[::-1]
                edition = ""
                if match.group(3):
                    edition = match.group(3)[::-1]

                references = append_reference(references=references, flag_error=print_errors, type=type, title=title, date=date,
                                              author=author, volume=vol, pages=pages, full_cite=full, edition=edition, original_cite=original)

        #No author book with paragraphs
        matches = re.finditer(r"(\)(?:\.de )?(\d{3,4})\s*([^\(]*)\( ((?:\w+ .nn? ?(?:dna )?,)?(?:(?:(?:\d+ )?seton dna ,)?[\d\.-]+ (?:ot [\d\.-]+ )?.p?p ,)?(?:[\w'\.\[\]]+ ?¶ ?)(?:-\d+)?(?: ?,\d+ \.hc)?)\s*([\w\s':,]+[A-Z]) (\d+)?)\s?(?:(?:[.;\"])|ee[Ss]|arpu[Ss]|osla ee[Ss]|eht ni|eht htiw)(?!([a-z]{1,2})?[A-Z])(?![A-Za-z]+\s\d)", rev_text)
        if matches:
            for match in matches:
                full = match.group(1)
                original = match.group(1)[::-1]
                date = match.group(2)[::-1]
                type="book"
                author=[("no_author","")]
                title = match.group(5)[::-1]
                vol = ""
                if match.group(6):
                    vol = match.group(6)[::-1]
                pages = ""
                if match.group(4):
                    pages = match.group(4)[::-1]
                edition = ""
                if match.group(3):
                    edition = match.group(3)[::-1]

                references = append_reference(references=references, flag_error=print_errors, type=type, title=title, date=date,
                                              author=author, volume=vol, pages=pages, full_cite=full, edition=edition, original_cite=original)

        #Books with 'pp.'s
        matches = re.finditer(r"(\)(?:\.de )?(\d{3,4})\s*([^\(]*)\(\s*((?:(?:\w+ ,)?(?:\w+ ,)?(?:\w+ ,)?\w+ \.nn?(?: dna)? ,)?(?:\d+(?:-\d+)?)?\s*(?:,\d+(?:-\d+)?)?\s*(?:,\d+(?:-\d+)?)?\s*(?:,\d+(?:-\d+)?)?\s*(?:,\d+(?:-\d+)?)?\s+.p?p\s,)([\w\s':,\.-]+[A-Z])\s*,([\w]+[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?)?\s*(?:(?:(?:&\s)|(?:dna\s)),?([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?)?\s*)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(\d+)?)", rev_text)
        if matches:
            for match in matches:
                date = match.group(2)[::-1]

                if match.group(7):
                    authors = [(match.group(6)[::-1],match.group(7)[::-1])]
                else:
                    authors = [(match.group(6)[::-1],"")]
                if match.group(9):
                    if match.group(10):
                        authors = [(match.group(9)[::-1], match.group(10)[::-1])] + authors
                    else:
                        authors = [(match.group(9)[::-1],"")] + authors
                if match.group(12):
                    if match.group(13):
                        authors = [(match.group(12)[::-1], match.group(13)[::-1])] + authors
                    else:
                        authors = [(match.group(12)[::-1],"")] + authors
                if match.group(15):
                    if match.group(16):
                        authors = [(match.group(15)[::-1], match.group(16)[::-1])] + authors
                    else:
                        authors = [(match.group(15)[::-1],"")] + authors
                if match.group(18):
                    if match.group(19):
                        authors = [(match.group(18)[::-1], match.group(19)[::-1])] + authors
                    else:
                        authors = [(match.group(18)[::-1],"")] + authors
                if match.group(21):
                    if match.group(22):
                        authors = [(match.group(21)[::-1], match.group(22)[::-1])] + authors
                    else:
                        authors = [(match.group(21)[::-1],"")] + authors

                type = "book"
                full = match.group(1)
                original = match.group(1)[::-1]
                vol = ""
                if match.group(24):
                    vol = match.group(24)[::-1]
                pages = ""
                if match.group(4):
                    pages = match.group(4)[::-1]
                title = match.group(5)[::-1]
                edition = ""
                if match.group(3):
                    edition = match.group(3)[::-1]
                #if testing:
                #    print(original)
                references = append_reference(references=references, flag_error=print_errors, type=type, title=title, date=date,
                                              author=authors, volume=vol, pages=pages, full_cite=full, edition=edition, original_cite=original)

        #Books with chapters
        matches = re.finditer(r"(\)(?:\.de )?(\d{3,4})\s*([^\(]*)\(\s*(?:([\d-]+ .p?p ,)?[\w]+ .hc ,)([\w\s':,\.]+[A-Z0-9])\s*,(([\w]+[A-Z])\s*([\.\s\w]*[A-Z])?)\s*(?:(?:(?:&\s)|(?:dna\s)),?([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?)?\s*)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(\d+)?)",
                            rev_text)
        for match in matches:
            date = match.group(2)[::-1]
            if match.group(8):
                authors = [(match.group(7)[::-1], match.group(8)[::-1])]
            else:
                authors = [(match.group(7)[::-1], "")]
            if match.group(11):
                if match.group(10):
                    authors = [(match.group(10)[::-1], match.group(11)[::-1])] + authors
                else:
                    authors = [(match.group(10)[::-1], "")] + authors
            if match.group(14):
                if match.group(13):
                    authors = [(match.group(13)[::-1], match.group(14)[::-1])] + authors
                else:
                    authors = [(match.group(13)[::-1], "")] + authors
            if match.group(17):
                if match.group(16):
                    authors = [(match.group(16)[::-1], match.group(17)[::-1])] + authors
                else:
                    authors = [(match.group(16)[::-1], "")] + authors
            if match.group(20):
                if match.group(19):
                    authors = [(match.group(19)[::-1], match.group(20)[::-1])] + authors
                else:
                    authors = [(match.group(19)[::-1], "")] + authors
            if match.group(23):
                if match.group(23):
                    authors = [(match.group(22)[::-1], match.group(23)[::-1])] + authors
                else:
                    authors = [(match.group(22)[::-1], "")] + authors

            type = "book"
            full = match.group(1)
            original = match.group(1)[::-1]
            vol = ""
            if match.group(24):
                vol = match.group(24)[::-1]
            pages = ""
            if match.group(4):
                pages = match.group(4)[::-1]
            title = match.group(5)[::-1]
            edition = ""
            if match.group(3):
                edition = match.group(3)[::-1]
            #if testing:
                #print(original)
            references = append_reference(references=references, flag_error=print_errors, type=type, title=title,
                                          date=date,
                                          author=authors, volume=vol, pages=pages, full_cite=full, edition=edition,
                                          original_cite=original)
        
        #Book Section
        hereinafters = re.finditer(r"(, in ([,A-Za-z\s]+) ([\s\d,-]+) \(([\sA-Za-z\.\d&,]*?)([0-9]{4})\) \(hereinafter ([\w\s]+)\))", text)
        herein = {}
        for hereinafter in hereinafters:
            author = [("No_Author (Edited Volume)",)]
            type="Book"
            full = match.group(1)
            original = match.group(1)
            date = match.group(5)
            edition = ""
            title = match.group(2)
            pages = match.group(3)
            if match.group(4):
                edition = match.group(4)
            herein[match.group(5)[::-1]] = [title, edition, date]
            if testing:
                print(original)
            references = append_reference(references=references, flag_error=print_errors, type=type, title=title, date=date,
                                      author=author, full_cite=full, edition=edition,
                                      original_cite=original)

        matches = re.finditer(r"(\)(?:\.de )?(\d{3,4})\s*([^\(]*)\(\s*((?:(?:\w+ ,)?(?:\w+ ,)?(?:\w+ ,)?\w+ \.nn?(?: dna)? ,)?(?:\d+(?:-\d+)?)?\s*(?:,\d+(?:-\d+)?)?\s*(?:,\d+(?:-\d+)?)?\s*(?:,\d+(?:-\d+)?)?\s*(?:,\d+(?:-\d+)?)?)\s+([\.\w\s':,]+[A-Z]) ni ,([\.\w\s':,]+[A-Z])\s*,([\w]+[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?)?\s*(?:(?:(?:&\s)|(?:dna\s)),?([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?)?\s*)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(\d+)?)",
                              rev_text)
        for match in matches:
            type="Book Section"
            full = match.group(1)
            original = match.group(1)[::-1]
            pages = match.group(4)[::-1]
            title = match.group(6)[::-1]
            edition = ""
            volume_title = match.group(5)[::-1]
            date = match.group(2)[::-1]
            vol = ""
            if match.group(25):
                vol = match.group(25)[::-1]
            if match.group(3):
                edition = match.group(3)[::-1]
            if match.group(8):
                authors = [(match.group(7)[::-1], match.group(8)[::-1])]
            else:
                authors = [(match.group(7)[::-1], "")]
            if match.group(11):
                if match.group(10):
                    authors = [(match.group(10)[::-1], match.group(11)[::-1])] + authors
                else:
                    authors = [(match.group(10)[::-1], "")] + authors
            if match.group(14):
                if match.group(13):
                    authors = [(match.group(13)[::-1], match.group(14)[::-1])] + authors
                else:
                    authors = [(match.group(13)[::-1], "")] + authors
            if match.group(17):
                if match.group(16):
                    authors = [(match.group(16)[::-1], match.group(17)[::-1])] + authors
                else:
                    authors = [(match.group(16)[::-1], "")] + authors
            if match.group(20):
                if match.group(19):
                    authors = [(match.group(19)[::-1], match.group(20)[::-1])] + authors
                else:
                    authors = [(match.group(19)[::-1], "")] + authors
            if match.group(23):
                if match.group(23):
                    authors = [(match.group(22)[::-1], match.group(23)[::-1])] + authors
                else:
                    authors = [(match.group(22)[::-1], "")] + authors
            if testing:
                print(original)
            references = append_reference(references=references, flag_error=print_errors, type=type, title=title,
                                              date=date, volume_title=volume_title, volume=vol, pages=pages,
                                              author=authors, full_cite=full, edition=edition,
                                              original_cite=original)
        matches = re.finditer(r"(((?:(?:\w+ ,)?(?:\w+ ,)?(?:\w+ ,)?\w+ \.nn?(?: dna)? ,)?(?:\d+(?:-\d+)?)?\s*(?:,\d+(?:-\d+)?)?\s*(?:,\d+(?:-\d+)?)?\s*(?:,\d+(?:-\d+)?)?\s*(?:,\d+(?:-\d+)?)?)\s+([\.\w\s':,]+[A-Z]) ni ([\.\w\s':,]+[A-Z])\s*,([\w]+[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?)?\s*(?:(?:(?:&\s)|(?:dna\s)),?([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?)?\s*)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(\d+)?)",
                              rev_text)
        for match in matches:
            if match.group(3) in herein:
                herein.append[match.group(3)[::-1]] = [title, edition, date]

                type = "Book Section"
                full = match.group(1)
                original = match.group(1)[::-1]
                pages = match.group(2)[::-1]
                title = match.group(4)[::-1]
                edition = herein[match.group(3)][1]
                volume_title = herein[match.group(3)][0]
                date = herein[match.group(3)][2]
                vol = ""
                if match.group(23):
                    vol = match.group(23)[::-1]
                if match.group(6):
                    authors = [(match.group(5)[::-1], match.group(6)[::-1])]
                else:
                    authors = [(match.group(5)[::-1], "")]
                if match.group(8):
                    if match.group(9):
                        authors = [(match.group(8)[::-1], match.group(9)[::-1])] + authors
                    else:
                        authors = [(match.group(8)[::-1], "")] + authors
                if match.group(11):
                    if match.group(12):
                        authors = [(match.group(11)[::-1], match.group(12)[::-1])] + authors
                    else:
                        authors = [(match.group(11)[::-1], "")] + authors
                if match.group(14):
                    if match.group(15):
                        authors = [(match.group(14)[::-1], match.group(15)[::-1])] + authors
                    else:
                        authors = [(match.group(14)[::-1], "")] + authors
                if match.group(17):
                    if match.group(18):
                        authors = [(match.group(17)[::-1], match.group(18)[::-1])] + authors
                    else:
                        authors = [(match.group(17)[::-1], "")] + authors
                if match.group(20):
                    if match.group(21):
                        authors = [(match.group(20)[::-1], match.group(21)[::-1])] + authors
                    else:
                        authors = [(match.group(20)[::-1], "")] + authors
                if testing:
                    print(original)
                    print(herein)
                references = append_reference(references=references, flag_error=print_errors, type=type, title=title,
                                              date=date, volume_title=volume_title, volume=vol, pages=pages,
                                              author=authors, full_cite=full, edition=edition,
                                              original_cite=original)
        
        #No author general books
        matches = re.finditer(r"(\)(?:\.de )?(\d{3,4})\s*([^\(]*)\(\s+([a-z][\w\s':]+[A-Z])\s?(\d+)?)\s?(?:(?:[.;\"])|ee[Ss]|arpu[Ss]|osla ee[Ss]|eht ni|eht htiw)(?!([a-z]{1,2})?[A-Z])(?![A-Za-z]+\s\d)",
                              rev_text)
        if matches:
            for match in matches:
                full = match.group(1)
                original = match.group(1)[::-1]
                date = match.group(2)[::-1]
                type = "book"
                author = [("no_author", "")]
                title = match.group(4)[::-1]
                edition = ""
                if match.group(3):
                    edition = match.group(3)[::-1]
                if edition != "in":
                    references = append_reference(references=references, flag_error=print_errors, type=type, title=title, date=date,
                                      author=author, full_cite=full, edition=edition,
                                      original_cite=original)

        #No author books
        matches = re.finditer(r"(\)(?:\.de )?(\d{3,4})\s*([^\(]*)\(\s+?(\d+(?:-\d+)?)?\s+([\w\s':]+?[A-Z])\s?(\d+)?)\s?(?:(?:[.;\"])|ee[Ss]|arpu[Ss]|osla ee[Ss]|eht ni|eht htiw)(?!([a-z]{1,2})?[A-Z])(?![A-Za-z]+\s\d)",
                              rev_text)
        if matches:
            for match in matches:
                full = match.group(1)
                original = match.group(1)[::-1]
                date = match.group(2)[::-1]
                type="book"
                author=[("no_author","")]
                title = match.group(5)[::-1]
                vol = ""
                if match.group(6):
                    vol = match.group(6)[::-1]
                pages = ""
                if match.group(4):
                    pages = match.group(4)[::-1]
                edition = ""
                if match.group(3):
                    edition = match.group(3)[::-1]

                references = append_reference(references=references, flag_error=print_errors, type=type, title=title, date=date,
                                              author=author, volume=vol, pages=pages, full_cite=full, edition=edition, original_cite=original)

        #Instituional Authors
        matches = re.finditer(r"(\)(?:\.de )?(\d{3,4})\s*([^\(]*)\(\s*((?:(?:\d+ ,)?(?:\d+ ,)?(?:\d+ ,)?\d+ \.nn?(?: dna)? ,)?(?:\d+(?:-\d+)?)?\s*(?:,\d+(?:-\d+)?)?\s*(?:,\d+(?:-\d+)?)?\s*(?:,\d+(?:-\d+)?)?\s*(?:,\d+(?:-\d+)?)?)\s+([\w\s':,]+[A-Z])\s*,([\w\s\.]+[A-Z] [\w\s\.]+[A-Z] [\w\s\.]+[A-Z] [\w\s\.]+[A-Z]))(\s\d+)?",
                              rev_text)
        if matches:
            for match in matches:
                full = match.group(1)
                original = match.group(1)[::-1]
                date = match.group(2)[::-1]
                type = "Instituional Report"
                author_temp = match.group(6)[::-1]
                if author_temp.strip().endswith(" eeS"):
                    author_temp = author_temp.strip()
                    author_temp = author_temp.rstrip("Se ")
                author = [(author_temp, "")]
                title = match.group(5)[::-1]
                vol = ""
                if match.group(7):
                    vol = match.group(7)[::-1]
                pages = ""
                if match.group(4):
                    pages = match.group(4)[::-1]
                edition = ""
                if match.group(3):
                    edition = match.group(3)[::-1]
                references = append_reference(references=references, flag_error=print_errors, type=type, title=title,
                                              date=date,
                                              author=author, volume=vol, pages=pages, full_cite=full, edition=edition,
                                              original_cite=original)

        #The Federalist
        matches = re.finditer(r"((The Federalist No. \d+,) (pp?\. \d+(?:\-\d+)?) \(([\w.\s]+) (\d{4})\) \(([\s\w.]+ )?([\s\w]+)\))",text)
        if matches:
            for match in matches:
                full = match.group(1)
                original=match.group(1)
                title = match.group(2)
                type = "book"
                volume = "The Federalist Papers"
                date=match.group(5)
                edition = ""
                if match.group(4):
                    edition = match.group(4)
                if match.group(6):
                    author = [(match.group(7), match.group(6))]
                else:
                    author = [(match.group(7), "")]

                references = append_reference(references=references, flag_error=print_errors, type=type,
                                              title=title, date=date,
                                              author=author, volume_title=volume, full_cite=full,
                                              edition=edition, original_cite=original)

        return create_citations(references,opinion)

    def find_news(text, opinion):
        if testing:
            print("Looking for News")
        references = []
        rev_text = text[::-1]

        print(opinion.name)
        matches = re.findall(r"([.;]((?:\d+ )?\w+ \.p?p) ,(\d{4} ,\d+ .?\w{3,4}(?:\-\d+ .?\w{3,4})?) ,((?:\s?[\w\.]+[A-Z])+)(?: [,?]([\w\s'’\–]+[A-Z]))?(?: ,(\w+[A-Z]( & \w+[A-Z])?))?)", rev_text)
        if testing:
            print("search complete")
        if matches and testing:
            print("first match: " + matches[0][0])
        for match in matches:
            print(match)
            if testing:
                print(match)
                print("New News Match!")
            full = match[0]
            original = match[0]
            pages = "not_specified"
            if match[1]:
                pages = match[1]
            if match[4]:
                title = match[4].strip()[::-1]
            else:
                title = "untitled (" + pages + ")"
            vol = match[3][::-1]
            date = match[2][::-1]
            type = "book"
            if match[5]:
                author = [(match[5][::-1],"")]
            else:
                author_temp = "no_author_(" + vol +  ")"
                author = [(author_temp,"")]
            if testing:
                print(original)
            references = append_reference(references=references, flag_error=print_errors, type=type,
                                          title=title, date=date,
                                          author=author, volume_title=vol, full_cite=full, original_cite=original)
            if testing:
                print("done with matches")
        return create_citations(references, opinion)

    def find_journals(text, opinion):
        if testing:
            print("Looking for Journals")
        references=[]
        rev_txt = text[::-1]

        matches = re.finditer(r"(\)(\d{3,4})\s*([^\(]*)\(\s*?((?:(?:\d+ ,)?(?:\d+ ,)?(?:\d+ ,)?\d+ \.nn?(?: dna)? ,)?(?:\d+(?:-\d+)?)?\s*(?:,\d+(?:-\d+)?)?\s*(?:,\d+(?:-\d+)?)?\s*(?:,\d+(?:-\d+)?)?\s*(?:,\d+(?:-\d+)?)?\s*,)?(\d+)\s*([\w\s':,\.\"\(\)?!&]+[A-Z])\s*(\d+)\s*,([\w\s':,\"\\\.?!\u2014]+[A-Z\"])\s*,([\w]+[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?)?\s*(?:(?:(?:&\s)|(?:dna\s)),?([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?)?\s*)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?)",
                              rev_txt)
        if matches:
            for match in matches:
                type = "journal"
                full = match.group(1)
                original = match.group(1)[::-1]
                date = match.group(2)[::-1]
                start_page = match.group(5)[::-1]
                journal_title = match.group(6)[::-1]
                vol = match.group(7)[::-1]
                title = match.group(8)[::-1]

                if match.group(10):
                    authors = [(match.group(9)[::-1], match.group(10)[::-1])]
                else:
                    authors = [(match.group(9)[::-1], "")]
                if match.group(12):
                    if match.group(13):
                        authors = [(match.group(12)[::-1], match.group(13)[::-1])] + authors
                    else:
                        authors = [(match.group(12)[::-1], "")] + authors
                if match.group(15):
                    if match.group(16):
                        authors = [(match.group(15)[::-1], match.group(16)[::-1])] + authors
                    else:
                        authors = [(match.group(15)[::-1], "")] + authors
                if match.group(18):
                    if match.group(19):
                        authors = [(match.group(18)[::-1], match.group(19)[::-1])] + authors
                    else:
                        authors = [(match.group(18)[::-1], "")] + authors
                if match.group(21):
                    if match.group(22):
                        authors = [(match.group(21)[::-1], match.group(22)[::-1])] + authors
                    else:
                        authors = [(match.group(21)[::-1], "")] + authors
                if match.group(24):
                    if match.group(25):
                        authors = [(match.group(24)[::-1], match.group(25)[::-1])] + authors
                    else:
                        authors = [(match.group(24)[::-1], "")] + authors

                pages = ""
                if match.group(4):
                    pages = match.group(4)[::-1]
                edition = ""
                if match.group(3):
                    edition = match.group(3)[::-1]
                references = append_reference(references=references, flag_error=print_errors, type=type, title=title,
                                              date=date, start_page=start_page, journal_title=journal_title,
                                              author=authors, volume=vol, pages=pages, full_cite=full, edition=edition,
                                              original_cite=original)

            #Year as volume
            matches = re.finditer(r"([;.,](\d+(?:(?:(?:\d+ ,)?(?:\d+ ,)?(?:\d+ ,)?\d+ \.nn?(?: dna)? ,)?(?:\d+(?:-\d+)?)?\s*(?:,\d+(?:-\d+)?)?\s*(?:,\d+(?:-\d+)?)?\s*(?:,\d+(?:-\d+)?)?\s*(?:,\d+(?:-\d+)?)?)) ([.\w\s]+) (\d{4}) ,([\w\s:]+) ,([\w]+[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?)?\s*(?:(?:(?:&\s)|(?:dna\s)),?([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?)?\s*)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?(?:,([\w]*[A-Z])\s*(\.?[\w]*[A-Z]\s*(\.?[\w]*[A-Z])?\s*)?)?)",
                                  rev_txt)
            if matches:
                for match in matches:
                    type = "Journal"
                    full = match.group(1)
                    original = match.group(1)[::-1]
                    date = match.group(4)[::-1]
                    start_page = match.group(2)[::-1]
                    vol = match.group(4)[::-1]
                    title = match.group(5)[::-1]
                    journal_title = match.group(3)[::-1]
                    if match.group(7):
                        authors = [(match.group(6)[::-1], match.group(7)[::-1])]
                    else:
                        authors = [(match.group(6)[::-1], "")]
                    if match.group(10):
                        if match.group(11):
                            authors = [(match.group(10)[::-1], match.group(11)[::-1])] + authors
                        else:
                            authors = [(match.group(10)[::-1], "")] + authors
                    if match.group(13):
                        if match.group(14):
                            authors = [(match.group(13)[::-1], match.group(14)[::-1])] + authors
                        else:
                            authors = [(match.group(13)[::-1], "")] + authors
                    if match.group(16):
                        if match.group(17):
                            authors = [(match.group(16)[::-1], match.group(17)[::-1])] + authors
                        else:
                            authors = [(match.group(16)[::-1], "")] + authors
                    if match.group(19):
                        if match.group(20):
                            authors = [(match.group(19)[::-1], match.group(20)[::-1])] + authors
                        else:
                            authors = [(match.group(19)[::-1], "")] + authors
                    if match.group(22):
                        if match.group(23):
                            authors = [(match.group(22)[::-1], match.group(23)[::-1])] + authors
                        else:
                            authors = [(match.group(22)[::-1], "")] + authors
                    references = append_reference(references=references, flag_error=print_errors, type=type, title=title,
                                              date=date, start_page=start_page, journal_title=journal_title,
                                              author=authors, volume=vol, pages=start_page, full_cite=full,
                                              original_cite=original)

            #Harvard Law Supreme Court Term
            matches = re.finditer(r"((The Supreme Court, \d+ Term), (\d+) Harv. L. Rev. (\d+), ([\w\s,-]+) \((\d+)\))", text)
            for match in matches:
                type = "jorunal"
                full = match.group(1)
                original = match.group(1)
                date = match.group(6)
                author = [("No_Author","")]
                title = match.group(2)
                vol = match.group(3)
                start_page = match.group(4)
                pages = match.group(5)
                journal_title = "Harvard Law Review"
                references = append_reference(references=references, flag_error=print_errors, type=type,
                                          title=title, pages=pages,
                                          date=date, start_page=start_page, journal_title=journal_title,
                                          author=author, volume=vol, full_cite=full,
                                          original_cite=original)

            #Special Case
            matches = re.finditer(r"([;.](\d+) ([\w\s.]+) (\d{4}) ,([\w\s]+)\s?(?:(?:[.;\"])|ee[Ss]|arpu[Ss]|osla ee[Ss]|eht ni|eht htiw)(?!([a-z]{1,2})?[A-Z])(?![A-Za-z]+\s\d))",
                                  rev_txt)
            if matches:
                for match in matches:
                    type = "journal"
                    full = match.group(1)
                    original = match.group(1)[::-1]
                    date = match.group(4)[::-1]
                    start_page = match.group(2)[::-1]
                    vol = match.group(4)[::-1]
                    title = match.group(3)[::-1]
                    author = [(match.group(5)[::-1],"")]
                    references = append_reference(references=references, flag_error=print_errors, type=type,
                                                  title=title,
                                                  date=date, start_page=start_page,
                                                  author=author, volume=vol, full_cite=full,
                                                  original_cite=original)

            return create_citations(references, opinion)

    def find_restatements(text, opinion):
        if testing:
            print("Looking for Restatements")
        references=[]
        matches = re.finditer(r"((\d+)? (Restatement [\w+\(\)\s]+) (\d+) \(([A-Za-z\d][\sA-Za-z\d\.]*\s)?([0-9]{4})\))",text)
        if matches:
            for match in matches:
                type = "Restatement"
                full = match.group(1)
                original = match.group(1)
                volume = ""
                if match.group(2):
                    volume = match.group(2)
                title = match.group(3)
                pages = match.group(4)
                edition = ""
                author = [("Restatement", "")]
                if match.group(5):
                    edition = match.group(5)
                date = match.group(6)
                references = append_reference(references=references, flag_error=print_errors, type=type, title=title,
                                              date=date, author=author, full_cite=full, edition=edition, pages=pages,
                                              volume = volume, original_cite=original)
        matches = re.finditer(r"((\d+)?\s?(Restatement [\w+\(\)\s]+) (§§?\s?\w+(?: \d+,\d+,?\d*,?\d*)?(?:\d+\(\d+\))?(?:, Comment [A-Za-z]+)?(?:,? pp?.? \d+(?:,?-?\d+)?)?(?:,? and [\w\s']+)?)\s*\(([A-Za-z\d][\sA-Za-z\d\.]*\s)?([0-9]{4})\))",
                              text)
        for match in matches:
            type = "Restatement"
            full = match.group(1)
            original = match.group(1)
            volume = ""
            if match.group(2):
                volume = match.group(2)
            title = match.group(3)
            pages = match.group(4)
            author = [("Restatement", "")]
            edition = ""
            if match.group(5):
                edition = match.group(5)
            date = match.group(6)
            if testing:
                print("Restatement: " + original)
            references = append_reference(references=references, flag_error=print_errors, type=type, title=title,
                                              date=date, author=author, full_cite=full, edition=edition, pages=pages,
                                              volume=volume, original_cite=original)

        return create_citations(references, opinion)
    def find_other(text, opinion):
        if testing:
            print("Looking for Other")
        references=[]
        matches = re.finditer(r"(Letter from ([\w.\s]+\s)?([\w]+)\sto([\w.\s]+)\s\(([\w]{3,4}\.?\s\d+,\s*\d{4})\))",text)
        if matches:
            for match in matches:
                type = "letter"
                full = match.group(1)
                original = match.group(1)
                if match.group(2):
                    author = [(match.group(3), match.group(2))]
                else:
                    author = [(match.group(3), "")]
                title = "Letter to " + match.group(4)
                date = match.group(5)
                references = append_reference(references=references, flag_error=print_errors, type=type, title=title,
                                              date=date, author=author, full_cite=full,
                                              original_cite=original)

        matches = re.finditer(r"(Taped excerpts of ([\s\w]+),\s([\w]{3,4}\.?\s\d+,\s*\d{4}))",
                              text)
        if matches:
            for match in matches:
                type = "video"
                full = match.group(1)
                original = match.group(1)
                author = [("no_author", "")]
                title = match.group(2)
                date = match.group(3)
                references = append_reference(references=references, flag_error=True, type=type, title=title,
                                      date=date, author=author, full_cite=full,
                                      original_cite=original)

        return create_citations(references, opinion)

    print_errors = False
    if testing:
        print_errors = True
    text = opinion.opinion_text
    references = []
    citations = []

    books = find_books(text, opinion)
    if books:
        citations = citations + books
    #if testing:
    #    print("Warning: News is turned off due to bug!")
    news = find_news(text, opinion)
    if news:
        citations = citations + news
    journals = find_journals(text, opinion)
    if journals:
        citations = citations + journals
    other_sources = find_other(text, opinion)
    if other_sources:
        citations = citations + other_sources
    restatements = find_restatements(text, opinion)
    if restatements:
        citations = citations + other_sources

    return citations

def get_dir(dir="./../Legal_Parser/Parsed_Cases", testing=False):
    #dir="./../parsed_cases_CAP"
    #dir="./../Citator_Cases"
    if testing:
        dir="./../Citator_Cases_tests"
    os.makedirs(dir, exist_ok=True)
    return dir

def get_dir_ref(dir="./references"):
    os.makedirs(dir, exist_ok=True)
    return dir

def clean(citations=[]):
    new_citations = []
    for citation in citations:
        new_cite = citation.update()
        if isinstance(new_cite, Citation):
            new_citations.append(new_cite)
    return new_citations

def write_citations(cites):
    with open("/Volumes/WD My Passport/LILProject/References/citations.csv",'w') as csvfile:
        fieldnames = [ 'opinion_name','reference_name', 'opinion_id','reference_id']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for cite in cites:
            writer.writerow(cite.export())

def find_files(dir, dir_ref, citations, potential_citations="", testing=False):
    for file in os.listdir(dir):
        print(dir + "/" + file)
        if file.endswith(".json"):
            print(dir + "/" + file)
            json_data = open(dir + "/" + file).read()
            opinion_cluster = json_to_cluster(json_data)
            if (testing):
                print("New Opinion Cluster: " + opinion_cluster.name + "!")
            for opinion in opinion_cluster.opinions:
                new_citations = find_citations(opinion, testing=testing)
                potential_citations = potential_citations + "\n" + find_potential_citations(opinion)
                if new_citations:
                    # print(citations)
                    citations = citations + new_citations
        if os.path.isdir(dir + "/" + file):
            path = dir + "/" + file
            new_cites = find_files(dir=path, dir_ref=dir_ref, citations=citations, potential_citations=potential_citations)
            citations = citations + new_cites[0]
            potential_citations = potential_citations+new_cites[1]
    return (citations, potential_citations)

def main(testing = False, dir=None, testing_dir=False):
    if testing:
        print("testing features are enabled!")
    if dir:
        dir = get_dir(dir=dir, testing=testing_dir)
    else:
        dir = get_dir(testing=testing_dir)
    citations = []
    dir_ref = get_dir_ref(dir = "/Volumes/WD My Passport/LILProject/References")

    reference_list = {"0": "test"}
    output = open(dir_ref + "/references.pk1", "wb")
    pickle.dump(reference_list, output, -1)
    output.close()

    citations_both = find_files(dir=dir, dir_ref=dir_ref, citations=citations, testing=testing)

    citations = citations_both[0]
    potential_citations = citations_both[1]

    citations = clean(citations)
    write_citations(citations)

    output=open(dir_ref + '/possible_citations.txt','w')
    output.write(potential_citations)
    output.close()

if __name__ == "__main__":
    main(testing=True, testing_dir=False, dir="/Volumes/WD My Passport/LILProject/CAP_data_parsed/")
