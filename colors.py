
from bokeh import palettes

# base = 0xFFFFFF
# reds = []
# blues= []
# greens=[]
# for i in range(256):

#     reds.append( '#%06x'% ( base - (i * 16 **4) ) )
#     greens.append( '#%06x'% ( base - (i * 16 **2) ) )
#     blues.append( '#%06x'% ( base - i) )

# blue_red = palettes.diverging_palette(palettes.Blues[9], palettes.Reds[9], 18)
# blue_red = palettes.diverging_palette(blues[128], reds[128], 256)
# blue_red = palettes.diverging_palette(blues[::-1], reds[::-1], 256*2)
blue_red = palettes.diverging_palette(palettes.Blues256, palettes.Reds256, 256*2)


viridis = palettes.Viridis[256]

palette_opts = {
    "viridis": palettes.Viridis[256],
    "magma": palettes.Magma[256],
    "blue_red": blue_red,
}

