from string import hexdigits
from random import choices
import os
SAFE_CHARS = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F')

class ColorHelper:

    def __init__(self, name, values):
        self.name = name
        self.values = values

    def __str__(self):
        return self.name

    def __iter__(self):
        #return self# this didn't work

        #yield self.values# nor did this

        #for i in range(3):
        #    yield self.values[i]

        for v in self.values:
            yield v



        """
        yield self.values[0]
        yield self.values[1]
        yield self.values[2]
        """

    def __getitem__(self, key):
        return self.values[key]

    def getValues(self):
        return self.values



def fromHex(hex, ln=0):
    hex = hex.upper()
    if len(hex) != 6:
        raise IndexError()
    for l in hex:
        if l not in hexdigits:
            raise TypeError('Read error at line {}. Hex values are {}.'.format(ln, hex))

    r = round(SAFE_CHARS.index(hex[0]) * 16 + SAFE_CHARS.index(hex[1]))
    g = round(SAFE_CHARS.index(hex[2]) * 16 + SAFE_CHARS.index(hex[3]))
    b = round(SAFE_CHARS.index(hex[4]) * 16 + SAFE_CHARS.index(hex[5]))

    return (r, g, b)

def buildColorDict():

    directory = str(os.path.dirname(os.path.abspath(__file__)))
    directory+= '/library/all_colors.txt'

    f = open(directory, 'r')

    lineNumber = 0

    stringList = f.read().split('\n')

    colorDict = dict()
    nameDict = dict()
    valuesDict = dict()

    for s in stringList:
        if ':' in s and len(s) >= 6 and s[:2] != '//':
            sp = s.split(':')
            name = sp[0].rstrip(' ')

            if '_' in name:

                informalName = name.lower().split('_')

                useName = ' '.join([informalName[1], informalName[0]])

                if 'hair ' == useName[:5]:
                    useName = useName[5:]
            else:
                useName = name.lower()

            colorValues = sp[1][0:6]

            nameDict[name] = useName
            valuesDict[name] = fromHex(colorValues, lineNumber)

            colorDict[name] = ColorHelper(useName, fromHex(colorValues, lineNumber))
        lineNumber+=1
    f.close()

    return colorDict, nameDict, valuesDict

ALL_COLORS_DICT, ALL_COLOR_NAMES_DICT, ALL_COLOR_VALUES_DICT = buildColorDict()


def blendColors(dictObject):
    #typeStr = str(type(colors))
    #print('type is: {}'.format(typeStr))
    #print('type is: {}'.format(type(colors[0])))
    #print('type is: {}'.format(type(colors[0][0])))
    #colors = list(colorsSet)
    r = 0
    g = 0
    b = 0

    l = 0

    for c in dictObject.values():
        print(c)
        r+=c[0]
        g+=c[1]
        b+=c[2]
        l+=1

    return tuple(round(r / l), round(g / l), round(b / l))

def checkBrightness(color):
    return ((color[0] / 256) + (color[1] / 256) + (color[2] / 256)) / 3

"""
def invert(color):
    brightness = checkBrightness(color)

    newR = 256 - color[0]
    newG = 256 - color[1]
    newB = 256 - color[2]
"""

BLACK =     fromHex('000000')
JET =       fromHex('343434')
GREY_DARK = fromHex('A9A9A9')
GREY =      fromHex('808080')
SILVER =    fromHex('C0C0C0')
GREY_LIGHT= fromHex('D3D3D3')
WHITE =     fromHex('FFFFFF')

AQUA =      fromHex('00FFFF')

BLUE =      fromHex('0000FF')
BLUE_DARK = fromHex('00008B')

BROWN =     fromHex('A52A2A')
BROWN_DARK= fromHex('422518')

BEIGE =     fromHex('F5F5DC')
PINK =      fromHex('FFC0CB')

GREEN =     fromHex('00FF00')
GREEN_DARK= fromHex('006400')

RED_DARK =  fromHex('8B0000')
RED =       fromHex('FF0000')
AUBURN =	fromHex('A52A2A')
BUFF =		fromHex('F0DC82')
TUSCANY =   fromHex('C09999')
RED_TUSCAN =fromHex('7C3030')

MAROON =    fromHex('080000')

GOLD =      fromHex('FFD700')
ORANGE =    fromHex('FFA500')
YELLOW =    fromHex('FFFF00')
TAN =       fromHex('D2B48C')
PURPLE =    fromHex('800080')
INDIGO =    fromHex('4B0082')
CHOCOLATE = fromHex('D2691E')
OLIVE =     fromHex('808000')
UMBER_BURNT =fromHex('8A3324')
CINNAMON =  fromHex('7B3F00')
COPPER =    fromHex('B87333')


ALL_COLORS = (BLACK, JET, GREY_DARK, GREY, SILVER, GREY_LIGHT, WHITE,

TUSCANY, RED_TUSCAN, MAROON
)

class MatColor:
    def __init__(self, name, values):
        self.name = name
        self.capName = name.capitalize()
        self.values = values

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash(self.name, self.values)

COL_BLACK = MatColor('black', BLACK)
COL_GREY =  MatColor('grey', GREY)
COL_GREY_LIGHT = MatColor('light grey', GREY_LIGHT)
COL_WHITE = MatColor('white', WHITE)





def invertBrightness(col):
    r = col[0]
    g = col[1]
    b = col[2]
    total = r + g + b
    totalPercent = (total) / 256 * 3
    inversePercent = 1 - totalPercent

    rPercent = r / total
    gPercent = g / total
    bPercent = b / total

    return (round(rPercent * inversePercent * 256), round(gPercent * inversePercent * 256), round(bPercent * inversePercent * 256))

"""
	ROSE_TAUPE			("rose taupe", "",			0x905D5D,	0b00000010000),//0
	ROSEWOOD			("rosewood", "",			0x674846,	0b00000010000),//0.01010101
	ROSE_EBONY			("rose ebony", "",			0x674846,	0b00000010000),//0.01010101

	GREY_LIGHT_HAIR		("light grey",	"",			0xD6C4C2, 		0b10),		//0.016666671
	MELON				("melon", "",				0xFDBCB4,		0b0),		//0.01826484
	BROWN_HAIR			("brown",	"",				0x6A4E42,		0b10),		//0.05

	GREY_MEDIUM			("medium grey",	"",			0xB7A69E,		0b10),				//0.05333333
	GREY_DARK			("dark grey",	"",			0x71635A,		0b10),				//0.0652174

	PUMPKIN				("pumpkin", "",		0xFF7515,		0b0),				//0.068376064

	BURNT_ORANGE		("burnt orange", "",0xCC55, 0,			0b00000010000),		//0.06944445
	ORANGE_PERSIAN		("Persian orange", "", 	0xD99058,	0b00100011000),		//0.072351426

	COPPER 				("copper", "", 		0xB87333,		0b00010000000),//0.0802005
	ORANGE 				("orange", "", 		0xFF7F00,			0b00100011000),//0.08300653

	SUNSET				("sunset", "",			0xFAD6A5,	0b0),		//0.09607843
	SUNRAY				("sunray", "",			0xE3A857,	0b0),		//0.09642857
	SAND				("sand", "",			0xE1A95F,	0b0),		//0.0948718
	ORANGE_DARK			("dark orange", ""FF8C00,			0b00100011000),//0.09150326
	ORANGE_CARROT		("carrot orange", ""ED9121,		0b00100011000),//0.09150326
	BEAVER				("beaver", "",		0x9F8170,		0b0),//0.06028369
	BROWN				("brown", "", 		0x964B00,			0b100110000000),//0.083333336
	BROWN_LIGHT			("light brown",	"",	0xA7856A,		0b10),//0.07377049
	BROWN_DARK			("dark brown",	"",	0x654321,		0b0),//0.083333336
	BROWN_DARK_HAIR		("dark brown",	"",	0x3B3024,		0b10),//0.08695652

	YELLOW 				("yellow", "", 		0xFFFF00,			0b1000000101000),//0.16666667
	YELLOW_GOLDEN		("golden yellow", "",0xFFDF00,			0b10),//0.14575164
	GOLDEN 				("golden", "", 		0xFFD700,		0b1000100000000),//0.14052288
	GOLDEN_POPPY		("golden poppy", "",0xFCc200,			0b0),//0.12830688
	GOLD_HARVEST		("harvest gold", "",0xDA9100,			0b0),//0.11085627
	GOLDENROD			("goldenrod", "",	0xCFB53B,		0b0),//0.13738738
	CREAM				("cream", "",		0xFFFDD0,		0b00100100000),//0.15957446

	BLACK_HAIR			("black",	"black",		0x090806,		0b10),				//0.111111104
	GREY_BATTLESHIP		("battleship grey", "", 	0x848482,		0b0000100000000),	//0.16666667

	BLACK_OFF			("off black",	"",			0x2C222B,		0b10),				//0.85
	CHARCOLE			("charcole", "blue-black",	0x36454F,		0b1001100000000),	//0.56666666
	SLATE				("slate",	"soft black",	0x708090,		0b1001000010000),	//0.5833333
	GREY_COOL			("cool grey", "",			0x8C92AC,		0b1001000100000),	//0.6354167
	GREY_ASH			("ash grey", 	"salt and pepper",	0xB2BEB5,	0b1001000100000),//0.375
	IVORY				("ivory", 	"",				0xFFFFF0,		0b0),//0.16666667
	PURPLE 				("purple", 	"purple", 		0x800080,			0b100100011000),//0.6770833
	INDIGO 				("indigo", 		"indigo", 	0x4B0082,			0b100100011000),//0.7628205
	MAUVE				("mauve", 		"",			0xEDB0FF,		0b0),//0.79535866
	MAUVE_OPERA			("opera mauve", "",			0xB784A7,		0b0),//0.8856209
	MAUVE_TAUPE			("mauve taupe", "",			0x915F6D,		0b0),//0.9533333
	MAUVE_OLD			("old mauve", "",			0x673147,		0b0),//0.93209875

	VIOLET 				("violet", "", 				0x8F00FF,			0b00000001000),//0.7601307
	BLUE 				("blue", "", 				0000FF,				0b01001001000),//0.6666667
	BLUE_ALICE			("Alice blue", "",			0xF0F8FF,		0b00000010000),//0.5777778
	BLUE_MIDNIGHT		("midnight blue", "",		0x191970,		0b00000100000),//0.6666667
	BLUE_SKY			("sky blue", "",			0x87CEEB,		0b00000100000),//0.54833335
	BLUE_LIGHT			("light blue", "",			0xADD8E6,		0b0001000100000),//0.5409357
	BLUE_DARK 			("dark blue", "", 			00008B,				0b0001111000000),//0.6666667
	BLUE_STEEL			("steel blue", "",			0x4682B4,		0b0001000000000),//0.57575756
	BLUE_GREY			("blue grey", "",			0x6699CC,		0b1000000100000),//0.5833333
	TEAL 				("teal", "", 				008080,			0b0000001011000),//0.5
	TURQUOISE 			("turqoise", "",			0x40E0D0,		0b0000010000000),//0.48333335
	EGGPLANT			("eggplant", "",			0x614051,		0b00000010000),//0.9141414
	GREEN_MIDNIGHT		("midnight green", "",		004953,			0b00000010000),//0.5200803
	GREEN_JUNGLE		("jungle green", "",		0x29AB87,		0b00000010000),//0.45384613
	GREEN_LIGHT			("light green", "",			0x90EE90,		0b00000100000),//0.33333334
	GREEN_INDIA			("indian green", "",		0x138808,		0b00000010000),//0.3190104
	GREEN_FOREST		("forest green", "",		0x228B22,		0b00000010000),//0.33333334
	OLIVE				("olive", "",				0x808000,			0b00001000000),//0.16666667
	MINT				("mint", "",				0x3EB489,		0b00000100000),//0.43926552
	FELDGRAU			("feldgrau", "",			0x4D5D53,		0b100000000000),//0.39583334

	PINE_GREEN			("pine green", "",	0x01796F,		0b00000010000),//0.48611113
	GREEN 				("green", "", 		0,	0xFF0000,			0b00000111000),//0.33333334
	LIME 				("lime", "", 		0xBFFF00,			0b00000001000),//0.20849673

	APRICOT				("apricot", "",		0xFBECB1,		0b0),//0.13288288
	BROWN_GOLDEN		("golden brown", "",0x996515,		0b0),//0.10101011
	BROWN_GOLDEN_HAIR	("golden brown",	"",		0x554838, 0b10),//0.09195402
	BROWN_WOOD			("wood brown", "",	0xC19A6B,		0b0),//0.09108528
	BROWN_MEDIUM		("medium brown",	"",	0x4E433F,	0b0),//0.04444444
	BROWN_ASH			("ash brown",	"",	0x977961, 		0b0),//0.07407407
	BROWN_PALE			("pale brown", "",	0x987654,		0b0),
	CHOCOLATE 			("chocolate", "deepest brunette", 	0x7B3F00,			0b00100000000),//0.085365854
	BISTRE				("bistre", "",		0x3D2B1F,		0b0),//0.06666666
	BOLE				("bole", "",		0x79443D,		0b0),//0.019444445
	BRONZE				("bronze", "",		0xCD7F32,		0b0),//0.0827957
	BRONZE_ANTIQUE		("antique bronze", "",0x665D1E,		0b0),//0.14583333
	LION				("lion", "",		0xC19A6B,		0b0),//0.09108528
	ECRU				("ecru", "",		0xC2B280,		0b0),//0.12626262
	UMBER 				("umber", "", 		0x635147,		0b1100100000000),//0.05952381
	UMBER_BURNT		 	("burnt	umber", "", 	0x8A3324,	0b00100000000),//A45A52  0.024509808
	UMBER_RAW			("raw umber", "",	0x826644,		0b0),//0.09139785
	KHAKI				("khaki", "",		0xC3B091,		0b0),//0.10333333
	GAMBOGE				("gamboge", "",		0xE49B0F,		0b0),//0.10954616
	CORAL				("coral", "",		0xFF7F50,		0b0),//0.044761907
	SEPIA				("sepia", "", 		0x704214,		0b0),
	CORAL_PINK			("coral pink", "",	0xF88379,		0b0),//0.013123363
	MAHOGANY			("mahogany", "",	0xC04000,			0b0),//0.003472219
	FLAME				("flame", "",		0xE25822,		0b0),//0.046875
	FIRE_BRICK			("fire brick", "",	0xB22222,		0b0),//0.0
	TOMATO				("tomato", "",		0xFF6347,		0b0),//0.025362322
	BITTERSWEET			("bittersweet", ""FE6F5E,		0b0),//0.017708331
	PERSIMMON			("persimmon", "",	0xEC58, 0,			0b0),//0.06214689
	RUSSET 				("russet", "russet brown", 	0x80461B,		0b1000100000000),//0.070957094
	BURGUNDY			("burgundy", "", 	0x80, 0020,			0b1000100000000),//0.9583333
	BURGUNDY_VIVID		("vivid burgundy", "", 	0x9F1D35,	0b1000100000000),//0.9692308
	BURGUNDY_OLD		("old burgundy", "", 	0x43302E,	0b1000100000000),//0.015873015
	SCARLET				("scarlet", "",			0xFF2400,	0b0),//0.02352941
	SCARLET_DARK		("dark scarlet",	"",	0x560319,	0b0),
	RED 				("red", "", 		0xFF0000,			0b01010011000),//0.0
	RED_IMPERIAL		("imperial red", "", 	0xED2939,	0b01010011000),//0.9863945
	RED_LIGHT			("light red",	"",		0xB55239,	0b10),//0.03360215
	RED_DARK			("dark red", "", 	0x8B0000,			0b01010011000),//0.0
	RED_DARK_HAIR		("dark red", "", 	0x8D4A430,		0b10),//0.67785573

	RED_VIOLET			("red violet", "", 		0xC71585,	0b01010011000),//0.8951311
	BLUSH				("blush", "",		0xDE5D83,		0b0),//0.95090437
	WINE				("wine", "",		0x722F37,		0b0),//0.9800995
	CHAMPAGNE			("champagne", "",	0xF7E7CE,		0b0),//0.101626016
	CLARET				("claret", "",		0x7F1734,		0b0),//0.95352566
	WINE_DREGS			("wine dregs", "",	0x673147,			0b0),//0.93209875
	BYZANTIUM			("byzantium", "",		0x702963,		0b0),//0.86384976
	TERRA_COTTA			("terra cotta", "",		0xE2725B,	0b0),//0.028395066
	RASPBERRY			("raspberry", "",	0xE30B5C,		0b0),//0.9375
	RASPBERRY_ROSE		("raspberry rose", "",	0xB3446C,		0b0),//0.9399399

	//Raspberry
	CRIMSON_ELECTRIC	("electric crimson", ""FF, 003F,	0b01010011000),//0.95882356
	FOLLY				("folly", "",			0xFF004F,	0b0),//0.94836605
	CRIMSON_ALIZARIN	("alizarin crimson", ""E32636, 0b0),//0.9858906
	AMARANTH			("amaranth", "",	0xE52B50,		0b0),//0.96684587
	AMARANTH_PINK		("amaranth pink", "",0xF19CBB,		0b0),//0.93921566
	RED_RADICAL			("radical red", "",	0xFF355E,		0b0),//0.9661716
	AMARANTH_PURPLE		("amaranth purple", "",	0xAB274F,		0b0),//0.94949496
	AMARANTH_D_PURPLE	("amaranth deep purple", "",0x9F2B68,	0b0),//0.9123563
	FUSHSIA_ANTIQUE		("antique fuchsia", "",	0x915C83,	0b0),//0.8773585
	HELIOTROPE			("heliotrope", "",	0xDF73FF,		0b0),//0.7952381
	HELIOTROPE_GREY		("heliotrope grey", "",	0xAA98A9,	0b0),//0.8425926
	HELIOTROPE_OLD		("heliotrope", "",	0x563C5C,		0b0),//0.8020833

	//Heliotrope
	MAGNOLIA			("magnolia", "",	0xF8F4FF,		0b00000100000),//0.72727275
	MAGENTIA 			("magentia", "", 	0xFF, 0FF,			0b00000011000),//0.8333333
	MAGENTIA_SKY		("sky magentia", ""Cf71AF,		0b00000011000),//0.8900709
	PLUM				("plum", "",		0x8E4585,		0b0),//0.8538813
	BEIGE				("beige", "",		0xF5F5DC,		0b10000100000),//0.16666667
	PUCE				("puce", "",		0x722F37,		0b10000100000),//0.9800995
	TAN					("tan", "",			0xD2B48C,		0b00110100000),//0.09523809
	TAN_DARK			("dark tan","",		0x918151,		0b0),//0.125
	PEACH				("peach", "",		0xFFE5B4,		0b01000010000),//0.10888889

	CHESTNUT 			("chestnut", "chestnut brown", 	0x954535,		0b00100000000),//0.027777782
	CHESTNUT_BROWN 		("chestnut brown", "chestnut brown", 	0x504444,	0b00100000000),//0.0
	CHESTNUT_PALE		("pale chestnut",	"",	0xDDADAF,	0b0),//0.9930556
	RED_BARN 			("barn red", "", 	0x7C0A02,		0b00100000000),//0.010928959
	LAVA				("lava", "",		0xCF1020,		0b0),//0.9860384
	LAVA_DARK			("dark lava", "",	0x483C32,		0b0),//0.07575757

	LIVER				("liver",	"",		0x674C47,		0b0),//0.026041666
	LIVER_DOG			("dog liver",	"",	0xB86D29,		0b0),//0.07925408
	LIVER_DARK			("dark liver",	"",	0x543D37,		0b0),//0.03448276
	LIVER_CHESTNUT		("liver chestnut",	""987456,	0b0),//0.07575757
	LIVER_ORGAN			("liver",	"",		0x6C2E1F,		0b0),//0.032467533

	AUBURN_LIGHT		("light auburn",	"",	0x91553D,	0b10),//0.047619045
	AUBURN_DARK			("dark auburn",		"",	0x533D32,	0b10),//0.055555552
	REDWOOD				("redwood", "",		0xA45A52,		0b0),//0.016260168
	PINK				("pink", "",		0xFFC0CB,		0b11000110000),//0.97089946
	PINK_BAKER_MILLER	("Baker-Miller pink", ""FF91AF,	0b11000110000),//0.95454544
	PINK_FANDANGO		("fandango pink", "",	0xDE5285,	0b11000110000),//0.9392857
	PINK_CARNATION		("carnation pink", "",	0xFFA6C9,	0b11000110000),//0.93445694
	PINK_CHAMPAGNE		("champagne pink", "",	0xF1DDCF,	0b11000110000),//0.06862745
	PINK_PALE			("pale pink", "",		0xF9CCCA,	0b0),//0.007092198
	PINK_CONGO			("congo pink", "",		0xF88379,	0b0),//0.013123363
	PINK_SILVER			("silver pink", "",		0xC4AEAD,	0b0),//0.007246375
	PINK_SHOCKING		("shoching pink", "",	0xFC0FC0,	0b11000110000),//0.87552744
	PINK_BABY			("baby pink", "",		0xF4C2C2,	0b11000110000),//0
	PINK_ORCHID			("orchid pink", "",		0xF2BDCD,	0b11000110000),//0.9496855
	PINK_MEXICAN		("Mexican pink", "",	0xE4, 07C,		0b11000110000),//0.9093567
	BLOND				("blond",	"blond",	0xFAF0BE,	0b10),//0.13888888
	BLOND_DIRTY			("dirty blond",	"dirty blond",	0xFFD57D, 0b10),//0.112820506
	BLOND_PLATINUM		("platinum blond",	"",	0xCABFB1,	0b10),//0.093333334
	CINNABAR			("cinnabar", "",		0xE34234,	0b0),//0.013333331

	BLOND_STRAWBERRY	("strawberry blond",		"",	0xA56B46,	0b10),//0.06491228
	SALMON				("salmon", "",			0xFA8072,	0b0),//0.01715686
	SALMON_LIGHT		("light salmon", "",	0xFFA07A,	0b0),//0.047619045
	BLOND_GOLDEN		("golden blond",	"",	0xE5C8A8,	0b10),//0.08743169
	BLOND_ASH			("ash blond",		"",	0xDEBC99,	0b10),//0.08454106
	BLOND_HONEY			("honey blond",		"",	0xB89778,	0b10),//0.080729164

	BLOND_LIGHT			("light blond",	"",		0xE6CEA8,	0b10),//0.10215054
	BLOND_BLEACHED		("bleached blond",	"",	0xDCD0BA,	0b10),//0.10784314
	BLOND_WHITE			("white blond",	"",		0xFFF5E1,	0b10),//0.111111104

	TAUPE_SANDY			("sandy taupe", "", 	0x967117,	0b0),//0.11811024
	BRASS				("brass", "", 			0xB5A642,	0b0),//0.14492755

	SALMON_PINK			("pink salmon", "",		0xFF91A4,	0b0),//0.97121215

	RUBY				("ruby", "",			0xE0115F,	0b0),//0.93719804
	RUBY_RED			("ruby red", "",		0x9B111E,	0b0),//0.98429954
	RUBY_DEEP			("ruby deep", "",		0x843F5B,	0b0),//0.93236715

	ROSE_QUARTZ			("rose quartz", "",		0xAA98A9,	0b00000010000),//0.8425926

	ROSE_PINK			("rose pink", "",		0xFF66CC,	0b00000010000),//0.8888889
	ROSE_FRENCH			("french rose", "",		0xF64ABA,	0b00000010000),//0.8914729
	VERMILION			("vermilion",	"",		0xE3,	0x4254, 0b0),
	TAUPE_MEDIUM		("medium taupe", "",	0x674C47,	0b0),//0.026041666
	SALMON_DARK			("dark salmon", "",		0xE9967A,	0b0),//0.042042047
	ORANGE_RED			("orange red", "",		0xFF45, 0,		0b0),//0.045098037
	RUST				("rust", "",			0xB7410E,	0b0),//0.05029586
	TAUPE_PALE			("pale taupe", "",		0xBC987E,	0b0),//0.06989247
	TUSCAN				("tuscan", "",			0xFAD6A5,	0b00000010000),//0.09607843

	PINK_PERSIAN		("persian pink", "",	0xF77FBE,	0b0),//0.9125
	ROSE				("rose", "",			0xFF007F,	0b00000010000),//0.9169935
	RED_RUSTY			("rusty red", "",		0xDA2C43,	0b0),//0.97796935

	CORDOVAN			("cordovan", "",		0x893F45,	0b0),//0.9864865
	TAUPE_DEEP			("deep taupe", "",		0x7E5E60, 	0b0),//0.9895833



	TUSCAN_TAN			("tuscan tan", "",		0xA67B5B,	0b00000010000),//0.07111111
	TUSCAN_BROWN		("tuscan brown", "",	0x6F4E37,	0b00000010000),//0.06845238
	CINNAMON			("cinnamon", "",		0xD2691E,	0b0),//0.06944445

	CRIMSON				("crimson", "",		0xDC143C,		0b00001010000),//0.9666667

	CRIMSON_GLORY		("crimson glory", "",	0xBE0032,	0b00001010000),//0.95614034

	RED_DEVIL			("red devil", "",		0x860111,	0b00001010000),//0.9799499

	CRIMSON_SPANISH		("Spanish crimson", "",	0xE51A4C,	0b00001010000),//0.9589491
	RAZZMATAZZ			("razzmatazz", "",		0xE3256B,	0b00001010000),//0.9385965
	CARDINAL			("cardinal", "",		0xC41E3A,	0b0),//0.9718875
	CARMINE				("carmine", "",			0x960018,	0b0),//0.97333336
	ROSE_OLD			("old rose", "",		0xC08081,	0b00000010000),//0.9973958
	ROSE_VALE			("rose vale", "",		0xAB4E52,	0b00000010000),//0.9928315

	CARMINE_RICH		("rich carmine", "",	0xD70040,	0b0),//0.9503876

	CARMINE_SPANISH		("Spanish carmine", "",	0xD10047,	0b00001010000),//0.9433812
	CARMINE_PICTORIAL	("pictorial carmine", ""C30B4E,	0b0),//0.9393116
	CARMINE_JAPANESE	("Japanese carmine", ""9D2933,	0b0),//0.9856322

	CERISE				("cerise", "",			0xDE3163,	0b0),	//0.95183045
	CERISE_HOLLYWOOD	("Hollywood cerise", ""F400A1,	0b0),	//0.89002734
	IRRESISTABLE		("irresistable", "",	0xB3446C,	0b0),//0.9399399

	ORCHID				("orchid", "",			0xDA70D6,	0b00010000000),//0.8396226

	PEARL				("pearl",	"",			0xF0EAD6,	0b0),
	LAVENDER_BLUSH		("lavender blush",	"",	0xFFF0F5,	0b0),
	YELLOW_GREEN		("yellow green",	"",	0x9ACD32,	0b0),
	GREEN_YELLOW		("green yellow", "",	0xADFF2F,	0b0),
	PERIWINKLE			("periwinkle", "",			0xCCCCFF,	0b0),
	CHARTREUSE			("chartreuse", "",			0x7FFF0,	0b0),
	INDIGO_DARK			("dark indigo", "",			0x31062,	0b0),
	VIOLET_DARK			("dark violet", "",			0x423189,	0b0),
	COBALT				("cobalt", "",				0x047AB,	0b0),
	GREEN_SPRING		("spring green", "",		0x0FF7F,	0b0),
	CERULEAN			("color", "",				0x07BA7,	0b0),
	GREEN_FERN		("fern green", "",				0x4F7942,	0b0),
	GREEN_MOSS		("moss green", "",				0xADDFAD,	0b0),
	GREEN_MINT		("mint green", "",				0x98FF98,	0b0),
	GREEN_SEA		("sea green", "",				0x2E8B57,	0b0),

	//CHARTREUSE
//BLACK_S_WHITE 		("black and white", "", 	 				0b0010000000),
	//BLACK_S_YELLOW 		("black and yellow", "", 	 				0b10010000000),
	COLOR		("color", "",				0x000,	0b0),
	RAINBOW				("rainbow", "",			0x000000,	0b00010000000);


//human skin colors
/*
 * NEGRONI	("Negroni"FFDFC4, 0b1),
2	JUST_RIGHT	("just right	#F0D5BE, 0b1),//	just right
3	DESERT_SAND		("desert sand", "", 	0xEECEB3,	0b1),//	desert sand
4	CALICO			("calico", ""E1B899, 0b1)	calico
5	229	194	152	#E5C298	''
6	255	220	178	#FFDCB2	 Frangipani
7	229	184	143	#E5B887	Gold sand
8	229	160	115	#E5A073	apricot
9	231	158	109	#E79E6D	''
10	219	144	101	#DB9065	copperfield
11	206	150	124	#CE967C
12	198	120	86	#C67856
13	186	108	73	#BA6C49
14	165	114	87	#A57257
15	240	200	201	#F0C8C9
16	221	168	160	#DDA8A0
17	185	124	109	#B97C6D
18	168	117	108	#A8756C
19	173	100	82	#AD6452
20	92	56	54	#5C3836
21	203	132	66	#CB8442
22	189	114	60	#BD723C
23	112	65	57	#704139
24	163	134	106	#A3866A
25	135	4	0	#870400
26	113	1	1	#710101
27	67	0	0	#430000
28	91	0	1	#5B0001
29	48	46	46	#302E2E
30	0	0	0	#000000*/
"""




#BROWN:1:BURNT_UMBER:1:CINNAMON:1:COPPER:1:DARK_BROWN:1:DARK_PEACH:1:DARK_TAN:1:ECRU:1:PALE_BROWN:1:PALE_CHESTNUT:1:PALE_PINK:1:PEACH:1:PINK:1:RAW_UMBER:1:SEPIA:1:TAN:1:TAUPE_PALE:1:TAUPE_SANDY:1]

#sna
#WHITE MOTTLED_TAN_DARK_BROWN GREEN GREY STRIPES_BROWN_BLACK COPPER OLIVE:1:TAN:1:BLACK STRIPES_BLACK_WHITE STRIPES_BROWN_WHITE

#hor
#BLACK:1:BROWN:1:WHITE:1:GRAY:1:LIGHT_BROWN:1:DARK_BROWN:1:TAN:1:AUBURN:1:CHESTNUT:1:SLATE_GRAY:1:CREAM:1:CINNAMON:1:BUFF:1:BEIGE:1:CHOCOLATE:1:CHARCOAL:1:ASH_GRAY:1:RUSSET:1:IVORY:1:FLAX:1:PUMPKIN:1:GOLD:1:GOLDEN_YELLOW:1:GOLDENROD:1:COPPER:1:SAFFRON:1:AMBER:1:MAHOGANY:1:OCHRE:1:PALE_BROWN:1:RAW_UMBER:1:BURNT_SIENNA:1:BURNT_UMBER:1:SEPIA:1:DARK_TAN:1:PALE_CHESTNUT:1:DARK_CHESTNUT:1:TAUPE_PALE:1:TAUPE_DARK:1:TAUPE_SANDY:1:TAUPE_GRAY:1:TAUPE_MEDIUM:1:ECRU:1]

#cow
#BLACK:1:BROWN:1:WHITE:1:GRAY:1:LIGHT_BROWN:1:DARK_BROWN:1:TAN:1:AUBURN:1:CHESTNUT:1:SLATE_GRAY:1:CREAM:1:CINNAMON:1:BUFF:1:BEIGE:1:CHOCOLATE:1:CHARCOAL:1:ASH_GRAY:1:RUSSET:1:IVORY:1:FLAX:1:PUMPKIN:1:GOLD:1:GOLDEN_YELLOW:1:GOLDENROD:1:COPPER:1:SAFFRON:1:AMBER:1:MAHOGANY:1:OCHRE:1:PALE_BROWN:1:RAW_UMBER:1:BURNT_SIENNA:1:BURNT_UMBER:1:SEPIA:1:DARK_TAN:1:PALE_CHESTNUT:1:DARK_CHESTNUT:1:TAUPE_PALE:1:TAUPE_DARK:1:TAUPE_SANDY:1:TAUPE_GRAY:1:TAUPE_MEDIUM:1:ECRU:1]

#goa
#AMBER:1:AUBURN:1:BLACK:1:BROWN:1:BUFF:1:BURNT_SIENNA:1:BURNT_UMBER:1:CHARCOAL:1:CHESTNUT:1:CHOCOLATE:1:CINNAMON:1:COPPER:1:DARK_BROWN:1:DARK_CHESTNUT:1:DARK_TAN:1:ECRU:1:FLAX:1:GOLD:1:GOLDEN_YELLOW:1:GOLDENROD:1:LIGHT_BROWN:1:MAHOGANY:1:OCHRE:1:PALE_BROWN:1:PALE_CHESTNUT:1:PUMPKIN:1:RAW_UMBER:1:RUSSET:1:SAFFRON:1:SEPIA:1:TAN:1:TAUPE_DARK:1:TAUPE_GRAY:1:TAUPE_MEDIUM:1:TAUPE_PALE:1:TAUPE_SANDY:1]

#sea
#MOTTLED_BLACK_WHITE GRAY:100:WHITE

#dra
#RED:1:CRIMSON:1:CARMINE CERULEAN BLACK EMERALD:1:GREEN:1:FERN_GREEN:1:DARK_GREEN AZURE:1:AQUA:1:COBALT:1:CERULEAN:1:MEDNIGHT_BLUE

#dog
#	[TL_COLOR_MODIFIER:BLACK:1:BROWN:1:WHITE:1:GRAY:1:LIGHT_BROWN:1:DARK_BROWN:1:TAN:1:AUBURN:1:CHESTNUT:1:SLATE_GRAY:1:CREAM:1:CINNAMON:1:BUFF:1:BEIGE:1:CHOCOLATE:1:CHARCOAL:1:ASH_GRAY:1:RUSSET:1:IVORY:1:FLAX:1:PUMPKIN:1:GOLD:1:GOLDEN_YELLOW:1:GOLDENROD:1:COPPER:1:SAFFRON:1:AMBER:1:MAHOGANY:1:OCHRE:1:PALE_BROWN:1:RAW_UMBER:1:BURNT_SIENNA:1:BURNT_UMBER:1:SEPIA:1:DARK_TAN:1:PALE_CHESTNUT:1:DARK_CHESTNUT:1:TAUPE_PALE:1:TAUPE_DARK:1:TAUPE_SANDY:1:TAUPE_GRAY:1:TAUPE_MEDIUM:1:ECRU:1]



#COL_GREY
#COL_BLACK
#COL_


class ColorChance:
    def __init__(self, colorList, chanceList):
        if len(colorList) != len(chanceList):
            raise IndexError('The length of colorList ({0}) is diffrent from the length of chanceList ({1})'.format( len(colorList), len(chanceList) ) )
        self.colorList = tuple([ALL_COLORS_DICT[c] for c in colorList])

        self.chanceList = tuple(chanceList)

        #print(self.colorList[0][0])
        #raise IndexError('test run. value of self.colorList[0] is: {}'.format(self.colorList[0]))
    @property
    def randomColor(self):
        return choices(self.colorList, cum_weights=self.chanceList)[0]
