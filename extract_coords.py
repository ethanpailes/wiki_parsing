"""
Authors: Ethan Pailes, Abdisalan Mohamud, Ethan Kopit
File: extract.py
Description: A script to extract a certain class of articles from the base wiki
corpus.
"""

import re
import sys

IN_FILE = "settlement_articles.txt"
IN_FILE = "minis.txt"
OUT_FILE = "coordinates.txt"

PAGES_TO_STORE = 10000
PAGE_BEGIN_REGEX = re.compile(".*<page>.*")
PAGE_END_REGEX = re.compile(".*</page>.*")

COORD_LINE_REGEX = re.compile(".*Coord\|[0-9]*\.[0-9]*\|.*")
COORD_REGEX = re.compile(".*Coord.*") #TODO delete and rename the new one
COORD_REGEX_SUBS = re.compile("{{Coord\|[0-9].*\|.*}}")
NUMBER_REGEX = re.compile("[0-9]")

COORD_KEYS = [ "latd", "latm", "latNS", "longd", "longm", "longEW"]


"""
                            CLASSES
"""

class Coordinates(object):
    valid = False
    def __init__(self, coord_str, by_keys):
        if by_keys:
            self.__init_from_keys(coord_str)
        else:
            self.__init_from_coord_tag(coord_str)

    def __init_from_keys(self, coord_str):
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

            print(latitude, longitude)
            self.coord_str = "{}\t{}".format(latitude, longitude)
            self.valid = True
        except ValueError: # if casting fails
            pass
        except KeyError: # if a key is not present
            pass

    def __init_from_coord_tag(self, coord_str):
        self.raw_str = coord_str
        cord_mentions = COORD_REGEX_SUBS.findall(coord_str)
        assert(len(cord_mentions) >= 1)
        coord_tag = cord_mentions[0]

        coord_arr = coord_tag.split("|")
        coord_arr = [x for x in coord_arr if self.__is_cordinate_info(x)]

        self.coord_str = {2: self.__numerical_form,
                          4: self.__directional_form,
                          6: self.__directional_form_minutes,
                          8: self.__directional_form_minutes_seconds
                          }[len(coord_arr)](coord_arr)
        self.valid = True

    def __numerical_form(self, coord_arr):
        return "\t".join(coord_arr)

    def __directional_form(self, coord_arr): #TODO still wonkey
        assert(coord_arr[1] in ["N", "S"] and coord_arr[3] in ["E", "W"])
        longitude = coord_arr[0]
        latitude = coord_arr[2]
        if coord_arr[1] == "S":
            longitude = "-" + longitude
        if coord_arr[3] == "W":
            longitude = "-" + latitude
        return "\t".join([longitude, latitude])

    def __directional_form_minutes(self, coord_arr):
        assert(coord_arr[2] in ["N", "S"] and coord_arr[5] in ["E", "W"])
        longitude = coord_arr[0]
        longitude_min = coord_arr[1]

    def __directional_form_minutes_seconds(self, coord_arr):
        pass

    def __is_cordinate_info(self, info):
        if info in ["N", "S", "E", "W"]:
            return True
        if NUMBER_REGEX.match(info):
            return True
        return False

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
                # self.coord_str = self.__fetch_coordinates()
                self.coords = self.__fetch_coordinates_bykeys()
                return
            if line == "":
                self.eof = True
                # self.coord_str = self.__fetch_coordinates()
                self.coords = self.__fetch_coordinates_bykeys()
                return

    def __fetch_coordinates(self):
        for line in self.lines:
            if COORD_LINE_REGEX.match(line):
                return Coordinates(line, False)

    def __fetch_coordinates_bykeys(self):
        coordinate_string = ""
        for line in self.lines:
            for key in COORD_KEYS:
                if key in line:
                    coordinate_string += line
        if len(coordinate_string) > 0:
            return Coordinates(coordinate_string, True)

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
    print("Processing")
    while True:
        p = Page(in_file)
        if p.hit_eof():
            break
        pages.append(p)
        if len(pages) >= PAGES_TO_STORE:
            for x in pages:
                x.write_coords_to_file(output_file)
                sys.stdout.write(".")
            pages = []
    for x in pages:
        x.write_coords_to_file(output_file)

if __name__ == "__main__":
    main()
