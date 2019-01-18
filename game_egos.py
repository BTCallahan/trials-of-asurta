from data_globals import checkForMandatoryInfo, checkForOptionalInfo, FILE_LOCATION_NAME
from magic_effects import MagicEffect, DUMMY_EFFECT, ALL_EFFECT_DICT
import re

"""
possible ego items:
weapon: damage, accuracry, both,
armor:defence, deflection, thorns
boots: speed
gauntlets: damage
"""

class Ego:
    def __init__(self, badSuffix, suffix, sutibleTypes, minLevel, extraDefence=0, extraDeflection=0,
                 extraDam=0, extraToHit=0, extraLandSpeed=0.0, extraWaterSpeed=0.0, extraAirSpeed=0.0,
                 extraLightRadius=0, extraMultiplier=0.0, extraCharges=0, isRandart=False,
                 effect: MagicEffect=DUMMY_EFFECT):
        self.suffix = tuple(suffix)
        self.badSuffix = tuple(badSuffix)
        self.sutibleTypes = tuple(sutibleTypes)
        self.minLevel = minLevel

        self.extraDefence = extraDefence
        self.extraDeflection = extraDeflection
        self.extraDam = extraDam
        self.extraToHit = extraToHit

        self.extraLandSpeed = extraLandSpeed
        self.extraWaterSpeed = extraWaterSpeed
        self.extraAirSpeed = extraAirSpeed

        self.extraLightRadius = extraLightRadius
        self.extraMultiplier = extraMultiplier
        self.extraCharges = extraCharges

        self.ego_effect: MagicEffect = effect

        self.isRandart = isRandart

    def calculate_value_ajustment(self, game_item):
        pow = game_item.egopower
        total = sum([e * pow for e in [self.extraDefence, self.extraDeflection, self.extraDam, self.extraToHit]])
        total += round(sum([e * pow for e in [self.extraLandSpeed, self.extraAirSpeed, self.extraWaterSpeed]]))
        total += round(self.extraLightRadius * pow * 0.5)
        total += round(self.extraMultiplier * pow * 1.25)
        total += game_item.getEffect.value * pow * self.extraCharges
        return total

    def __hash__(self):
        return hash((self.suffix, self.badSuffix, self.sutibleTypes,
self.minLevel, self.extraDefence, self.extraDeflection, self.extraDam,
self.extraToHit, self.extraLandSpeed, self.extraWaterSpeed))

    def __eq__(self, o):
        return hash(self) == hash(o)

    def getSuffix(self, power):
        if power >= len(self.suffix):
            return self.suffix[-1]
        if power < 0:
            return self.badSuffix
        return self.suffix[power]

    @classmethod
    def randart(cls, typeOfItem, power):

        typeDict = {
            'WEAPON': ['extraDeflection', 'extraDam', 'extraToHit'],
            'HEAD': ['extraDefence', 'extraDeflection', 'extraLightRadius'],
            'UPPER_BOD': ['extraDefence', 'extraDeflection', 'extraLightRadius', 'extraAirSpeed'],
            'HANDS': ['extraDefence', 'extraDeflection', 'extraDam', 'extraToHit'],
            'LOWER_BOD': ['extraDefence', 'extraDeflection', 'extraLandSpeed', 'extraWaterSpeed'],
            'FEET': ['extraDefence', 'extraDeflection', 'extraLandSpeed', 'extraWaterSpeed', 'extraAirSpeed'],
            'LAUNCHER': ['extraDam', 'extraToHit', 'extraMultiplier'],
            'STAFF': ['extraMultiplier', 'extraCharges'],
            'MISC': ['extraDeflection', 'extraDam', 'extraToHit', 'extraLightRadius', 'extraLandSpeed',
                     'extraWaterSpeed', 'extraAirSpeed']
        }

        valueDict = {'extraDeflection': 0,
                     'extraDefence': 0,
                     'extraDam': 0,
                     'extraToHit': 0,

                     'extraMultiplier': 0.0,
                     'extraCharges': 0,

                     'extraLightRadius': 0,

                     'extraLandSpeed': 0.0,
                     'extraWaterSpeed': 0.0,
                     'extraAirSpeed': 0.0

                     }

        #TODO: implement an error checking mechinism to make sure the typeOfItem is present in the typeDict keys

        possibleBonusAtributes = typeDict[typeOfItem]

        noOfEffects = min(4, len(possibleBonusAtributes))

        selected_bonus_atributes = choices(noOfEffects, k=noOfEffects)

        for a in selected_bonus_atributes:
            valueDict[a] += power


        return cls('', [], ['NONE'], -1,
                   extraDefence=valueDict['extraDefence'],
                   extraDeflection=valueDict['extraDeflection'],
                   extraDam=valueDict['extraDam'],
                   extraToHit=valueDict['extraToHit'],

                   extraMultiplier=valueDict['extraMultiplier'],

                   extraCharges=valueDict['extraCharges'],

                   extraAirSpeed=valueDict['extraAirSpeed'],
                   extraLandSpeed=valueDict['extraLandSpeed'],
                   extraWaterSpeed=valueDict['extraWaterSpeed'],

                   extraLightRadius=valueDict['extraLightRadius']
                   )

E_NONE = Ego([''], [''], ['NONE'], 0)

"""
E_ACCURACY = Ego('of unballancing', ['of agility', 'of skill', 'of the wind'],['WEAPON', 'AMNUNITION', 'LAUNCHER', 'MISC'], 5, extraToHit=2)
E_DAMAGE = Ego('of feathers', ['of mayham', 'of maiming', 'of slaying'], ['WEAPON', 'AMNUNITION', 'LAUNCHER', 'MISC'], 5, extraDam=2)
E_BATTLE = Ego('of pacifisim', ['of combat', 'of battle', 'of war'], ['WEAPON', 'AMNUNITION', 'LAUNCHER'], 8, extraToHit=1, extraDam=1)
E_DEFLECTION = Ego('of softness', ['of durability', 'of hardness', 'of the barrier'], ['HEAD', 'UPPER_BOD', 'HANDS', 'LOWER_BOD', 'FEET', 'WEAPON', 'SHIELD', 'MISC'], 5, extraDeflection=2)
E_DEFENCE = Ego('of vunrability', ['of resilince', 'of armor', ''], ['HEAD', 'UPPER_BOD', 'HANDS', 'LOWER_BOD', 'FEET', 'MISC'], 5, extraDefence=2)
E_PROTECTION = Ego('', ['of the mantle', 'of the guardian'], ['HEAD', 'UPPER_BOD', 'HANDS', 'LOWER_BOD', 'FEET', 'MISC'], 8, extraDeflection=1, extraDefence=1)
E_LIGHT = Ego('of darkness', ['of light', 'of guidance'], ['MISC'], 0, lightRadius=5)
"""

def buildEgosList(filename):

    egoList = []

    s = open(FILE_LOCATION_NAME + filename, 'r')

    sList = re.split(r'NAME:', s.read())

    for sp in sList:

        if re.match(r'(.+)\n\n', sp):

            #i = re.finditer(r'(.+)', s)

            i = re.findall('^(.+)\n', sp)

            name = re.match('(.+)', sp)

            def egosMandatoryCheck(textToLookFor, dataType, isList=False, listLength=-1):
                return checkForMandatoryInfo(textToLookFor, sp, dataType, 'egos.txt', name.string, isList, listLength)

            def egosOptionalCheck(textToLookFor, dataType, default, isList=False, acceptNewlines=False):
                return checkForOptionalInfo(textToLookFor, sp, dataType, default, isList, acceptNewlines)

            depth = egosMandatoryCheck('DEPTH:', 'INT')
            #re.finditer(r'DEPTH:[:.1234567890]\n', sp)

            suffix = egosMandatoryCheck('SUFFIX:', 'STR', True)
            #re.finditer(r'SUFFIX:[' + regexValid + ']\n', sp)

            badSuffix = egosMandatoryCheck('BAD_SUFFIX:', 'STR', True)

            okayTypes = egosMandatoryCheck('TYPES:', 'STR', True)

            #re.finditer(r'BAD_SUFFIX:[' + regexValid + ']\n', sp)

            toHit = egosOptionalCheck(r'TO_HIT:', 'INT', 0)

            toDam = egosOptionalCheck(r'TO_DAM:', 'INT', 0)

            defence = egosOptionalCheck(r'DEFENCE:', 'INT', 0)

            deflection = egosOptionalCheck(r'DEFLECTION', 'INT', 0)

            light = egosOptionalCheck(r'LIGHT:', 'INT', 0)

            effectStr = egosOptionalCheck('EFFECT:', 'STR', 'NONE')

            effect = ALL_EFFECT_DICT.get(effectStr, DUMMY_EFFECT)

            egoList.append(Ego(badSuffix, suffix, okayTypes, depth, extraDefence=defence,
            extraDeflection=deflection, extraToHit=toHit, extraDam=toDam, extraLightRadius=light, effect=effect
            ))

    s.close()
    return egoList

ALL_EGOS = buildEgosList('/library/egos.txt')

#ALL_EGOS = (E_NONE, E_ACCURACY, E_DAMAGE, E_BATTLE, E_DEFLECTION, E_DEFENCE, E_PROTECTION, E_LIGHT)

#def getListOfEgosSuitbleForDepth(depth):
