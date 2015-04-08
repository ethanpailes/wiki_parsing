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


"""
                            CLASSES
"""

class Coordinates(object):
    def __init__(self, coord_str):
        self.raw_str = coord_str
        cord_mentions = COORD_REGEX_SUBS.findall(coord_str)
        assert(len(cord_mentions) >= 1)
        coord_tag = cord_mentions[0]

        coord_arr = coord_tag.split("|")
        coord_arr = [x for x in coord_arr if self.__is_cordinate_info(x)]
        print(len(coord_arr))

        self.coord_str = {2: self.__numerical_form,
                          4: self.__directional_form,
                          6: self.__directional_form_minutes,
                          8: self.__directional_form_minutes_seconds
                          }[len(coord_arr)](coord_arr)


    def __numerical_form(self, coord_arr):
        return "\t".join(coord_arr)

    def __directional_form(self, coord_arr):
        print("PING")
        assert(coord_arr[1] in ["N", "S"] and coord_arr[3] in ["E", "W"])
        longitude = coord_arr[0]
        latitude = coord_arr[2]
        if coord_arr[1] == "S":
            longitude = "-" + longitude
        if coord_arr[3] == "E":
            longitude = "-" + latitude
        return "\t".join([longitude, latitude])

    def __directional_form_minutes(self, coord_arr):
        pass
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
                self.coord_str = self.__fetch_coordinates()
                print(self.coord_str)
                return
            if line == "":
                self.eof = True
                self.coord_str = self.__fetch_coordinates()
                return

    
    def __fetch_coordinates(self):
        for line in self.lines:
            if COORD_LINE_REGEX.match(line):
                return Coordinates(line).coord_str

        """
        try:
            for i in range(len(cord_arr)):
                if COORD_REGEX.match(cord_arr[i]):
                    print("PING")
                    longitude = cord_arr[i+1]
                    float(longitude)

                    longitude_dir = cord_arr[i+2]
                    if (longitude_dir == "N" or longitude_dir == "S"):
                        if longitude_dir == "S":
                            longitude = "-" + longitude
                    else:
                        float(longitude_dir)
                        latitude = longitude_dir
                        return "{}\t{}\n".format(longitude, latitude)


                    latitude = cord_arr[i+3]
                    float(latitude)

                    latitude_dir = cord_arr[i+4]
                    assert(latitude_dir == "E" or latitude_dir == "W")
                    if latitude_dir == "E":
                        latitude_dir = "-" + latitude_dir

                    return "{}\t{}\n".format(longitude, latitude)
        except IndexError:
            return None
        except AssertionError:
            return None
        except ValueError:
            return None
        """

    def write_coords_to_file(self, outfilehandle):
        if self.coord_str != None:
            outfilehandle.write(self.coord_str)

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
