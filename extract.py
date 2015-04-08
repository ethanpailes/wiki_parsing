"""
Authors: Ethan Pailes, Abdisalan Mohamud, Ethan Kopit
File: extract.py
Description: A script to extract a certain class of articles from the base wiki
corpus.
"""

import re
import sys

CORPUS_FILE = "enwiki-20150304-pages-articles.xml"
OUT_FILE = "settlement_articles.txt"

PAGES_TO_STORE = 10000
PAGE_BEGIN_REGEX = re.compile(".*<page>.*")
PAGE_END_REGEX = re.compile(".*</page>.*")
IS_INTERESTING_REGEX = re.compile(".*Infobox\s+settlement.*")


"""
                            CLASSES
"""
class Page(object):
    def __init__(self, infilehandle):
        """ takes the main corpus file and consumes the first page it finds """
        self.lines = []
        self.eof = False
        appending = False
        while True:
            line = infilehandle.readline()
            if PAGE_BEGIN_REGEX.match(line):
                appending = True
            if appending:
                self.lines.append(line)
            if PAGE_END_REGEX.match(line):
                return
            if line == "":
                self.eof = True
                return

    def write_to_file_if_interesting(self, outfilehandle):
        if self.is_interesting():
            outfilehandle.writelines(self.lines)

    def hit_eof(self):
        return self.eof

    def is_interesting(self):
        """ returns true if the whole page is interesting """
        for line in self.lines:
            if IS_INTERESTING_REGEX.match(line):
                return True
        return False

"""
                            END CLASSES
"""

def main():
    corpus_file = open(CORPUS_FILE, "r")
    output_file = open(OUT_FILE, "w")
    pages = []
    print("Processing")
    while True:
        p = Page(corpus_file)
        if p.hit_eof():
            break
        pages.append(p)
        if len(pages) >= PAGES_TO_STORE:
            for x in pages:
                x.write_to_file_if_interesting(output_file)
                sys.stdout.write(".")
            pages = []
    for x in pages:
        x.write_to_file_if_interesting(output_file)



if __name__ == "__main__":
    main()
