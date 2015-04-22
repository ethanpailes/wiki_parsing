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

WIKI_MARKUP_BLOCK_REGEX = re.compile("{{.*}}");

INFOBOX_BEGIN_REGEX = re.compile("{{ *Infobox *[Uu]niversity")

COORD_KEYS = [ "latd", "latm", "latNS", "longd", "longm", "longEW"]
EST_KEYS = ["established"]

"""
                            CLASSES
"""

class Coordinates(object):
    valid = False
    def __init__(self, coord_str):
        pairings = coord_str.split("|")
        pairings = [p.split("=") for p in pairings]
        pairings = [p for p in pairings if len(p) == 2]
        d = {}
        for k, v in pairings:
            d[k.strip()] = v.strip()

        try:
            latd = float(d["latd"])
            latm = float(d["latm"])
            latNS = d["latNS"]
            latitude = latd + (latm * (1.0/60.0))
            if latNS == "S":
                latitude = -latitude

            longd = float(d["longd"])
            longm = float(d["longm"])
            longEW = d["longEW"]
            longitude = longd + (longm * (1.0/60.0))
            if longEW == "W":
                longitude = -longitude

            self.coord_str = "{}\t{}\n".format(latitude, longitude)
            self.valid = True
        except ValueError: # if casting fails
            pass
        except KeyError: # if a key is not present
            pass

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
        self.coords = self.__fetch_coordinates_bykeys()

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

    def __fetch_coordinates_bykeys(self):
        coordinate_string = ""
        for line in self.lines:
            for key in COORD_KEYS:
                if key in line:
                    coordinate_string += line
        print(len(coordinate_string))
        if len(coordinate_string) > 0:
            return Coordinates(coordinate_string)

    def write_to_file(self, outfilehandle):
        data_str = self.est
        if self.coords != None and self.coords.valid:
            data_str += "\t{}".format(self.coords.coord_str)
            #outfilehandle.write(self.coords.coord_str)
        print(data_str)

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
