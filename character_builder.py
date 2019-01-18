from game_items import DUMMY_ITEM, getListOfItemsSuitbleForDepth, \
getSuitbleItemsByType, UniversalItem, UniversalGameItem, getLongestItemName
from data_globals import ALL_STATS, ALL_SKILLS, STAT_NAMES, SKILL_NAMES, PRONOUN_DICT, check_if_entity_can_wear_armor
from species import getFilteredSpecies, ARMOR
from color_factory import ALL_COLORS_DICT
import tdl

class ItemContainer:
    def __init__(self, item, amount):
        self.item = item
        self.amount = amount

    @classmethod
    def singleItem(cls, item):
        return cls(item, 1)

    @classmethod
    def nullItem(cls):
        return cls(DUMMY_ITEM, 1)

    def __str__(self):
        if not self.hasItem:
            return ' '
        else:
            if self.item.isStackable:
                return '{0} {1}'.format(self.amount, self.item.name)
            else:
                return '{0}'.format(self.item.name)

    @property
    def hasItem(self):
        return self.item is not DUMMY_ITEM

    @property
    def value(self):
        if not self.hasItem:
            return 0
        return self.item.value * self.amount

    def clear(self):
        value = self.value
        self.item = DUMMY_ITEM
        self.amount = 1
        return value

    def subtract(self):
        self.amount-=1
        if self.amount < 2:
            return self.clear()
        else:
            return self.item.value

    #this returns the value of the item that is being replaced
    def add(self, item):
        if self.item is item:
            if item.isStackable:
                self.amount+=1
        else:
            if not self.hasItem:
                self.item = item
                self.amount = 1
            else:
                ret = self.item.value
                if self.item.isStackable:
                    ret = self.item.value * self.amount
                self.amount = 1
                self.item = item

    def valueDiffrence(self, item):
        if self.item == item:
            if item.isStackable:
                return -item.value
            else:
                return 0
        else:
            if not self.hasItem:
                return -item.value

            elif item is DUMMY_ITEM:

                if self.item.isStackable:
                    return self.value

                else:
                    return self.item.value
            else:
                return self.value - item.value

class SpeciesSelector:

    def __positionHelperDict(self):
        r = dict()

        st = len(ALL_STATS)

        for s, i in zip(ALL_STATS, range(st)):
            r[s] = i

        sk = len(ALL_SKILLS)

        for s, i in zip(ALL_SKILLS, range(st, st + sk)):
            r[s] = i

        return r


    def __equipPlaceNames(self, species):
        r = ['Head:', 'Upper Body:', 'Hands:', 'Lower Body:']
        if species.bodyDict['FEET'].nullType:
            r.append('')
        else:
            r.append('Feet:')

        r+=['Main Hand:', 'Off Hand:', 'Quiver:', 'Misc:', '  ', '  ', '  ', '  ', '  ', 'Inventory:']

        return r

    def __init__(self, statOrSkillSelected, statPoints, skillPoints, lowestDepth):

        self.speciesNo = 0
        self.speciesAvliable = getFilteredSpecies(lowestDepth)
        #elf.selectedSpecies = self.speciesAvliable[self.speciesNo]
        self.statOrSkillSelected = 0

        self.statPoints = statPoints
        self.skillPoints = skillPoints
        self.statDict = {k:v for k, v in zip(ALL_STATS, [0 for z in range(len(ALL_STATS))])}
        self.skillDict = {k:v for k, v in zip(ALL_SKILLS, [0 for z in range(len(ALL_SKILLS))])}


        self.EQUIP_PLACE_NAMES = self.__equipPlaceNames(self.selectedSpecies)
        #EQUIP_PLACE_NAMES = ('Head:', 'Upper Body:', 'Hands:', 'Lower Body:', 'Feet:' 'Main Hand:', 'Off Hand:', 'Misc:' 'Inventory:')
        #EQUIP_PLACE_NAMES = tuple(['Head:', 'Upper Body:', 'Hands:', 'Lower Body:'], )

        #self.statDict = OrderedDict()

        self.statPlusSkillLength = len(ALL_STATS) + len(ALL_SKILLS)
        #self.space = (' ' * self.statPlusSkillLength).split()
        self.space = [' ' for c in range(self.statPlusSkillLength)]
        #print('length of space: {}'.format(len(self.space)))
        #print('length of all stats {}, length of all skills {}'.format(len(ALL_STATS), len(ALL_SKILLS)))
        #print('stat dict keys: {}, values: {}'.format(self.statDict.keys(), self.statDict.values()))
        self.space[self.statOrSkillSelected] = '*'

        self.selectedGender = 0
        self.colors = self.selectedSpecies.getColorDict

        self.avalibleEquip = getListOfItemsSuitbleForDepth(0)

        self.buyItems = False
        self.itemNo = 0
        self.valueLeft = 100

        self.handItem = ItemContainer.nullItem()
        self.offHandItem = ItemContainer.nullItem()
        self.quiver = ItemContainer.nullItem()

        self.wornDict = {'HEAD' : ItemContainer.nullItem(), 'UPPER_BOD' :
ItemContainer.nullItem(), 'HANDS' : ItemContainer.nullItem(), 'LOWER_BOD' :
ItemContainer.nullItem(), 'FEET' : ItemContainer.nullItem()}

        self.miscItems = [ItemContainer.nullItem() for e in range(6)]
        self.inventory = [ItemContainer.nullItem() for e in range(16)]
        self.starPositionHelperDict = self.__positionHelperDict()

        maxBuyItemLineLenght = max([len(a.name) for a in self.avalibleEquip])

        self.buyItemSelectedString = '*{:=^' + str(maxBuyItemLineLenght + 2) + '}*'
        self.buyItemString = '{: ^' + str(maxBuyItemLineLenght + 4) + '}'

    def ajustForChosenSpecies(self):

        self.EQUIP_PLACE_NAMES = self.__equipPlaceNames(self.selectedSpecies)

        aitems = getListOfItemsSuitbleForDepth(0)
        #self.selectedSpecies.bodyDict[a.typeOfItem] in a.bodySlotTypesAllowed

        # self.avalibleEquip = list(filter(lambda a: self.selectedSpecies.canWearArmor(a), aitems))
        self.avalibleEquip = [a for a in aitems if check_if_entity_can_wear_armor(self.selectedSpecies, a)]

    #resets the valueLeft and clears the items from the equipment slots
    def clearItems(self, window):
        self.valueLeft = 100

        windowWidthBlank = ' ' * window.width

        self.handItem.clear()
        self.offHandItem.clear()
        self.quiver.clear()

        for v in self.wornDict.values():
            v.clear()

        for m in self.miscItems:
            m.clear()

        for i in self.inventory:
            i.clear()

        for y in range(window.height):
            window.draw_str(0, y, windowWidthBlank)
        self.infoBuyItems(window)
        self.infoBoughtItems(window)
        self.drawInstructions(window)
        tdl.flush()

    def cycleThruItems(self, reverse=False):

        inc = (lambda : -1 if reverse else 1)

        self.itemNo-= inc()

        if self.itemNo < 0:
            self.itemNo = len(self.avalibleEquip) - 1
        elif self.itemNo >= len(self.avalibleEquip):
            self.itemNo = 0

    @property
    def selectedItem(self):
        return self.avalibleEquip[self.itemNo]

    def __swapEquipment(self, item, swapThisItemOut, *swapTheseItemsOut):
        subtractFromValue = item.value
        ajustment = 0

        #swapThisItemOut = nameOfAttrToSwapTo

        ajustment = swapThisItemOut.valueDiffrence(item)

        for c in swapTheseItemsOut:
            ajustment+= c.valueDiffrence(item)
            c.clear()

        if ajustment + self.valueLeft >= 0:

            swapThisItemOut.add(item)

            for c in swapTheseItemsOut:
                c.add(item)
            self.valueLeft+= ajustment

            #if swapThisItemOut is not None and swapThisItemOut.item is not None:

    def infoBuyItems(self, window):
        printList = []
        startY = 20
        startX = 40
        equipLength = len(self.avalibleEquip)

        limit = 5

        start = self.itemNo - limit
        end = self.itemNo + limit + 1

        if start < 0:
            printList+= self.avalibleEquip[equipLength + (start):]
            printList+= self.avalibleEquip[:end]
        elif end >= equipLength:
            printList+= self.avalibleEquip[start:]
            printList+= self.avalibleEquip[:end - equipLength]
        else:
            printList+= self.avalibleEquip[start:end]


        window.draw_str(startX, 10, 'Value Left: {: <5}'.format(self.valueLeft))
        tick = 0

        for n in printList:
            color = n.getColor.values

            if tick == limit:
                window.draw_str(startX, startY + tick, self.buyItemSelectedString.format(n.name), fg=color)
                #window.draw_str(40, 10 + tick, '*')
                #window.draw_str(60, 10 + tick, '*')
            else:
                window.draw_str(startX, startY + tick, self.buyItemString.format(n.name), fg=color)
            tick+=1

    def infoBoughtItems(self, window):

        #infoBoughtItems
        startY = 16
        startX = 22

        def checkValueAndPrintName(value, x, y):
            blankText = ' '*17
            text = ''
            if value.hasItem:
                if value.item.isStackable:
                    text = '{:<17}'.format(str(value))
                    #window.draw_str(x, y, , bg=ALL_COLORS_DICT['WHITE'])
                else:
                    text = '{:<17}'.format(str(value))
                    #window.draw_str(x, y, '  {:<17}'.format(str(value)))
            else:
                text = blankText
                #window.draw_str(x, y, '  {:<17}'.format(str(value)))

            window.draw_str(x, y, text, bg=ALL_COLORS_DICT['GREEN'].values)
            tdl.flush()

        tick = 0

        for n in self.EQUIP_PLACE_NAMES:

            window.draw_str(6, startY + tick, '{:>15}'.format(n))

            tick+=1

        tick = 0

        for a in ARMOR:
            checkValueAndPrintName(self.wornDict[a], startX, startY + tick)

            tick+=1

        checkValueAndPrintName(self.handItem, startX, startY + tick)
        tick+=1

        checkValueAndPrintName(self.offHandItem, startX, startY + tick)
        tick+=1

        checkValueAndPrintName(self.quiver, startX, startY + tick)
        tick+=1


        for i in self.miscItems:
            checkValueAndPrintName(i, startX, startY + tick)
            tick+=1

        for i in self.inventory:
            checkValueAndPrintName(i, startX, startY + tick)
            tick+=1

    def buySelectedItem(self):
        def findEmptySlot(item, listOfContainers):
            for l in listOfContainers:
                if not l.hasItem or item is l.item:
                    return l
            return listOfContainers[-1]

        if self.selectedItem.typeOfItem in self.wornDict:
            if check_if_entity_can_wear_armor(self.selectedSpecies, self.selectedItem):
            # if self.selectedSpecies.canWearArmor(self.selectedItem):
            #bodyDict[self.selectedItem.typeOfItem] in self.selectedItem.bodySlotTypesAllowed:
                self.__swapEquipment(self.selectedItem,
                    self.wornDict[self.selectedItem.typeOfItem]
                    #self.selectedSpecies.bodyDict[self.selectedItem.typeOfItem]
                    )
        elif self.selectedItem.typeOfItem in {'WEAPON', 'LAUNCHER'}:
            if self.selectedItem.isTwoHanded:
                self.__swapEquipment(self.selectedItem, self.handItem, self.offHandItem)
            elif self.handItem.hasItem:
                if self.handItem.hasItem and self.handItem.item.isTwoHanded:
                    self.__swapEquipment(self.selectedItem, self.handItem, self.offHandItem)
                else:
                    self.__swapEquipment(self.selectedItem, self.offHandItem)
            else:
                self.__swapEquipment(self.selectedItem, self.handItem)
        elif self.selectedItem.typeOfItem == 'SHIELD':
            if self.handItem.hasItem and self.handItem.item.isTwoHanded:
                self.__swapEquipment(self.selectedItem, self.offHandItem, self.handItem)
            else:
                self.__swapEquipment(self.selectedItem, self.offHandItem)
        elif self.selectedItem.typeOfItem == 'AMNUNITION':
            self.__swapEquipment(self.selectedItem, self.quiver)

        elif self.selectedItem.typeOfItem == 'MISC':
            slot = findEmptySlot(self.selectedItem, self.miscItems)

            #lengthMisc = max()
            self.__swapEquipment(self.selectedItem, slot)

        else:
            slot = findEmptySlot(self.selectedItem, self.inventory)
            self.__swapEquipment(self.selectedItem, slot)
        tdl.flush()

    #---------Charcter generations options below-------

    @property
    def isReady(self):
        if self.buyItems:
            return True
        else:
            return True
            #return self.statPoints == 0 and self.skillPoints == 0

    def reRollColors(self):
        self.colors = self.selectedSpecies.getColorDict

    def __breakUpString(self, wordString, maxLength, maxNumberOfLines):
        carrageReturns = []

        blankSpace = ' ' * maxLength

        lengthLeft = len(wordString)
        progress = 0
        sizeOfBiggestWord = max([len(w) for w in wordString.split(' ')])

        """assume that sizeOfBiggestWord = 8,
        maxLength = 40
        len(wordString) = 75

        so:
        ind = index(' ', max(40 - 8, (0 + 40) - 8)
        ind = index(' ', max(32, 32))
        thus index will be at least 32

        assume that a space is found on index 37, so progress now equals 37
        next loop:
        ind = index(' ', max(40 - 8), (37 + 40) - 8)
        ind = index(' ', max(32, 69))
        thus index will be at least 96
        """

        while progress < len(wordString):
            try:
                ind = wordString.index(' ', max(maxLength - sizeOfBiggestWord, (progress + maxLength) - sizeOfBiggestWord)) + 1
            except ValueError:
                break
            carrageReturns.append(''.join(['{:<', str(maxLength), '}']).format(wordString[progress:ind]))

            progress = ind
        carrageReturns.append(''.join(['{:<', str(maxLength), '}']).format(wordString[progress:]))

        if len(carrageReturns) < maxNumberOfLines:
            for l in range(len(carrageReturns) - maxNumberOfLines):
                carrageReturns.append(blankSpace)

        return carrageReturns

    def toggleSpecies(self, reverse=False):
        if reverse:
            self.speciesNo-=1
            if self.speciesNo < 0:
                self.speciesNo = len(self.speciesAvliable) - 1
        else:
            self.speciesNo+=1
            if self.speciesNo >= len(self.speciesAvliable):
                self.speciesNo = 0
        if self.selectedSpecies != self.speciesAvliable[self.speciesNo]:
            self.selectedGender = 0
        #self.selectedSpecies = self.speciesAvliable[self.speciesNo]
        self.reRollColors()

    @property
    def selectedSpecies(self):
        return self.speciesAvliable[self.speciesNo]

    @property
    def getGender(self):
        return self.selectedSpecies.genders[self.selectedGender]

    def speciesInfo(self, window):
        #self.selectedSpecies = self.speciesAvliable[self.speciesNo]

        info = '''{0.name:^10}\n
Base Health: {0.maxHealth}
Base Stamna: {0.maxStamna}
Base Mana:   {0.maxMagic}\n
Land Movement Speed: {0.landSpeed:3}
Water Movement Speed: {0.waterSpeed:3}\n
Natural Armor: {0.naturalArmor}
Glamor: {0.glamor}\n\n'''.format(self.selectedSpecies).split('\n')

        #info+= self.__dictHelper(self.selectedSpecies.baseStats, ALL_STATS, STAT_NAMES, 3, 2, prefix='Base ')

        for st, sn in zip(ALL_STATS, STAT_NAMES):
            info.append('Base {}: {:>2}'.format(sn, self.selectedSpecies.baseStats[st]))

        info.append('\n')
        info.append('\n')

        #info+= self.__dictHelper(self.selectedSpecies.skillAppitude, ALL_SKILLS, SKILL_NAMES, 7, 2, prefix='Aptitude ')

        for st, sn in zip(ALL_SKILLS, SKILL_NAMES):
            info.append('Aptitude {:<8} {:>2}'.format('{}:'.format(sn), self.selectedSpecies.skillAppitude[st]))

        info.append('\n')
        info.append('\n')
        des = self.selectedSpecies.description.replace('\n', ' ')
        info+= self.__breakUpString(des, 60, 8)
        #info.append(self.selectedSpecies.description)
        li = 4
        for i in info:
            window.draw_str(2, li, i)
            li+=1


    @property
    def appearenceToText(self):
        cd = self.selectedSpecies.getColorDict

        tMat = self.selectedSpecies.bodyMaterialDict['UPPER_BOD']

        tColor = cd.get(self.selectedSpecies.bodyMaterialDict['UPPER_BOD'], '')

        return self.selectedSpecies.appearence.format(
            headcolor=cd.get(self.selectedSpecies.bodyMaterialDict['HEAD'], ''),
            torsocolor=cd.get(self.selectedSpecies.bodyMaterialDict['UPPER_BOD'], ''),
            handcolor=cd.get(self.selectedSpecies.bodyMaterialDict['HANDS'], ''),
            legcolor=cd.get(self.selectedSpecies.bodyMaterialDict['LOWER_BOD'], ''),
            feetcolor=cd.get(self.selectedSpecies.bodyMaterialDict['FEET'], ''),
            heshe=PRONOUN_DICT['GEN_YOU']['subject'], heshecap=PRONOUN_DICT['GEN_YOU']['subject'].capitalize(),
            hashave=PRONOUN_DICT['GEN_YOU']['hashave'], isare=PRONOUN_DICT['GEN_YOU']['isare'])

    def appearinceInfo(self, window):
        #newLineCount = self.selectedSpecies.description.count('\n') + 4
        app = self.appearenceToText.replace('\n', ' ')

        newString = self.__breakUpString(app, 50, 12)
        newLineCount = 20

        for s in newString:
            window.draw_str(30, newLineCount, s)
            newLineCount += 1

            """
    @property
    def getStatOrSkillFromID(self):
        if self.statOrSkillSelected < len(STAT_NAMES):
            return ALL_STATS[self.statOrSkillSelected]
        else:
            return ALL_SKILLS[self.statOrSkillSelected - len(STAT_NAMES)]
    """

    def statInfo(self, window):
        info = '''Stat Pts. Left : {0.statPoints:>2}\n\n'''.format(self).split('\n')

        for stat, statname, star in zip(ALL_STATS, STAT_NAMES, range(len(ALL_STATS))):
            try:
                info.append('{2} {0}: {1:>2} {2}'.format(statname, self.statDict[stat], self.space[star]))
            except IndexError:
                print('Error: stat name is {}, stat keys is {}, star counter is {}, range is {}'.format(statname, stat, star, range(len(ALL_STATS))))

        li = 2
        for i in info:
            window.draw_str(30, li, i)
            li+=1

    def skillInfo(self, window):
        info = '''Skill Pts. Left: {0.skillPoints:>2}\n\n'''.format(self).split('\n')

        for skill, skillname, star in zip(ALL_SKILLS, SKILL_NAMES, range(len(ALL_STATS), self.statPlusSkillLength)):
            try:
                info.append('{2} {0:<8} {1:>2} {2}'.format('{}:'.format(skillname), self.skillDict[skill], self.space[star]))
            except IndexError:
                print('Error: skill name is {}, skill keys is {}, star counter is {}, range is {}'.format(skillname, skill, star, range(len(ALL_STATS), self.statPlusSkillLength)))

        li = 2
        for i in info:
            window.draw_str(55, li, i)
            li+=1

    def toggleGender(self):
        self.selectedGender+=1
        if self.selectedGender >= len(self.selectedSpecies.genders):
            self.selectedGender = 0

    def genderInfo(self, window):
        selGen = self.selectedSpecies.genders[self.selectedGender]
        name = PRONOUN_DICT[selGen]['name']
        window.draw_str(2, 2, '{0:^10}'.format(name))

    def toggleStatOrSkill(self, reverse=False):
        incOrDeinc = lambda : -1 if reverse else 1

        i = incOrDeinc()

        newSelection = self.statOrSkillSelected + i

        self.space[self.statOrSkillSelected] = ' '
        if newSelection < 0:
            self.statOrSkillSelected = self.statPlusSkillLength - 1
        elif newSelection >= self.statPlusSkillLength:
            self.statOrSkillSelected = 0
        else:
            self.statOrSkillSelected = newSelection
        self.space[self.statOrSkillSelected] = '*'


    def incrementStatOrSkill(self, decrease=False):
        incOrDeinc = lambda : -1 if decrease else 1

        i = incOrDeinc()

        selectionHelper = list(ALL_STATS) + list(ALL_SKILLS)

        #statSelected
        #skillSelected = self.statOrSkillSelected - len(ALL_STATS)

        selected = selectionHelper[self.statOrSkillSelected]




        if selected in ALL_SKILLS:#if using skills
            newAmount = self.skillDict[selected] + i
            if newAmount >= 0 and self.skillPoints - i >= 0:
                self.skillDict[selected]+= i
                self.skillPoints-=i
        else:
            newAmount = self.statDict[selected] + i
            if newAmount >= 0 and self.statPoints - i >= 0:
                self.statDict[selected]+= i
                self.statPoints-=i


    def drawInstructions(self, window):
        if self.buyItems:
            window.draw_str(3, 1, 'Up and down keys: Cycle through the avaliable items')
            window.draw_str(3, 2, 'Space: Purchesses the highlighted item.')
            window.draw_str(3, 3, 'R: Resets the player\'s purchesed items')
            window.draw_str(3, 4, 'Return/Enter: Begins the game')
        else:
            window.draw_str(3, 1, 'Up and down keys: Cycle through the avaliable stats/skills')
            window.draw_str(3, 2, 'Left and right keys: increase or decrease stats/skills')
            window.draw_str(3, 3, 'R: Rerolls the player\'s appearence')
            window.draw_str(3, 4, 'Return/Enter: When all points have been distributed, the player is taken to the equipment customization screen.')

    """
    def __checkWornDictForNoneTypes(self, key):
        if self.wornDict[key].hasItem:
            return
handItem, offHandItem, quiver
    """
    def generateEquipment(self, x, y):
        return {k: UniversalGameItem.spawnForPlayer(self.wornDict[k].item, x, y) for k in ARMOR}

    def generateMisc(self, x, y):
        return [UniversalGameItem.spawnForPlayer(m.item, x, y) for m in self.miscItems]

    def generateInventory(self, x, y):
        return [UniversalGameItem.spawnForPlayer(i.item, x, y, i.amount) for i in self.inventory]

    def generateHandItem(self, x, y):
        return UniversalGameItem.spawnForPlayer(self.handItem.item, x, y)

    def generateOffHandItem(self, x, y):
        return UniversalGameItem.spawnForPlayer(self.offHandItem.item, x, y)

    def generateQuiver(self, x ,y):
        return UniversalGameItem.spawnForPlayer(self.quiver.item, x, y, self.quiver.amount)

    def generateDummyItem(self):
        return UniversalGameItem.spawnDummyItem(0, 0)
