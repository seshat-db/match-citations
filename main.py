import re
import json

from nltk.tokenize import word_tokenize
from collections import OrderedDict

# import nltk
# nltk.download('punkt')

year_re = re.compile(r"\b(18|19|20)\d{2}\b")

def preprocess(zotero, date_missing_counter):

    title_keys = {'event-title', 'collection-title', 'title-short', 'title', 'container-title'}
    author_keys = {'reviewed-author', 'author', 'container-author'}

    out_dict = {}
    out_dict["id"] = zotero["id"]
   

    title_words = []
    for key in title_keys:
        if key in zotero.keys():
            title_words += word_tokenize(zotero[key])
    
    out_dict["title"] = set(title_words)
    
    authors = []
    for key in author_keys:
        if key in zotero.keys():
            for author in zotero[key]:
                 authors += list(author.values())
    out_dict["authors"] = set(authors)
    
    try:
        out_dict["publisher"] = set(word_tokenize(zotero["publisher"]))
    
    except KeyError:
        pass
    
    years = []
    try:
        # print(zotero["issued"])
        years.append(zotero["issued"]['date-parts'][0][0])
        
        if "season" in zotero["issued"].keys():
            if len(zotero["issued"]["season"]) == 4:
                years.append(zotero["issued"]["season"])
    
    except KeyError:
        # print("date missing")
        date_missing_counter += 1

        
    out_dict["years"] = set(years)
    return out_dict


def search_match(citation, zoteros):

    years_weight = 0.3
    title_weight = 0.2
    authors_weight = 0.45
    publisher_weight = 0.05

    scores = []
    

    if len(citation) == 0:
        return "NO_CITATION_PROVIDED"

    years = set(year_re.findall(citation))
    words = set(word_tokenize(citation))

    for zotero in zoteros:
        author_score = len(words.intersection(zotero["authors"])) / (len(zotero["authors"]) + 0.01)
        title_score = len(words.intersection(zotero["title"])) / (len(zotero["title"]) + 0.01)
        years_score = len(years.intersection(zotero["years"])) / (len(zotero["years"]) + 0.01)
        if "publisher" in zotero.keys():
            publisher_score = len(words.intersection(zotero["publisher"])) / len(zotero["publisher"])

        score = author_score * authors_weight + title_score * title_weight + years_score * years_weight + publisher_score * publisher_weight
        scores.append((score, zotero, citation, (author_score, title_score, years_score, publisher_score)))
        
    best_match = max(scores, key = lambda x: x[0])

    return best_match



def main():

    with open("all_citations_with_duplicates_indicated.json", "r") as handle:
        citations = json.load(handle)
    with open ("/home/scrappy/csh/match-citations/Seshat Databank.json", "r") as handle:
        library = json.load(handle)

    preprocessed = []
    date_missing_counter = 0

    for zotero in library:
        preprocessed.append(preprocess(zotero, date_missing_counter))


    
    for ref_id , citation in citations.items():
        
        if citation.startswith("IS_DUPLICATE"):
            citations[ref_id] = citations[citation[13:]]
        
        else :
            citations[ref_id] = (search_match(citation, preprocessed))
        

    
    num_scores = 0
    for i in citations.values():
        if type(i[1]) == str:
            continue
        if i[0] > 0.4:
            num_scores += 1
        # print(i[0])
        # print(i[1])
        # print(i[2])
        # print("\n")
        # # for x in i:
        # #     print(x)

        # # break
        # # if len(i[0]) > 2:
        # #     print(i[0][1])
        # #     print(i[0][2])
    # return citations
    print(num_scores, "/" , len(citations.keys()))










if __name__ == "__main__":
    main()
