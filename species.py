from random import choice
import re, types
from math import fsum
from color_factory import ALL_COLORS_DICT
from magic_effects import ALL_EFFECT_DICT
from data_globals import ALL_BODY_PARTS_DICT, stringFloatDict, stringIntDict, PRONOUN_DICT, \
ALPHABET, rollAttack, ALL_STATS, ALL_SKILLS, STAT_NAMES, \
checkForMandatoryInfo, checkForOptionalInfo, regexValid, \
FILE_LOCATION_NAME
from color_factory import ColorChance, ALL_COLORS_DICT
from game_items import doNothing
from game_items import getListOfItemsSuitbleForDepth, getSuitbleItemsByType, \
UniversalItem, UniversalGameItem, getLongestItemName, DUMMY_ITEM

ARMOR = ('HEAD', 'UPPER_BOD', 'HANDS', 'LOWER_BOD', 'FEET')

class BodyMaterial:
    def __init__(self, name, descriptor, key):
        self.name = name
        self.capName = name.capitalize()
        self.descriptor = descriptor
        self.key = key

    def __str__(self):
        return self.name

    def get_descriptor_color(self, color):
        return ' '.join([self.descriptor, '{}'.format(color), self.name])

    def __hash__(self):
        return hash((self.name, self.descriptor))

    def __eq__(self, o):
        if isinstance(o, BodyMaterial):
            return self.name == o.name
        else:
            return hash(self) == hash(o)

ALL_MATERIAL_DICT = {
'MAT_SKIN' : BodyMaterial('skin', 'covered in', 'MAT_SKIN'),
'MAT_FUR' : BodyMaterial('fur', 'covered in', 'MAT_FUR'),
'MAT_CHITIN' : BodyMaterial('chitin', 'covered in', 'MAT_CHITIN'),
'MAT_SCALES' : BodyMaterial('scales', 'covered in', 'MAT_SCALES'),
'MAT_FEATHERS' : BodyMaterial('feathers', 'covered by', 'MAT_FEATHERS'),
'MAT_CLAY' : BodyMaterial('clay', 'made from', 'MAT_CLAY'),
'MAT_NONE' : BodyMaterial('', '', 'MAT_NONE')
}

#ALL_MATERIALS = (MAT_SKIN, MAT_FUR, MAT_CHITIN, MAT_SCALES, MAT_FEATHERS)

"""
B:HEAD:'UPPER_BOD':HANDS:LOWER_BOD:FEET
S:1:1
M:
C:
"""

#species flags:
"""
FLAG_NONE = b'00000000'
FLAG_FEY =  b'00000001'
FLAG_REPTILE =  b'00000010'
FLAG_POWER =  b'00000100'
FLAG_BEASTKIN =  b'00001000'
"""

FLAG_NONE =     1 << 0
FLAG_FEY =      1 << 1
FLAG_REPTILE =  1 << 2
FLAG_POWER =    1 << 3
FLAG_BEASTKIN = 1 << 4

TRAIT_COLDBLOOD = 1 << 0
TRAIT_CANNIBLE = 1 << 1
#TRAIT_

def combineFlags(*flags):
    baseFlag = b'00000000'
    for f in flags:
        baseFlag = baseFlag | f
    return baseFlag

"""
undead:
"""

def newSkillDict(*skillValues):
    if len(ALL_SKILLS) != len(skillValues):
        raise IndexError('The number of skill values entered ({}) is not equal to the number of avaliable skills.'.format(len(skillValues)))

    return {k: v for (k, v) in zip(ALL_SKILLS, skillValues)}
#ALL_STATS


def newStatDict(*statValues):
    if len(ALL_STATS) != len(statValues):
        raise IndexError('The number of stat values entered {} is not equal to the number of avaliable stats {}.'.format(len(statValues), len(ALL_STATS)))

    return {k: v for (k, v) in zip(ALL_STATS, statValues)}

#VOWELS = ()

class Species:
    """body dict is a string : string dictionary
    bodyMaterialDict is a string : string dictionary
    colorChanceDict is a string : ColorChance dictionary"""

    BASE_MAX_FOOD = 5.0 * 1.0 * 24.0 * 30.0 #2592000.0
    BASE_HEALTH_STAMNA_MANA = 40

    def __init__(self, name: str, symbol, genders, size: int,
        bodyDict,
                 descriptiveBodyDict,
                 bodyMaterialDict, colorChanceDict,

        landSpeed: float, waterSpeed: float, airSpeed: float,
        
        maxHealth, maxStamna, maxMagic, maxFood,
        regenHealth, regenStamna, regenMagic, hungerRate,
                 baseStats: stringIntDict,
                 skillAppitude: stringFloatDict,

        depthEnountered=0, heatVision=0, glamor=0, naturalArmor=0, equipSize = -1,
        description = [' ', ' '],
        innateAbilites = []):

        self.symbol = symbol
        self.name = name
        self.genders = tuple(genders)
        self.size = size
        if equipSize < 0:
            self.equipSize = self.size
        else:
            self.equipSize = equipSize
        # .bodyDict is a string : BodyPart dictionary
        self.bodyDict = {k: ALL_BODY_PARTS_DICT[v] for (k, v) in bodyDict.items()}
        # self.bodyMaterialDict is a string : BodyMaterial dictionary
        self.bodyMaterialDict = {k: ALL_MATERIAL_DICT[v] for (k, v) in bodyMaterialDict.items()}
        #print(self.name)

        self.descriptiveBodyDict = {k: ALL_BODY_PARTS_DICT[v] for (k, v) in descriptiveBodyDict.items()}

        self.miscSlots = 6

        #print(' '.join([str(s) for s in self.bodyMaterialDict.values()]))
        #'''A dict comprised of strings for keys and ColorChance for values
        self.colorChanceDict = colorChanceDict

        self.landSpeed = landSpeed
        self.waterSpeed = waterSpeed
        self.airSpeed = airSpeed

        self.regenHealth = regenHealth
        self.regenStamna = regenStamna
        self.regenMagic = regenMagic
        self.hungerRate = hungerRate

        self.baseStats = baseStats
        self.skillAppitude = skillAppitude

        self.maxHealth = int(maxHealth * self.BASE_HEALTH_STAMNA_MANA)
        self.maxStamna = int(maxStamna * self.BASE_HEALTH_STAMNA_MANA)
        self.maxMagic = int(maxMagic * self.BASE_HEALTH_STAMNA_MANA)
        self.maxFood = maxFood * self.BASE_MAX_FOOD

        self.depthEnountered = depthEnountered
        self.heatVision = heatVision
        self.glamor = glamor
        self.naturalArmor = naturalArmor
        self.description = ' '.join(description.split('\n')).replace('DESCRIPTION:', '')
        self.innateAbilites = tuple(innateAbilites)

        self.corpseItem = UniversalItem.newCorpse(self)
        #    UniversalItem(name + ' corpse', 'WHITE', size * 5, 0, 0, '&', 0, None, 'CORPSE', ['NONE'])

        # print(type(self.innateAbilites))
        self.appearence = self.describe

        self.__hash = hash((name, symbol, 
        self.genders, 
        tuple(self.bodyDict.values()), 
        tuple(self.bodyMaterialDict.values()),
        tuple(self.colorChanceDict.values()), 
        tuple(self.colorChanceDict.keys()), 
        regenHealth, regenStamna, regenMagic, hungerRate,
        tuple(self.baseStats.values()), 
        tuple(self.skillAppitude.values()), 
        maxHealth, maxStamna, maxMagic, maxFood, 
        depthEnountered, heatVision, glamor, naturalArmor, 
        self.description, 
        self.innateAbilites
        ))

    def __hash__(self):
        """
        return hash((self.symbol, self.name, self.genders,
self.bodyDict.values(), self.moveSpeed, self.swimSpeed, self.maxHealth,
self.maxStamna, self.maxMagic, self.maxFood, self.depthEnountered,
self.hungerRate, self.baseStats.values(), self.skillAppitude.values(),
self.heatVision, self.glamor, self.bodyMaterialDict.values(), self.description))
        """
        return self.__hash

    def __eq__(self, o):
        return hash(self) == hash(o)

    @property
    def getColorDict(self):
        #returns a dictionary with bodyMaterials for keys and colorHelper for values
        #key is a BodyMaterial, key.key is a string

        try:
            d = {
                key: self.colorChanceDict[key.key].randomColor 
                for key in self.bodyMaterialDict.values() 
                if key.key in self.colorChanceDict
                }
        except KeyError:
            s = ' '.join([str(t.key) for t in self.bodyMaterialDict.values()])
            print(s)
            s = ' '.join([str(t) for t in self.bodyMaterialDict.keys()])
            print(s)
            s = ' '.join([str(t) for t in self.colorChanceDict.values()])
            print(s)
            s = ' '.join([str(t) for t in self.colorChanceDict.keys()])
            print(s)
            
            raise AttributeError('self.colorChanceDict keys: {}, self.bodyMaterialDict values: {}'.format(self.colorChanceDict.keys(), self.bodyMaterialDict.values()))
        #dc = {key:value.randomColor for (key, value) in d.items()}
        """
        if self.colorChanceDict[MAT_SKIN] != None:
            d[MAT_SKIN] = self.colorChanceDict[MAT_SKIN].randomColor
        if self.colorChanceDict[MAT_FUR] != None:
            d[MAT_FUR] = self.colorChanceDict[MAT_FUR].randomColor
        if self.colorChanceDict[MAT_CHITIN] != None:
            d[MAT_CHITIN] = self.colorChanceDict[MAT_CHITIN].randomColor
        if self.colorChanceDict[MAT_SCALES] != None:
            d[MAT_SCALES] = self.colorChanceDict[MAT_SCALES].randomColor
        if self.colorChanceDict[MAT_FEATHERS] != None:
            d[MAT_FEATHERS] = self.colorChanceDict[MAT_FEATHERS].randomColor
        """


        return d

    def canWearArmor(self, armorItem):
        try:
            #print()
            if armorItem.baseData.typeOfItem not in ARMOR:
                return False
            return self.bodyDict[armorItem.baseData.typeOfItem].partType in armorItem.baseData.bodySlotTypesAllowed
        except AttributeError:
            if armorItem.typeOfItem not in ARMOR:
                return True
            return self.bodyDict[armorItem.typeOfItem].partType in armorItem.bodySlotTypesAllowed

    @property
    def describe(self):
        des = []
        #heshe hashave torsocolor torsomat headcolor headmat legcolor legmat feetcolor feetmat

        onlyOneMaterialType = self.bodyMaterialDict['HEAD'] == self.bodyMaterialDict['UPPER_BOD'] == \
                              self.bodyMaterialDict['HANDS'] == self.bodyMaterialDict['LOWER_BOD'] == \
                              self.bodyMaterialDict['FEET'] == self.bodyMaterialDict['WINGS'] == \
                              self.bodyMaterialDict['TAIL']

        if self.bodyMaterialDict['HEAD'] == self.bodyMaterialDict['UPPER_BOD']:
            des.append('{heshecap} {hashave} a')
            des.append('{head} head on top of a torso that has {torso}.'.format(
            head=self.bodyDict['HEAD'], torso=self.bodyDict['UPPER_BOD']))
        else:
            des.append('{heshecap} {hashave} a')
            des.append('{head} head covered in'.format(head=self.bodyDict['HEAD']))
            des.append('{headcolor}')
            des.append('{headmat} on top of a'.format(headmat=self.bodyMaterialDict['HEAD']))
            des.append('{torsocolor}')
            des.append('{torsomat} torso that has {torso}'.format(torsomat=self.bodyMaterialDict['UPPER_BOD'], torso=self.bodyDict['UPPER_BOD']))
        if not self.bodyDict['UPPER_BOD'].nullType:
            if self.bodyMaterialDict['UPPER_BOD'] == self.bodyMaterialDict['WINGS']:
                des.append('{wings}.'.format(wings=self.descriptiveBodyDict['WINGS']))
            else:
                des.append('{wings} covered in'.format(wings=self.descriptiveBodyDict['WINGS']))
                des.append('{wingcolor}')
                des.append('{wingmat}.'.format(wingmat=self.bodyMaterialDict['WINGS']))

        if self.bodyMaterialDict['HANDS'] == self.bodyMaterialDict['UPPER_BOD']:
            des.append('{heshecap} {hashave}')
            des.append('two {hands}.'.format(hands=self.bodyDict['HANDS']))
        else:
            des.append('{heshe} {hashave} two')
            des.append('{hands}'.format(hands=self.bodyDict['HANDS']))
            des.append('covered in {handcolor}')
            des.append('{handmat}.'.format(handmat=self.bodyMaterialDict['HANDS']))


        if self.bodyMaterialDict['LOWER_BOD'] == self.bodyMaterialDict['UPPER_BOD']:
            des.append('{heshecap} {hashave}')
            des.append('{legs} legs'.format(legs=self.bodyDict['LOWER_BOD']))
        else:
            des.append('From the waist down, {heshe} {hashave} {legcolor}')
            des.append('{legmat} {legs} legs'.format(legmat=self.bodyMaterialDict['LOWER_BOD'], legs=self.bodyDict['LOWER_BOD']))

        if not self.bodyDict['FEET'].nullType:
            if self.bodyMaterialDict['LOWER_BOD'] == self.bodyMaterialDict['FEET']:
                des.append('ending in {feet}'.format(feet=self.bodyDict['FEET']))
            else:
                des.append('ending in {feetcolor}')
                des.append('{feetmat} {feet}'.format(feetmat=self.bodyMaterialDict['FEET'], feet=self.bodyDict['FEET']))

        if not self.descriptiveBodyDict['TAIL'].nullType:
            if self.bodyMaterialDict['LOWER_BOD'] == self.bodyMaterialDict['TAIL']:
                des.append('Sprouting from {hisher} rear end is a')
                des.append('{tail}.'.format(tail=self.descriptiveBodyDict['TAIL']))
            else:
                des.append('Sprouting from {hisher} rear end is a')
                des.append('{tail} covered in'.format(tail=self.descriptiveBodyDict['TAIL']))
                des.append('{tailcolor}')
                des.append('{tailmat}'.format(tailmat=self.bodyMaterialDict['TAIL']))
        if onlyOneMaterialType:
            des.append('\n{heshecap} {isare} covered in {torsocolor}')
            des.append('{torsomat}.'.format(torsomat=self.bodyMaterialDict['UPPER_BOD']))

        #print(len(des))
        return ' '.join(des)


#('Meele', 'Ranged', 'Thrown', 'Armor', 'Block',
#'Dodge', 'Stealth', 'Observe', 'Disarm', 'Detect',
#'Resist', 'Device', 'Thuam')

#PLAYABLE_SPECIES = tuple([s for s in ALL_SPECIES if s.depthEnountered == 0])

def buildSpeciesList(fileName):

    allSpecies = []

    def colorGenerator(text, materialName, speciesName):

        def gen(numList):
            prev = 0
            for n in numList:
                n+= prev
                yield n + prev

        splitText = re.split(':', text)

        colorNames = splitText[:len(splitText) // 2:2]

        colorNumbers = splitText[1:len(splitText) // 2:2]

        if len(colorNames) != len(colorNames):
            raise IndexError('''Error while reading species.txt, entry {}, 
material {}: the number of colors ({}) does not match the number of value 
weights ({}).'''.format(speciesName, materialName, colorNames, colorNumbers))

        #colors = [ALL_COLORS_DICT[c] for c in colorNames]

        colorProbs = list(gen(colorNumbers))

        return ColorChance(colorNames, colorProbs)

    s = open(FILE_LOCATION_NAME + fileName, 'r')

    a = s.read()

    sList = re.split('NAME:', a)

    #print('preparing to create species list')

    for sp in sList:

        if re.match('(.+)\n', sp) and sp[0] != '#':

            i = re.findall('^(.+)\n', sp)

            allCapsName, name, symbol = re.split(':', i[0])

            def speciesMandatoryCheck(textToLookFor, dataType, isList=False, listLength=-1):
                return checkForMandatoryInfo(textToLookFor, sp, dataType, 'species.txt', allCapsName, isList, listLength)
            
            def speciesOptionalCheck(textToLookFor, dataType, default, isList=False, acceptNewlines=False):
                return checkForOptionalInfo(textToLookFor, sp, dataType, default, isList, acceptNewlines)

            capName = name.upper()

            maxValues = speciesMandatoryCheck('MAX_VALUES:', 'FLOAT', True, 4)

            regeneration = speciesMandatoryCheck('REGENERATION:', 'FLOAT', True, 4)

            regenHealth, regenStamna, regenMagic, hungerRate = regeneration

            stats = speciesMandatoryCheck('STATS:', 'INT', True, len(ALL_STATS))

            statDict = {key: int(value) for key, value in zip(ALL_STATS, stats)}

            genders = speciesMandatoryCheck('GENDERS:', 'STR', True, -1)

            combatSkills = speciesMandatoryCheck('COMBAT_SKILLS:', 'FLOAT', True, 5)

            rogueSkills = speciesMandatoryCheck('ROGUE_SKILLS:', 'FLOAT', True, 5)

            magicSkills = speciesMandatoryCheck('MAGIC_SKILLS:', 'FLOAT', True, 3)

            skills = combatSkills + rogueSkills + magicSkills

            skillDict = {key: float(value) for (key, value) in zip(ALL_SKILLS, skills)}

            maxHealth, maxStamna, maxMagic, maxFood = maxValues

            body = speciesMandatoryCheck('BODY:', 'STR', True, len(ARMOR))

            #constructs a string : string dictionary

            bodyDict = {key: value for (key, value) in zip(ARMOR, body)}

            descriptiveBody = speciesMandatoryCheck('DESCRIPTIVE_BODY:', 'STR', True, 2)

            descriptiveBodyDict = {key: value for (key, value) in zip(('WINGS', 'TAIL'), descriptiveBody)}

            speed = speciesMandatoryCheck('SPEED:', 'FLOAT', True, 3)

            landSpeed, waterSpeed, airSpeed = speed

            size = speciesMandatoryCheck('SIZE:', 'INT')

            equipSize = speciesOptionalCheck('EQUIP_SIZE:', 'INT', size)

            bms = speciesMandatoryCheck('BODY_MATERIALS:', 'STR', True, 5)

            dbms = speciesMandatoryCheck('DESCRIPTIVE_BODY_MATERIALS:', 'STR', True, 2)

            #constructs a string : string dictionary

            bodyMats = {k:v for (k, v) in zip(ARMOR, bms)}

            for k, v in zip(('WINGS', 'TAIL'), dbms):
                bodyMats[k] = v

            # descriptiveBodyMats = {k:v for (k, v) in zip(('WINGS', 'TAIL'), dbms)}

            colorChance = dict()

            for r in re.finditer(r'COLOR:(.+)\n', sp):

                #print('color result:')
                #print(r.groups())
                

                #a = re.findall(r':[' + regexValid + r']$', r.group(0))
                #print(a)
                a = r.group(0)
                aSplit = re.split(r'[:]', a)
                if len(aSplit) % 2 != 0:
                    print(a)
                    print(aSplit)
                    raise IndexError('length of list is {}'.format(len(aSplit)))
                
                mat = ALL_MATERIAL_DICT[aSplit[1]]

                colors = aSplit[2::2]

                values = [int(v) for v in aSplit[3::2]]

                #creates a string : ColorChance dictionary

                colorChance[mat.key] = ColorChance(colors, values)
            
            for e in colorChance.keys():
                if e not in bodyMats.values():
                    raise KeyError('''Check the body materials keys {} and values {} 
and color materials keys {} and values {} for entry {}'''.format(
                        ' '.join([str(a) for a in bodyMats.keys()]),
                        ' '.join([str(a) for a in bodyMats.values()]),
                        ' '.join([str(a) for a in colorChance.keys()]),
                        ' '.join([str(a) for a in colorChance.values()]),
                        
                        name))

            

            """
            colorChance = {k:colorGenerator(
                re.findall('COLOR:' + k + '-\n', sp), k, capName)
                 for k in ALL_MATERIAL_DICT.keys() if re.search('COLOR:' + k, sp)}
            """
                
            #speciesOptionalCheck('COLOR:' + k, 'STR', [], True) for k in ALL_MATERIAL_DICT.keys()}

            glamor = speciesOptionalCheck('GLAMOR:', 'INT', 0)

            naturalArmor = speciesOptionalCheck('NATURAL_ARMOR:', 'INT', 0)

            heatVision = speciesOptionalCheck('HEAT_VISION:', 'INT', 0)

            depthEnountered = speciesOptionalCheck('DEPTH:', 'INT', 0)

            maxHealth, maxStamna, maxMagic = [int(m) for m in maxValues[:-1]]

            maxFood = maxValues[3]

            innateAbilitesStr = speciesOptionalCheck('ABILITIES:', 'STR', [], True)

            #print(innateAbilitesStr)
            #print(len(innateAbilitesStr))
            #print(type(innateAbilitesStr))
            """
            if len(innateAbilitesStr) == 1:
                innateAbilites = ALL_EFFECT_DICT[innateAbilitesStr[0]]
            else:
            """
            #print(ALL_EFFECT_DICT.keys())
            try:
                innateAbilites = [ALL_EFFECT_DICT[a] for a in innateAbilitesStr]
            except KeyError:
                raise AttributeError('keys {} not found in ALL_EFFECT_DICT'.format(innateAbilitesStr))

            description = speciesOptionalCheck('DESCRIPTION:', 'STR', '', False, acceptNewlines=True)

            #print(description)

            allSpecies.append(
                Species(name, symbol, genders, size,
                        bodyDict, descriptiveBodyDict,
                        bodyMats, colorChance,
                        landSpeed, waterSpeed, airSpeed,
                        maxHealth, maxStamna, maxMagic, maxFood,
                        regenHealth, regenStamna, regenMagic, hungerRate,
                        statDict, skillDict,
                        depthEnountered=depthEnountered, heatVision=heatVision, glamor=glamor,
                        naturalArmor=naturalArmor, equipSize=equipSize,
                        description=description, innateAbilites=innateAbilites))

    #print('total species: ')
    #print(len(allSpecies))
    return allSpecies


ALL_SPECIES = tuple(buildSpeciesList('/library/species.txt'))

ALL_SPECIES_DICT = {s.name.upper(): s for s in ALL_SPECIES}

#print(ALL_SPECIES)

def testRun():

    ld = 7

    all_s = (9, 1, 4, 3, 5, 7, 0, 41, 2, 3, 7, 12)

    ft = tuple(filter(lambda s: s <= ld, all_s))


def getFilteredSpecies(lowestDepth):
    return tuple(filter(lambda s: s.depthEnountered <= lowestDepth, ALL_SPECIES))
    #return tuple([s for s in ALL_SPECIES if s.depthEnountered <= lowestDepth])

def debugBalance():
    for s in ALL_SPECIES:
        b = 0.0
        speedBal = fsum([s.landSpeed / 1.0, s.waterSpeed / 0.333]) * 0.5
        b+= speedBal
        maxValueBal = sum([s.maxHealth, s.maxStamna, s.maxMagic]) / 40.0
        b+= maxValueBal
        armorDodgeBal = (s.naturalArmor + s.glamor) * 0.5
        b+= armorDodgeBal
        foodBal = ((s.maxFood / s.BASE_MAX_FOOD) + (1.0 / s.hungerRate)) * 0.5
        b+= foodBal
        baseStatBal = fsum(s.baseStats.values()) / len(ALL_STATS)
        b+= baseStatBal
        skillAptBal = fsum(s.skillAppitude.values()) / len(ALL_SKILLS)
        b+= skillAptBal
        print('{0}: speedBal: {1:.4}, maxValueBal: {2:.4}, armorDodgeBal: {3:.4}, \
foodBal: {4:.4}, baseStatBal: {5:.4}, skillAptBal: {6:.4}, total balence: {7:.5}'.format(s.name, speedBal, \
maxValueBal, armorDodgeBal, foodBal, baseStatBal, skillAptBal, b))

