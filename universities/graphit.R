library(ggplot2)
library(maps)
library(mapdata)
library(rgeos)
library(maptools)
library(mapproj)
library(PBSmapping)
library(data.table)

###############################################################################
WIKI_HOME = "~/Documents/tufts/text_mining/wiki/"
UNIVERCITY_HOME = paste0(WIKI_HOME, "universities/")
OUT_DIR = paste0(UNIVERCITY_HOME, "output/")

XLIM = c(-150, 150)
YLIM = c(-70, 70)
###############################################################################

worldmap = map_data("world")

# clip the world map
setnames(worldmap, c("X", "Y", "PID", "POS", "region", "subregion"))
worldmap = clipPolys(worldmap, xlim = XLIM, ylim = YLIM)

# map coloration variables
land = "grey"
water = "grey80"
bgColor = "grey80"

locs = read.csv(paste0(UNIVERCITY_HOME, "uni_info.txt"),
                   stringsAsFactors = F, header = F, sep = "\t")

humanLocations = geom_point(data = locs, color = "red", alpha = .75, size = 1, aes(y = V2, x = V3))

p = ggplot() + coord_map(xlim = XLIM, ylim = YLIM) +
    geom_polygon(data=worldmap, aes(X,Y,group=PID), size = 0.1, colour=land, fill=water, alpha=1, ) +
    humanLocations + labs(y="", x="") + theme_grey()
  
print(p)
  
ggsave(file = paste0(OUT_DIR, "wiki_universities.png"),
         plot = p, dpi = 600, width = 10, height = 6)
