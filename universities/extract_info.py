"""
Authors: Ethan Pailes, Abdisalan Mohamud, Ethan Kopit
File: extract_coords.py
Description: A script to pull coordinates from settlement data
"""

import re
import json

# IN_FILE = "university_articles.txt"
IN_FILE = "mini.txt"
OUT_FILE = "uni_info.txt"

PAGES_TO_STORE = 10000
PAGE_BEGIN_REGEX = re.compile(".*<page>.*")
PAGE_END_REGEX = re.compile(".*</page>.*")

WIKI_MARKUP_BLOCK_REGEX = re.compile("{{(.*)}}")

INFOBOX_BEGIN_REGEX = re.compile("{{ *Infobox *[Uu]niversity")

COORD_KEYS = [ "latd", "latm", "latNS", "longd", "longm", "longEW"] #TODO delete
EST_KEYS = ["established"]
COORDINATE_KEY = "coor"

COORDINATE_PARSING_SCHEMA = [
    (re.compile(
    "[Cc]oord\|[0-9]+\|[0-9]+\|[0-9]+\|[NS]\|[0-9]+\|[0-9]+\|[0-9]+\|[EW]\|"),
        [
            (None, lambda t, s: None),
            ("lat", lambda t, s: float(s)),
            ("lat", lambda t, s: t + (float(s) * (1.0/60.0))),
            ("lat", lambda t, s: t + (float(s) * (1.0/3600.0))),
            ("lat", lambda t, s: t if s == "N" else -t),

            ("long", lambda t, s: float(s)),
            ("long", lambda t, s: t + (float(s) * (1.0/60.0))),
            ("long", lambda t, s: t + (float(s) * (1.0/3600.0))),
            ("long", lambda t, s: t if s == "N" else -t)
        ]),
    # TODO add the two number one here
    (re.compile("[Cc]oord\|[0-9.-]+\|[0-9.-]+\|"),
        [
            (None, lambda t, s: None),
            ("lat", lambda t, s: float(s)),

            ("long", lambda t, s: float(s))
        ]),
]

"""
                            CLASSES
"""

class Coordinates(object):
    coord_str = None
    def __init__(self, info_lines):
        raw_coords = None
        for line in info_lines:
            if COORDINATE_KEY in line:
                try:
                    raw_coords = WIKI_MARKUP_BLOCK_REGEX.search(line).group(1)
                except AttributeError:
                    pass

        targets = {"lat": None, "long": None}
        if raw_coords != None:
            for reg, parse_list in COORDINATE_PARSING_SCHEMA:
                if reg.match(raw_coords):
                    coord_list = raw_coords.split("|")
                    for i, (tgt, F) in enumerate(parse_list):
                        if tgt in targets:
                            targets[tgt] = F(targets[tgt], coord_list[i])
                    break
        if targets["lat"] != None and targets["long"] != None:
            self.coord_str = "{}\t{}".format(targets["lat"], targets["long"])

class University(object):
    def __init__(self, infilehandle):
        """ takes the main corpus file and consumes the first page it finds """
        self.lines = []
        self.est = None
        self.eof = False
        appending = False
        while True:
            line = infilehandle.readline()
            if PAGE_BEGIN_REGEX.match(line):
                appending = True
            if appending:
                self.lines.append(line)
            if PAGE_END_REGEX.match(line):
                self.__setup()
                return
            if line == "":
                self.__setup()
                self.eof = True
                return

    def __setup(self):
        #i = Infobox(self.lines)
        self.__info_box_lines()
        self.__fetch_date_established()
        self.coords = Coordinates(self.info_lines)

    # Expects to be called after lines has been initialized.
    # Initializes the internal info_lines variable TODO
    def __info_box_lines(self):
        curly_count = 0
        appending = False
        self.info_lines = []
        for line in self.lines:
            if INFOBOX_BEGIN_REGEX.search(line):
                appending = True

            if appending:
                curly_count += line.count("{{")
                curly_count -= line.count("}}")
                self.info_lines.append(line)
                if curly_count <= 0:
                    break

    # Expects to be called when the self.info_lines has been initialized
    # initializes the date of the current page
    def __fetch_date_established(self):
        est_str = ""
        for line in self.info_lines:
            for key in EST_KEYS:
                if key in line:
                    est_str += line

        # build dictionary out of est string
        pairs = WIKI_MARKUP_BLOCK_REGEX.sub("", est_str)
        pairs = pairs.split("|")
        pairs = [p.split("=") for p in pairs]
        pairs = [p for p in pairs if len(p) == 2]
        d = {}
        for k, v in pairs:
            d[k.strip()] = v.strip()

        # locate date est
        for key in EST_KEYS:
            if key in d:
                self.est = d[key]
                return

    def write_to_file(self, outfilehandle):
        if (self.coords != None
                    and self.coords.coord_str != None
                    and self.est != None):
            data_str = "{}\t{}".format(self.est, self.coords.coord_str)
            print(data_str)
            #outfilehandle.write(self.coords.coord_str)

    def hit_eof(self):
        return self.eof

"""
                            END CLASSES
"""

def main():
    in_file = open(IN_FILE, "r")
    output_file = open(OUT_FILE, "w")
    pages = []
    flushes = 0
    print("Processing.")
    while True:
        p = University(in_file)
        if p.hit_eof():
            break
        pages.append(p)
        if len(pages) >= PAGES_TO_STORE:
            for x in pages:
                x.write_to_file(output_file)
            flushes += 1
            print("Processed " + str(flushes * PAGES_TO_STORE) + " records.")
            pages = []
    for x in pages:
        x.write_to_file(output_file)

if __name__ == "__main__":
    main()
