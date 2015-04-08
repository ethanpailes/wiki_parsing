"""
Authors: Ethan Pailes, Abdisalan Mohamud, Ethan Kopit
File: extract_coords.py
Description: A script to pull coordinates from settlement data
"""

import re

IN_FILE = "settlement_articles.txt"
# IN_FILE = "minis.txt"
OUT_FILE = "coordinates.txt"

PAGES_TO_STORE = 10000
PAGE_BEGIN_REGEX = re.compile(".*<page>.*")
PAGE_END_REGEX = re.compile(".*</page>.*")

COORD_KEYS = [ "latd", "latm", "latNS", "longd", "longm", "longEW"]

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
                self.coords = self.__fetch_coordinates_bykeys()
                return
            if line == "":
                self.eof = True
                self.coords = self.__fetch_coordinates_bykeys()
                return

    def __fetch_coordinates_bykeys(self):
        coordinate_string = ""
        for line in self.lines:
            for key in COORD_KEYS:
                if key in line:
                    coordinate_string += line
        if len(coordinate_string) > 0:
            return Coordinates(coordinate_string)

    def write_coords_to_file(self, outfilehandle):
        if self.coords != None and self.coords.valid:
            outfilehandle.write(self.coords.coord_str)

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
        p = Page(in_file)
        if p.hit_eof():
            break
        pages.append(p)
        if len(pages) >= PAGES_TO_STORE:
            for x in pages:
                x.write_coords_to_file(output_file)
            flushes += 1
            print("Processed " + str(flushes * PAGES_TO_STORE) + " records.")
            pages = []
    for x in pages:
        x.write_coords_to_file(output_file)

if __name__ == "__main__":
    main()
