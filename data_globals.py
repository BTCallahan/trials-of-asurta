from random import randint
import string, re
from os import path
from typing import Dict

FILE_LOCATION_NAME = str(path.dirname(path.abspath(__file__)))

def checktypeOfList(listOfItems, itemType):
    for i in listOfItems:
        assert isinstance(i, itemType)

def checkForMandatoryInfo(textToLookFor, stringToCheck, dataType, fileName, entryName, isList=False, listLength=1):
    '''textToLookFor = A string to search for. If it is not found, an AssertionError will be raised.
stringToCheck = a string to check to see if it contaions textToLookFor. 
dataType = if textToLookFor is found within stringToCheck, then the resulting text will be cast to the data type spefified. 
Can be \'INT\' or \'FLOAT\'. Anything else will result in resulting text being cast to a string.
fileName = The name of the file being searched. Used for error reporting.
entryName = The name of the entry being searched. Used for error reporting.
isList = checks to see if 
listLength = the specified length of the list. If isList is true and the length of the list is diffrent, an IndexError will be raised.
Set to -1 to disable checking.
'''
    castType = str
    if dataType == 'INT':
        castType = int
    elif dataType== 'FLOAT':
        castType = float

    if re.search(textToLookFor, stringToCheck):

        searchResult = re.findall(textToLookFor + '(.+)\n', stringToCheck)

        #multiMatches = re.findall(textToLookFor + '(:(.+):)')
        


        if isList:
            splitResult = re.split(r'[:]', searchResult[0])
            #splitResult = 

            if listLength > 0 and len(splitResult) != listLength:

                raise IndexError('''Error while reading {}, entry {}. The length of the 
array the follows the text {} is not equal to the length specified ({}).'''.format(
                    fileName, entryName, textToLookFor, listLength))
            # strip('\'[]')
            return [castType(s.strip('\'[]')) for s in splitResult]

        else:

            searchResult = re.findall(textToLookFor + '(.+)\n', stringToCheck)

            return castType(searchResult[0])
    
    else:
        raise AttributeError('Error while reading {}, entry {}. The value ({}) was not found'.format(fileName, entryName, textToLookFor))


def checkForOptionalFlag(textToLookFor, stringToCheck):
    return re.search(textToLookFor, stringToCheck)

def checkForOptionalInfo(textToLookFor, stringToCheck, dataType, default, isList=False, acceptNewlines=False):
    'acceptNewlines = used for multiline string targets'
    castType = str
    if dataType == 'INT':
        castType = int
    elif dataType== 'FLOAT':
        castType = float

    if re.search(textToLookFor, stringToCheck) is not None:
        endRegex = r'(.+)\n'
        if acceptNewlines:
            endRegex = r'[\s\S]+'

        searchResult = re.findall(textToLookFor + endRegex, stringToCheck)

        #searchResult = re.search(textToLookFor + endRegex, stringToCheck)
        #searchResult.group(0)
        if isList:
            
            try:
                splitResult = re.split(':', searchResult)
            except TypeError:
                splitResult = searchResult
            return [castType(s) for s in splitResult]

        else:


            return castType(searchResult[0])

    else:
        return default


ALPHABET = 'abcdefghijklmnopqrstuvwxyz'

DAMAGE_TYPES = ('PIRCE', 'BLUNT', 'CUT', 'STAMNA', 'MANA', 'HEAT', 'COLD', 'BLAST', 'ELEC', 'RADIATION')

regexValid = string.ascii_uppercase + string.digits + '_.:'

SIDE_PLAYER = 0
SIDE_RIVAL_ADVENTURER = 1
SIDE_WILDLIFE = 2
SIDE_OUTISDER = 3
SIDE_UNDEAD = 4
SIDE_ELEMENTAL = 5

ENEMY_SIDE_DICT = {
    'SIDE_PLAYER' : frozenset(['SIDE_RIVAL_ADVENTURER', 'SIDE_WILDLIFE', 'SIDE_OUTISDER', 'SIDE_UNDEAD', 'IDE_ELEMENTAL']),
    'SIDE_RIVAL_ADVENTURER' : frozenset(['SIDE_PLAYER', 'SIDE_RIVAL_ADVENTURER', 'SIDE_WILDLIFE', 'SIDE_OUTISDER', 'SIDE_UNDEAD', 'SIDE_ELEMENTAL']),
    'SIDE_WILDLIFE' : frozenset(['SIDE_PLAYER', 'SIDE_RIVAL_ADVENTURER', 'SIDE_UNDEAD']),
    'SIDE_OUTISDER' : frozenset(['SIDE_PLAYER', 'SIDE_RIVAL_ADVENTURER', 'SIDE_UNDEAD']),
    'SIDE_UNDEAD' : frozenset(['SIDE_PLAYER', 'SIDE_RIVAL_ADVENTURER', 'SIDE_WILDLIFE', 'SIDE_OUTISDER']),
    'SIDE_ELEMENTAL' : frozenset(['SIDE_PLAYER', 'SIDE_RIVAL_ADVENTURER'])
}

MOVE_NONE = 0
MOVE_VERTICAL = 1
MOVE_HORIZONTAL = 2
MOVE_DIAGIONAL = 3

"""
GEN_NONE = 0
GEN_MALE = 1
GEN_FEMALE = 2
GEN_MULTI = 3s
GEN_YOU = 4
"""


def aVsAn(string):
    s = string.lower()
    if s[0] in 'aeiou' or s[:3] == 'hou':
        return 'an'
    return 'a'


def pronounDict(name, subject, object, dependentPos, independentPos, reflexive, hashave='has', isare='is'):
    return {'name' : name, 'subject' : subject, 'object' : object,
    'dependentPos' : dependentPos, 'independentPos' : independentPos,
    'reflexive' : reflexive, 'hashave' : hashave, 'isare' : isare}


def buildPronounDict(filename):
    pDict = {'GEN_NONE': pronounDict('Nuter', 'it', 'it', 'its', 'its', 'itself')}

    p = open(FILE_LOCATION_NAME + filename, 'r')

    pList = re.split(r'\n', p.read())

    for pr in pList:

        if len(pr) > 0:
            spl = re.split(r':', pr)

            key, name, subject, object, dependentPos, independentPos, reflexive, hashave, isare = spl

            pDict[key] = pronounDict(name, subject, object, dependentPos, independentPos, reflexive,
                                                   hashave, isare)

    p.close()

    return pDict

PRONOUN_DICT = buildPronounDict('/library/pronouns.txt')



ALL_ITEM_TYPES = ('HEAD', 'UPPER_BOD', 'HANDS', 'LOWER_BOD', 'FEET', 'WEAPON', 'LAUNCHER',
                  'AMNUNITION', 'SHIELD', 'MISC', 'KNOT', 'STAFF', 'GLYPH', 'TALISMAN', 'FOOD', 'CORPSE')

ALL_IMPORTANT_ITEM_TYPES = ALL_ITEM_TYPES[:-1]

ALL_ITEM_SET = frozenset(ALL_ITEM_TYPES)

#ARMOR = ('HEAD', 'UPPER_BOD', 'HANDS', 'LOWER_BOD', 'FEET')

ARMOR = {'HEAD', 'UPPER_BOD', 'HANDS', 'LOWER_BOD', 'FEET'}

WIELDABLE_SET = frozenset(['WEAPON', 'LAUNCHER', 'SHIELD', 'AMNUNITION', 'MISC'])

# EQUIPABLE = ARMOR | WIELDABLE

ARMOR_SET = frozenset(ARMOR)

EQUIPABLE = ('HEAD', 'UPPER_BOD', 'HANDS', 'LOWER_BOD', 'FEET', 'WEAPON', 'LAUNCHER', 'AMNUNITION', 'SHIELD', 'MISC')

EQUIPABLE_SET = frozenset(EQUIPABLE)

ACTIVATIABLE = ('KNOT', 'STAFF', 'TALISMAN', 'GLYPH', 'FOOD')

ACTIVATIABLE_SET = frozenset(ACTIVATIABLE)

statBonusDict = {'SKILL_MEELE' : ('STAT_STR', 'STAT_AGL'),
                'SKILL_RANGED' : ('STAT_DEX', 'STAT_PER'),
                'SKILL_THROWN' : ('STAT_PER', 'STAT_AGL'),
                'SKILL_ARMOR' : ('STAT_STR', 'STAT_END'),
                'SKILL_BLOCKING' : ('STAT_END', 'STAT_WIL'),
                'SKILL_DODGING' : ('STAT_AGL', 'STAT_PER'),
                'SKILL_STEALTH' : ('STAT_AGL', 'STAT_DEX'),
                'SKILL_DETECT_STEALTH' : ('STAT_PER', 'STAT_MAG'),
                'SKILL_TRAPS' : ('STAT_DEX', 'STAT_MIN'),
                'SKILL_DETECT_TRAPS' : ('STAT_PER', 'STAT_MIN'),
                'SKILL_RESIST_MAGIC' : ('STAT_WIL', 'STAT_END'),
                'SKILL_MAGIC_DEVICE' : ('STAT_MAG', 'STAT_DEX'),
                'SKILL_SPELLCRAFT' : ('STAT_MAG', 'STAT_MIN')}

ARMOR_CHANGE_COST_DICT = {'HEAD': 1.2,
                          'UPPER_BOD': 1.8,
                          'HANDS': 1.3,
                          'LOWER_BOD': 1.8,
                          'FEET': 1.2,
                          'WEAPON': 1.05,
                          'LAUNCHER': 1.15,
                          'AMNUNITION': 1.35,
                          'SHIELD': 1.1,
                          'MISC': 1.05
                          }

def generateRatio(*args):
    subtotal = 0

    total = sum(args)
    for a in args:
        subtotal += a
        yield subtotal / total


ITEM_RATIO_DICT = {k: v for (k, v) in zip( ALL_ITEM_TYPES, list(generateRatio(
    5, 5, 5, 5, 5, 15, 10, 30, 8, 4, 8, 4, 3, 12, 30)))}

class StatusCondition:

    def __init__(self, name, typeOfCondition, value):
        self.name = name
        self.typeOfCondition = typeOfCondition
        self.value = value




class BodyPart:
    def __init__(self, name, slot, description, partType, nullType=False):
        self.__name = name
        self.__slot = slot
        self.__description = description
        self.__partType = partType
        self.__nullType = nullType

    @property
    def name(self):
        return self.__name

    @property
    def slot(self):
        return self.__slot

    @property
    def description(self):
        return self.__description

    @property
    def partType(self):
        return self.__partType

    @property
    def nullType(self):
        return self.__nullType

    def __str__(self):
        return self.__description

    def __eq__(self, o):
        return hash(self) == hash(o)

    def __hash__(self):
        return hash((self.slot, self.description, self.partType,
        self.nullType))

    """
    def __str__(self):
        return '{} {} {}'.format(self.slot, self.description, self.partType)
    """


def buildBodyPartDict(filename):

    bpDict = dict()

    b = open(FILE_LOCATION_NAME + filename, 'r')

    bList = re.split(r'\n', b.read())

    for bp in bList:

        if len(bp) > 0:

            spl = re.split(r':', bp)

            if len(spl) == 5:
                key, slot, description, number, isNullStr = spl
                null = isNullStr == 'True'
            elif len(spl) == 4:
                key, slot, description, number, = spl
                null = False
            else:
                raise ValueError('There are {} items in the body string ({})'.format(len(spl), bp))


            bpDict[key] = BodyPart(key, slot, description, number, null)

    b.close()

    return bpDict

def rollAttack(dice, diceSides):
    if dice <= 1:
        return randint(1, diceSides)
    else:
        return rollAttack(dice - 1, diceSides)

ALL_BODY_PARTS_DICT = buildBodyPartDict('/library/body.txt')

ALL_STATS = ('STAT_STR', 'STAT_END', 'STAT_AGL', 'STAT_DEX', 'STAT_MIN', 'STAT_WIL', 'STAT_PER', 'STAT_MAG')

STAT_NAMES = ('Str', 'End', 'Agi', 'Dex', 'Min', 'Wil', 'Per', 'Mag')

"""
STAT_STR affects the following traits:
    health, ranged/thrown weapon range, carrying ability, meele damage
It also affects the following skills:
    meele, armor
STAT_END affects the following traits:
    health, stamna, health regen, stamna regen
It also affects the following skills:
    armor, blocking
STAT_AGL affects the following traits:
    thrown
It also affects the following skills:
    meele, dodging, , stealth
STAT_DEX affects the following traits:

It also affects the following skills:
    ranged, disarm traps, open locks
STAT_MIN affects the following traits:

It also affects the following skills:
    traps, detect traps, spellcraft
STAT_WIL affects the following traits:
    stamn, magic, stamna regen, magic regen
It also affects the following skills:
    resist magic
STAT_PER affects the following traits:

It also affects the following skills:
    detect traps, detect stealth, ranged
STAT_MAG affects the following traits:
    magic effectiveness, magic
It also affects the following skills:
    spellcraft, magic device
"""

"""
SKILL_MEELE = 0
SKILL_RANGED = 1
SKILL_THROWN = 2
SKILL_ARMOR = 3
SKILL_BLOCKING = 4

SKILL_DODGING = 5
SKILL_STEALTH = 6
SKILL_DETECT_STEALTH = 7
SKILL_TRAPS = 8
SKILL_DETECT_TRAPS = 9

SKILL_RESIST_MAGIC = 10
SKILL_MAGIC_DEVICE = 11
SKILL_SPELLCRAFT = 12
"""

ALL_SKILLS = ('SKILL_MEELE', 'SKILL_RANGED', 'SKILL_THROWN',
'SKILL_ARMOR', 'SKILL_BLOCKING',
'SKILL_DODGING', 'SKILL_STEALTH', 'SKILL_DETECT_STEALTH', 'SKILL_TRAPS',
'SKILL_DETECT_TRAPS',
'SKILL_RESIST_MAGIC', 'SKILL_MAGIC_DEVICE', 'SKILL_SPELLCRAFT')

SKILL_NAMES = ('Meele', 'Ranged', 'Thrown', 'Armor', 'Block',
'Dodge', 'Stealth', 'Observe', 'Disarm', 'Detect', 'Resist', 'Device', 'Thuam')

stringFloatDict = Dict[str, float]
stringIntDict = Dict[str, int]


def check_if_entity_can_use_equip_item(entity, item):

    try:
        item_type = item.baseData.typeOfItem
    except AttributeError:
        item_type = item.typeOfItem

    try:
        bodySlotTypesAllowed = item.baseData.bodySlotTypesAllowed
    except AttributeError:
        bodySlotTypesAllowed = item.bodySlotTypesAllowed

    try:
        bodyDict = entity.species.bodyDict
    except AttributeError:
        bodyDict = entity.bodyDict

    if item_type in WIELDABLE_SET:

        return True

    if item_type in ARMOR_SET:

        name = bodyDict[item_type].name

        return bodyDict[item_type].name in bodySlotTypesAllowed

    return False

def check_if_entity_can_wear_armor(entity, item):
    try:
        item_type = item.baseData.typeOfItem
    except AttributeError:
        item_type = item.typeOfItem

    if item_type not in ARMOR_SET:
        return False

    try:
        bodySlotTypesAllowed = item.baseData.bodySlotTypesAllowed
    except AttributeError:
        bodySlotTypesAllowed = item.bodySlotTypesAllowed

    try:
        bodyDict = entity.species.bodyDict
    except AttributeError:
        bodyDict = entity.bodyDict

    return bodyDict[item_type].name in bodySlotTypesAllowed



