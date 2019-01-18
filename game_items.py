from data_globals import rollAttack, checkForOptionalInfo, checkForMandatoryInfo, FILE_LOCATION_NAME, \
    ACTIVATIABLE_SET, ARMOR_SET, EQUIPABLE_SET
from magic_effects import MagicEffect, ALL_EFFECT_DICT, ALL_STAFFS_DICT, ALL_KNOTS_DICT, DUMMY_EFFECT, \
ALL_SPELLS_DICT, ALL_TALISMANS_DICT, EFFECTS_BY_ITEM_TYPE
from game_egos import E_NONE, ALL_EGOS
from color_factory import ALL_COLORS_DICT
from random import choice, choices, randrange
from coords import Coords
from game_egos import Ego
import re
from typing import List
from data_globals import ALL_ITEM_SET, check_if_entity_can_use_equip_item


def doNothing():
    pass

"""
Angband, Nethack

Floor:
Trap:
Open door:
Closed door:
Wall:
Mineral:

Weapon: /, )
Armor: [, [
Ring: =, =
Staff: _,
"""

def isItemValid(item):
    return item is not None and item.isValidItem

class UniversalItem:

    def __init__(self, name, color, weight, value, minLevel, symbol, coolDown,
            magicEffect, typeOfItem, bodySlotTypesAllowed=['NONE'],
            defence=0, deflection=0,
            toHit=0, damageDice=0, damageDiceSides=0, negateShield=0, negateArmor=0,
            multiplier=0.0, twoHanded=False, unuseableColor='', amnoType='NONE', neutrition=0):
        self.__name = name
        self.__color = color
        if unuseableColor != '':
            self.__unuseableColor = unuseableColor
        else:
            self.__unuseableColor = self.__color
        self.weight = weight
        self.minLevel = minLevel
        self.value = value
        self.symbol = symbol
        self.coolDown = coolDown
        """coolDown equal to 0 = can't use.
        coolDown greater then 0 = egoItem or randart
        coolDown equal to -1 = consumable item
        coolDown equal to -2 = rechargable item
        """
        if magicEffect is not None and magicEffect is not DUMMY_EFFECT:
            self.__magicEffect = ALL_EFFECT_DICT[magicEffect]
        else:
            self.__magicEffect = DUMMY_EFFECT
        self.typeOfItem = typeOfItem
        try:
            # self.bodySlotTypesAllowed = tuple([ALL_BODY_PARTS_DICT[b] for b in bodySlotTypesAllowed])
            self.bodySlotTypesAllowed = tuple(bodySlotTypesAllowed)
        except KeyError:
            self.bodySlotTypesAllowed = tuple(['NONE'])
        self.defence = defence
        self.deflection = deflection
        self.toHit = toHit
        self.damageDice = damageDice
        self.damageDiceSides = damageDiceSides
        self.negateShield = negateShield
        self.negateArmor = negateArmor
        self.isTwoHanded = twoHanded
        self.multiplier = multiplier
        self.amnoType = amnoType
        self.neutrition = neutrition

        if self.typeOfItem == 'NONE':
            self.egosAllowed = tuple([E_NONE])
        else:
            self.egosAllowed = tuple(filter(lambda e: self.typeOfItem in e.sutibleTypes, ALL_EGOS))

    @property
    def name(self):
        return self.__name

    @property
    def color(self):
        return self.__color

    @property
    def unuseableColor(self):
        return self.__unuseableColor

    @property
    def magicEffect(self):
        return self.__magicEffect

    @property
    def isStackable(self):
        return self.typeOfItem in {'AMNUNITION', 'FOOD', 'KNOT'}

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash((self.__name, self.weight, self.minLevel, self.typeOfItem,
self.bodySlotTypesAllowed, self.__unuseableColor, self.__color))

    def __gt__(self, other):
        if self.typeOfItem == other.typeOfItem:
            return self.value > other.value
        return self.typeOfItem > other.typeOfItem

    @property
    def getColor(self):
        return self.__color

    @classmethod
    def newHelmet(cls, name, weight, value, minLevel, defence, bodySlotTypesAllowed):
        return cls(name, 'GREY_LIGHT', weight, value, minLevel, '[', 0,
        None, 'HEAD', bodySlotTypesAllowed,
        defence)

    @classmethod
    def newUpperArmor(cls, name, weight, value, minLevel, defence, bodySlotTypesAllowed):
        return cls(name, 'GREY_LIGHT', weight, value, minLevel, '{', 0,
        None, 'UPPER_BOD', bodySlotTypesAllowed,
        defence)

    @classmethod
    def newLowerArmor(cls, name, weight, value, minLevel, defence, bodySlotTypesAllowed):
        return cls(name, 'GREY_LIGHT', weight, value, minLevel, '{', 0,
        None, 'LOWER_BOD', bodySlotTypesAllowed,
        defence)

    @classmethod
    def newGauntlet(cls, name, weight, value, minLevel, defence):
        return cls(name, 'GREY_LIGHT', weight, value, minLevel, '[', 0,
        None, 'HANDS', ['HANDS_STANDARD'],
        defence)

    @classmethod
    def newBoots(cls, name, weight, value, minLevel, defence, bodySlotTypesAllowed):
        return cls(name, 'GREY_LIGHT', weight, value, minLevel, '{', 0,
        None, 'FEET', bodySlotTypesAllowed,
        defence)

    @classmethod
    def newWeapon(cls, name, weight, value, minLevel, damageDice, damageDiceSides,
        deflection=0, toHit=0, negateShield=0, negateArmor=0, thrownMultiplier=0.5, isTwoHanded=False):
        return cls(name, 'WHITE', weight, value, minLevel, '/', 0, None,
        'WEAPON', [0], deflection=deflection,
        toHit=toHit, damageDice=damageDice, damageDiceSides=damageDiceSides,
        negateShield=negateShield, negateArmor=negateArmor,
        twoHanded=isTwoHanded, multiplier=thrownMultiplier)

    @classmethod
    def newLauncher(cls, name, weight, value, minLevel,
        damageMultiplier, amnoType, negateArmor=0, toHit=0):
        return cls(name, 'WHITE', weight, value, minLevel, '%', 0, None, 'LAUNCHER',
        amnoType=amnoType,
        toHit=toHit, multiplier=damageMultiplier,
        negateArmor=negateArmor, twoHanded=True)

    @classmethod
    def newAmno(cls, name, weight, value, minLevel, damageDice,
        damageDiceSides, amnoType, negateArmor=0):
        return cls(name, 'WHITE', weight, value, minLevel, '*', -1, None, 'AMNUNITION',
        amnoType=amnoType, damageDice=damageDice, damageDiceSides=damageDiceSides,
        negateArmor=negateArmor)

    @classmethod
    def newShield(cls, name, weight, value, minLevel, deflection):
        return cls(name, 'WHITE', weight, value, minLevel, '(', 0, None,
        'SHIELD', ['NONE'], deflection=deflection)

    @classmethod
    def newMisc(cls, name, weight, value, minLevel):
        return cls(name, 'WHITE', weight, value, minLevel, '=', 0, None,
        'MISC', ['NONE'])

    @classmethod
    def newKnot(cls, name, weight, value, minLevel, magicEffect):
        return cls(name, 'BLUE', weight, value, minLevel, '~', -1, magicEffect,
        'KNOT', ['NONE'])

    @classmethod
    def newStaff(cls, name, weight, value, minLevel, magicEffect):
        return cls(name, 'MAUVE_OPERA', weight, value, minLevel, '_', -2, magicEffect,
        'STAFF', ['NONE'])

    @classmethod
    def newTalisman(cls, name, weight, value, minLevel, magicEffect, coolDown):
        return cls(name, 'RED', weight, value, minLevel, '&', coolDown, magicEffect,
        'TALISMAN', ['NONE'])

    @classmethod
    def newGlyph(cls, name, weight, value, minLevel, magicEffect):
        return cls(name, 'GOLD', weight, value, minLevel, '$', -1, magicEffect,
        'GLYPH', ['NONE'])

    @classmethod
    def newCorpse(cls, species):
        return cls(species.name + ' corpse',
                   ALL_COLORS_DICT['GREY'],
                   species.size * 10, 0,
                   species.depthEnountered, species.symbol, 0, None, 'CORSPE', ['NONE'],
                   neutrition=species.size * 10)


DUMMY_ITEM = UniversalItem('', 'WHITE', 0, 0, 0, '&', 0, None, 'NONE')

def safeItemChoice(itemList):
    if len(itemList) < 1:
        return DUMMY_ITEM
    return choice(itemList)


def buildItemsList(fileName) -> dict:

    itemList = dict()

    s = open(FILE_LOCATION_NAME + fileName, 'r')

    sList = re.split(r'NAME:', s.read())

    for sp in sList:

        if re.match(r'(.+)\n', sp):

            i = re.findall(r'^(.+)\n', sp)#find the name and symbol uppercase name to use as a dictionary key

            try:
                name, nameLowerCase, color, symbol = re.split(r'[:]', i[0])
            except ValueError:
                raise AttributeError(re.split(r'[:]', i[0]))

            def itemMandatoryCheck(textToLookFor, dataType, isList=False, listLength=-1):
                return checkForMandatoryInfo(textToLookFor, sp, dataType, 'items.txt', name, isList, listLength)
            
            def itemOptionalCheck(textToLookFor, dataType, default, isList=False, acceptNewlines=False):
                return checkForOptionalInfo(textToLookFor, sp, dataType, default, isList, acceptNewlines)
            
            def itemFlagPresent(textToLookFor):
                return re.search(textToLookFor, sp)

            color = ALL_COLORS_DICT[color]

            weight, value, depth = itemMandatoryCheck('DATA:', 'INT', True, 3)
            #re.split(r'[:]', re.findall(r'DATA:[:.1234567890]\n', sp))

            typeData = itemMandatoryCheck('TYPE:', 'STR', True)#[' + regexValid + ']+\n
            #re.split(r'[:]', re.findall(r'TYPE:[' + regexValid + ']\n', sp))

            itemType = typeData[0]

            if itemType not in ALL_ITEM_SET:
                raise AttributeError('The itemType value ({}) for item {} is not in the permitted set of {}'.format(
                    itemType, name, ALL_ITEM_SET))

            okBodySlots = ['NONE']
            
            defence, deflection, dice, diceSides, toHit, negateArmor, negateShield, neutrition = 0, 0, 0, 0, 0, 0, 0, 0

            magicEffect = DUMMY_EFFECT

            coolDown = 0

            twoHanded= False

            amnoType = 'NONE'

            power = 0.0

            if itemType in {'HEAD', 'UPPER_BOD', 'HANDS', 'LOWER_BOD', 'FEET'}:

                #okBodySlots = [ALL_BODY_PARTS_DICT[b] for b in typeData[1:]]

                okBodySlots = [b for b in typeData[1:]]

                defence, deflection = itemMandatoryCheck('DEFENCE:', 'INT', True, 2)
                #re.split(r'[:]', re.finditer(r'DEFENCE:[:.1234567890]\n', sp))

            elif itemType == 'WEAPON':

                dice, diceSides = itemMandatoryCheck('DICE:', 'INT', True, 2)
                #re.split(r'[:]', re.finditer(r'DICE:[:.1234567890]\n', sp))

                power = itemOptionalCheck('THROW_POWER:', 'FLOAT', 0.5)
                #checkForOptionalInfo(r'THROW_POWER:', sp, 'FLOAT', 0.5)

                toHit = itemOptionalCheck('TO_HIT:', 'INT', 0)
                #checkForOptionalInfo(r'TO_HIT:', sp, 'INT', 0)

                twoHanded = itemFlagPresent('TWO_HANDED')
                #re.search(r'TWO_HANDED:', sp) is not None

                negateArmor = itemOptionalCheck('NEGATE_ARMOR:', 'INT', 0)
                #checkForOptionalInfo(r'NEGATE_ARMOR:', sp, 'INT', 0)

                negateShield = itemOptionalCheck('NEGATE_SHIELD:', 'INT', 0)
                #checkForOptionalInfo(r'NEGATE_SHIELD:', sp, 'INT', 0)

            elif itemType == 'LAUNCHER':

                amnoType = typeData[1]

                power = itemOptionalCheck('POWER:', 'FLOAT', 1.0)
                #checkForOptionalInfo(r'POWER:', sp, 'FLOAT', 1.0)

                toHit = itemOptionalCheck('TO_HIT:', 'INT', 0)
                #checkForOptionalInfo(r'TO_HIT:', sp, 'INT', 0)

            elif itemType == 'AMNUNITION':

                dice, diceSides = itemMandatoryCheck('DICE:', 'INT', True, 2)
                #re.split(r'[:]', re.finditer(r'DICE:[:.1234567890]\n', sp))

                amnoType = typeData[1]

                toHit = itemOptionalCheck('TO_HIT:', 'INT', 0)
                #checkForOptionalInfo(r'TO_HIT:', sp, 'INT', 0)

            elif itemType == 'SHIELD':

                deflection = itemMandatoryCheck('DEFENCE:', 'INT')
                #re.finditer(r'DEFENCE:[:.1234567890]\n', sp)

            elif itemType == 'FOOD':

                neutrition = itemMandatoryCheck('NEUTRITION:', 'INT')
                #re.finditer(r'NEUTRITION:[:.1234567890]\n', sp)

            if itemType in {'STAFF', 'KNOT', 'GLYPH', 'TALISMAN'}:

                effectItemDict = EFFECTS_BY_ITEM_TYPE[itemType]
                # effectItemDict is a string : MagicEffect dictionary

                for k, v in effectItemDict.items():

                    if k in EFFECTS_BY_ITEM_TYPE[itemType]:

                        new_name = '{}_OF_{}'.format(name, k)

                        sDepth = depth + v.depth

                        sName = nameLowerCase + ' of ' + v.name

                        sValue = value + v.value

                        sCoolDown = v.coolDown

                        itemList[new_name] = (UniversalItem(sName, color, weight, sValue, sDepth, symbol,
                                                      sCoolDown, k, itemType, okBodySlots, defence, deflection, toHit,
                                                      dice, diceSides, negateShield,
                                                      negateArmor, power, twoHanded, unuseableColor='', amnoType=amnoType,
                                                      neutrition=neutrition
                                                      ))
            else:
            
                itemList[name] = (UniversalItem(nameLowerCase, color, weight, value, depth, symbol,
                coolDown, magicEffect, itemType, okBodySlots, 
                defence, deflection, toHit, dice, diceSides, negateShield, negateArmor,
                power, twoHanded, unuseableColor='', amnoType=amnoType, neutrition=neutrition
                ))

    s.close()
    return itemList

ALL_ITEM_DICT = buildItemsList('/library/items.txt')

ALL_ITEM_DATA = ALL_ITEM_DICT.values()

def generateStaffs():

    staffList = []

    for s in ALL_STAFFS_DICT.values():

        staffList.append(UniversalItem.newStaff('Staff of ' + s.name,
            8, s.cost, s.difficulty, s)
        )

    return staffList

def generateKnots():

    knotList = []

    for k in ALL_KNOTS_DICT.values():

        knotList.append(UniversalItem.newKnot('Knot of ' + k.name,
        1, k.cost, k.difficulty, k)

        )

    return knotList

def generateTalismans():

    talismanList = []

    for t in ALL_TALISMANS_DICT.values():

        talismanList.append(UniversalItem.newTalisman('Talisman of ' + t.name,
        3, t.cost, t.difficulty, t, t.cost)
        )

    return talismanList


def generateGlyphs():

    glyphList = []

    for g in ALL_SPELLS_DICT.values():

        glyphList.append(UniversalItem.newGlyph('Glyph of ' + g.name,
        1, g.cost * 5, g.difficulty, g)
        )

    return glyphList


"""
def randomItem(itemType):
    return choice(ITEM_DICT[itemType])
"""

def getListOfItemsSuitbleForDepth(depth):
    l = list(filter(lambda i: i.minLevel <= depth, ALL_ITEM_DATA))


    #items = [i for i in ALL_ITEM_DATA if i.minLevel <= depth]
    return l
    #return items

def getSuitbleItemsByType(itemList, itemType, slot=None):
    if slot is None:
        return list(filter(lambda i: i.typeOfItem == itemType, itemList))
    return list(filter(lambda i: i.typeOfItem == itemType and slot in i.bodySlotTypesAllowed, itemList))


def getLongestItemName():

    l = 0

    l = sum([max(l, a.name) for a in ALL_ITEM_DATA])

    return l


#egoDict = {k:v for k in (EQUIPABLE, [e for e in ALL_EGOS if k in e.sutibleTypes])}

class UniversalGameItem:
    def __init__(self, baseData: UniversalItem, co, ego: Ego, egoPower, seen, stackSize, identified=False):
        assert isinstance(baseData, UniversalItem), 'Expected item baseData to be of type UniversalItem, instead it was of type %r.' % baseData
        self.__baseData = baseData
        self.co = co
        #self.extraDef = extraDef
        #self.extraDeflection = extraDeflection
        #self.extraDam = extraDam
        #self.extraToHit = extraToHit
        self.coolDown = 0
        self.ego = ego

        self.seen = seen
        self.__stack = 1
        self.egoPower = egoPower
        if self.__baseData.coolDown == -1:
            self.__stack = stackSize

        self.identified = identified
        self.fullName = self.getFullName()


    @property
    def baseData(self):
        return self.__baseData
    
    @baseData.setter
    def baseData(self, value: UniversalItem):
        self.__baseData = value

    @property
    def stack(self):
        return self.__stack

    @stack.setter
    def stack(self, value: int):
        self.__stack = value

    @property
    def long_description(self):
        des = []

        if self.typeOfItem in {'WEAPON', 'AMNUNITION'}:
            des.append('It does {}d{}')
            if self.identified:
                if self.extraDam > 0:
                    des.append('plus {}'.format(self.extraDam))
                elif self.extraDam < 0:
                    des.append('minus {}'.format(self.extraDam))
            des.append('points of damage.')

            des.append('When thrown, the damage that it inflicts is multiplied by {:%}.'.format(self.__baseData.multiplier))

        elif self.typeOfItem == 'LAUNCHER':

            des.append('Any missiles that it launches have thier damage multiplied by {:%}.'.format(self.__baseData.multiplier))

        if self.typeOfItem in {'WEAPON', 'LAUNCHER', 'AMNUNITION', 'MISC'}:

            if self.__baseData.toHit > 0:
                des.append('It is well balanced, giving it an extra {} to hit.'.format(self.__baseData.toHit))
            elif self.__baseData.toHit < 0:
                des.append('It is poorly balanced, reducing its to hit chance by {}.'.format(self.__baseData.toHit))

        if self.identified:
            if self.extraToHit > 0:
                des.append('Supernatural properties imporve it\'s chance to hit by {}'.format(self.extraToHit))
            elif self.extraToHit < 0:
                des.append('Malignant energies hinder the users accuracy by {}'.format(self.extraToHit))

        if self.typeOfItem == 'WEAPON':
            if self.__baseData.negateShield > 0:
                des.append('It is especially effective against shields, reducing their block level bhy a maximum of {}.'.format(self.__baseData.negateShield))

        if self.typeOfItem in ARMOR_SET or self.typeOfItem == 'WEAPON':
            if self.__baseData.deflection > 0:
                des.append('It improves the chance of deflecting an attack by {}.'.format(self.__baseData.deflection))

        if self.identified:
            if self.extraDeflection > 0:
                des.append('Its deflective abilities are further improved by {}.'.format(self.extraDeflection))
            elif self.extraDeflection < 0:
                des.append('The chance for the user to evade any attack is decreased by {}.'.format(self.extraDeflection))

        if self.typeOfItem in ARMOR_SET:
            des.append('Any enemy attack has it\'s damage reduced by {}.'.format(self.__baseData.defence))

        if self.identified:
            if self.extraDef > 0:
                des.append('Magical forces boost the users armor rating by {}.'.format(self.extraDef))
            elif self.extraDef < 0:
                des.append('Sinister forces reduce the users armor rating by {}.'.format(self.extraDef))

        return ' '.join(des)


    @classmethod
    def new_dummy_object(cls):
        return cls(DUMMY_ITEM, Coords(0, 0), E_NONE, 0, False, 0, True)

    def make_item_into_dummy(self):
        self.__baseData = DUMMY_ITEM
        self.coolDown = 0
        self.__stack = 1
        self.ego = E_NONE
        self.fullName = self.getFullName()


    @property
    def getValue(self):
        if self.identified:
            return self.get_actual_value

        else:
            if self.__baseData.coolDown == -2:
                return self.__baseData.value - self.__baseData.magicEffect.value
            elif self.__baseData.typeOfItem == 'KNOT':

                return (self.__baseData.value - self.__baseData.magicEffect.value) * self.__stack

            elif self.__baseData.coolDown == -1:
                return self.__baseData.value * self.__stack

            else:
                return self.__baseData.value

    @property
    def get_actual_value(self):
        if self.ego != E_NONE:
            if self.__baseData.coolDown == -2:# if it is a staff
                return self.__baseData.value * (self.stack + 1) + self.ego.calculate_value_ajustment(self)
            elif self.__baseData.coolDown == -1:# if it is a knot or arrow
                return (self.ego.calculate_value_ajustment(self) + self.__baseData.value) * self.__stack
            else:
                return self.__baseData.value + self.ego.calculate_value_ajustment(self)
        else:
            if self.__baseData.coolDown == -2:
                return self.__baseData.value * (self.__stack + 1)
            elif self.__baseData.coolDown == -1:
                return self.__baseData.value * self.__stack
            else:
                return self.__baseData.value

    def getFullName(self):

        if self.__baseData is DUMMY_ITEM:
            return 'NONE TYPE'

        plu = ''
        pre = ''

        if self.__baseData.typeOfItem in ('KNOT', 'AMNUNITION', 'FOOD'):
            if self.__stack == 1:
                pre = 'A'
            else:
                pre = str(self.__stack)
        else:
            pre = 'A'

        if self.__baseData.typeOfItem in ARMOR_SET:
            if self.extraDef == 0 or not self.identified:
                plu = '[{: d}]'.format(self.__baseData.defence)
            else:
                plu = '[{: d} {:+d}]'.format(self.__baseData.defence, self.extraDef)

        elif self.__baseData.typeOfItem == 'WEAPON':
            pl = ['({: d}'.format(self.__baseData.toHit)]
            if self.extraToHit != 0 and self.identified:
                pl.append('+{: d}'.format(self.extraToHit))
            pl.append(' acc')

            pl.append(' {:d}d{:d}'.format(self.__baseData.damageDice, self.__baseData.damageDiceSides))

            if self.extraDam != 0 and self.identified:
                pl.append(' {:+d}'.format(self.extraDam))

            pl.append(' {: d}')


            if self.__baseData.negateShield > 0:
                pl.append(' {: d} negSh'.format(self.__baseData.negateShield))

            if self.__baseData.negateArmor != 0:
                pl.append(' {: d} negAr'.format(self.__baseData.negateArmor))

            pl.append(')')


            plu = ''.join(pl)
        elif self.__baseData.typeOfItem == 'SHIELD':
            if self.extraDeflection == 0:
                plu = '[{: d}]'.format(self.__baseData.deflection)
            else:
                plu = '[{: d}+{:+d}]'.format(self.__baseData.deflection, self.extraDeflection)
        elif self.__baseData.typeOfItem == 'STAFF':
            if self.__stack > 0:
                plu = '({: d} charges)'.format(self.__stack)
            else:
                plu = '(Empty)'
        elif self.__baseData.typeOfItem == 'TALISMAN':
            if self.identified:
                plu = '({:%} charged)'.format(1.0 - self.coolDown / self.__baseData.coolDown)
            else:
                if self.coolDown > 0:
                    plu = '(charging)'
                else:
                    plu = '(charged)'
        elif self.__baseData.typeOfItem == 'FOOD':
            plu = '({} food value)'.format(self.__baseData.defence)


        if self.identified:
            return ' '.join([pre, self.__baseData.name, self.ego.getSuffix(self.egoPower), plu])

        return ' '.join([pre, self.__baseData.name, plu])


    def identify_item(self):
        self.identified = True
        self.fullName = self.getFullName()

    @property
    def extraDef(self):
        return self.ego.extraDefence

    @property
    def extraToHit(self):
        return self.ego.extraToHit

    @property
    def extraDam(self):
        return self.ego.extraDam

    @property
    def extraDeflection(self):
        return self.ego.extraDeflection

    def __gt__(self, other):
        return self.__baseData > other.baseData

    @property
    def isValidItem(self):
        return self.__baseData != DUMMY_ITEM

    def checkDuplicate(self, item):
        return self.__baseData == item.baseData and self.ego == item.ego

    @property
    def typeOfItem(self):
        return self.__baseData.typeOfItem

    @classmethod
    def spawnDummyItem(cls, x, y):
        return cls(DUMMY_ITEM, Coords(x, y), E_NONE, 0, False, 1, False)

    @classmethod
    def spawnForPlayer(cls, baseData, x, y, stack=-1):
        if baseData is None or baseData is DUMMY_ITEM:
            return cls(DUMMY_ITEM, Coords(x, y), E_NONE, 0, False, 1, identified=True)

        if stack == -1:
            stack = 1
        if baseData.typeOfItem == 'STAFF':
            stack = rollAttack(2, 1 + baseData.minLevel)

        return cls(baseData, Coords(x, y), E_NONE, 0, True, 1, identified=True)

    def regenerate(self, baseData, x, y, depth, identified=False, stack=-1):
        if baseData is None or baseData is DUMMY_ITEM:
            self.baseData = DUMMY_ITEM
            self.co = Coords(x, y)
            self.identified = identified
            self.egoPower = 0
            self.ego = E_NONE
            self.__stack = 0
        else:
            self.__baseData = baseData

            ego = E_NONE

            egos = list(filter(lambda e: e.minLevel + baseData.minLevel < depth, baseData.egosAllowed))

            if len(egos) == 1:
                ego = egos[0]
            elif len(egos) > 1:
                ego = choices(egos, [depth - (e.minLevel + baseData.minLevel) for e in egos])[0]

            egoPower = depth - (ego.minLevel + baseData.minLevel)

            if egoPower < 1:
                egoPower = 0
            else:

                minPower = -egoPower // 4

                egoPower = randrange(minPower, egoPower)

            if egoPower == 0:
                ego = E_NONE

            if stack == -1:
                stack = 1
            if baseData.typeOfItem == 'STAFF':
                stack = ego.extraCharges + baseData.magicEffect.max_charges

            else:
                self.ego = ego
                self.egoPower = egoPower
                self.identified = identified
                self.seen = False
                self.stack = stack
                self.identify_item()

    @classmethod
    def spawnItem(cls, baseData, x, y, depth, identified=False, stack= -1):
        if baseData is None or baseData is DUMMY_ITEM:
            return cls(DUMMY_ITEM, Coords(x, y), E_NONE, 0, False, 1, identified=True)

        ego = E_NONE

        egos = list(filter(lambda e: e.minLevel + baseData.minLevel < depth, baseData.egosAllowed))

        if len(egos) == 1:
            ego = egos[0]
        elif len(egos) > 1:
            ego = choices(egos, [depth - (e.minLevel + baseData.minLevel) for e in egos])[0]

        egoPower = depth - (ego.minLevel + baseData.minLevel)

        if egoPower < 1:
            egoPower = 0
        else:

            minPower = -egoPower // 4

            egoPower = randrange(minPower, egoPower)

        if egoPower == 0:
            ego = E_NONE

        if stack == -1:
            stack = 1
        if baseData.typeOfItem == 'STAFF':
            stack = ego.extraCharges + baseData.magicEffect.max_charges

        return cls(baseData, Coords(x, y), ego, egoPower, False, stack, identified)

    @property
    def isStackable(self) -> bool:
        return self.__baseData.coolDown == -1

    @property
    def can_be_recharged(self) -> bool:
        return self.__baseData.typeOfItem in {'STAFF', 'TALISMAN'} or self.egoPower != E_NONE

    @property
    def get_max_charges(self) -> int:
        if self.__baseData.coolDown == -2:
            return self.ego.extraCharges + self.__baseData.magicEffect.max_charges
        else:
            return 0

    def recharge(self, amount):
        if self.__baseData.typeOfItem == 'STAFF':
            self.__stack += amount
        elif self.__baseData.typeOfItem not in {'KNOT', 'CORPSE'}:
            self.coolDown = 0

    def subtract_charge_or_reset_cooldown(self) -> bool:
        """Returns True is item is a consumable"""
        if self.__baseData.typeOfItem in {'STAFF', 'KNOT', 'AMNUNITION'}:
            self.__stack -= 1
            return self.__baseData.typeOfItem != 'STAFF'
        elif self.__baseData.typeOfItem == 'TALISMAN':
            self.coolDown = self.__baseData.magicEffect.coolDown
            return False
        elif self.__baseData.typeOfItem != 'CORPSE':
            self.coolDown = self.egoPower.coolDown
            return False
        return False

    @property
    def rollDamage(self):
        if self.__baseData.typeOfItem == 'WEAPON' or self.__baseData.typeOfItem == 'AMNUNITION':
            return rollAttack(self.__baseData.damageDice, self.__baseData.damageDiceSides) + self.extraDam
        return 0

    @property
    def averageDamage(self):
        if self.__baseData.typeOfItem == 'WEAPON' or self.__baseData.typeOfItem == 'AMNUNITION':
            return ((self.__baseData.damageDice * self.__baseData.damageDiceSides) * 0.5 + self.__baseData.damageDice * 0.5) + self.extraDam
        return 0

    def avarageLauncherDamage(self, proj):
        if proj.averageDamage == 0:
            return 0
        return proj.averageDamage * self.__baseData.multiplier + self.extraDam

    @property
    def rollThrownDamage(self):
        return round(rollAttack(self.__baseData.damageDice, self.__baseData.damageDiceSides) * self.__baseData.multiplier) + self.extraDam

    @property
    def getToHit(self):
        if self.__baseData.typeOfItem in ('WEAPON', 'AMNUNITION', 'LAUNCHER', 'HANDS', 'MISC'):
            return self.__baseData.toHit + self.extraToHit
        return 0

    @property
    def getToDamage(self) -> int:
        if self.__baseData.typeOfItem in ('WEAPON', 'AMNUNITION', 'LAUNCHER', 'HANDS', 'MISC'):
            return self.extraDam
        return 0

    @property
    def isEquipable(self) -> bool:
        return self.__baseData.typeOfItem in EQUIPABLE_SET

    @property
    def getWeight(self):
        if self.__baseData.typeOfItem in ('KNOT', 'AMNUNITION', 'FOOD'):
            return self.__baseData.weight * self.__stack
        return self.__baseData.weight

    @property
    def isTwoHanded(self):
        return self.__baseData.isTwoHanded and self.__baseData.typeOfItem == 'WEAPON'

    @property
    def getTotalDefence(self):
        if self.__baseData.typeOfItem in ARMOR_SET:
            return self.__baseData.defence + self.extraDef
        return 0

    @property
    def getDeflection(self):
        if self.__baseData.typeOfItem in ('HEAD', 'UPPER_BOD', 'HANDS', 'LOWER_BOD', 'FEET', 'WEAPON', 'SHIELD'):
            return self.__baseData.deflection + self.extraDeflection
        return 0

    @property
    def getSymbol(self):
        return self.__baseData.symbol

    @property
    def getColor(self):
        return self.__baseData.color

    def checkEquipColor(self, entity):
        if check_if_entity_can_use_equip_item(entity, self):
            return self.__baseData.color
        else:
            return self.__baseData.unuseableColor
    """
        if self.__baseData.typeOfItem in ARMOR:
            if entity.bodyDict[self.__baseData.typeOfItem] not in self.__baseData.bodySlotTypesAllowed:
                return self.__baseData.unuseableColor
        elif self.__baseData.typeOfItem == 'STAFF' and self.__stack < 1:
            return self.__baseData.unuseableColor
        elif self.__baseData.typeOfItem == 'TALISMAN' and self.coolDown > 0:
            return self.__baseData.unuseableColor
        return self.__baseData.color
    """


    def checkCorrectAmno(self, amno):
        if amno.baseData.typeOfItem != 'AMNUNITION' or self.__baseData.typeOfItem != 'LAUNCHER' or amno.stack < 1:
            return False
        return self.__baseData.amnoType == amno.baseData.amnoType

    def rollLauncherDamage(self, amno) -> int:
        if self.__baseData.typeOfItem is 'LAUNCHER':
            return round(amno.rollDamage * self.__baseData.multiplier) + self.extraDam + amno.extraDam
        return 0

    @property
    def getFoodValue(self) -> int:
        if self.__baseData.typeOfItem is 'FOOD':
            return self.__baseData.defence
        return 0

    @property
    def getEffect(self) -> MagicEffect:
        if self.__baseData.typeOfItem in ACTIVATIABLE_SET:
            return self.__baseData.magicEffect
        elif self.ego is not E_NONE:
            return self.ego.ego_effect
        else:
            return DUMMY_EFFECT

    @property
    def can_be_used(self) -> bool:
        if self.getEffect is not DUMMY_EFFECT:
            if self.__baseData.typeOfItem in {'KNOT', 'STAFF'}:
                return self.__stack > 0
            else:
                return self.coolDown < 1
        else:
            return False



itemList = List[UniversalGameItem]
