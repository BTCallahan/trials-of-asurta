from random import randint, choice
from math import radians, atan2, sin
from data_globals import rollAttack, FILE_LOCATION_NAME, checkForMandatoryInfo, checkForOptionalInfo
from coords import Coords
from color_factory import ALL_COLORS_DICT
from terrain import Rectangle
import re

def checkConeBest(caster, target, gl, degrees):
    r = radians(degrees)
    offset = (target.co - caster.co).normalize
    angleToTarget = atan2(offset.x, offset.y)

    otherWithin = []
    for e in gl.allEntities:
        off = e.co - caster.co
        angleToEntity = atan2(off.x, off.y)
        if abs(angleToEntity - angleToTarget) <= r:
            otherWithin.append(e)

    return otherWithin


def rollDice(dice, diceSides):
    if dice <= 1:
        return randint(1, diceSides)
    else:
        return randint(1, diceSides) + rollDice(dice - 1, diceSides)


def doNothing(gl, target, amount):
    pass


def restoreHealth(gl, target, amount):
    target.health.addTo(amount)


def restoreMagic(gl, target, amount):
    target.magic.addTo(amount)


def blastEntity(gl, target, amount):
    target.health.addTo(-amount)


def _teleport(gl, target, amount):

    level_rect = gl.get_rectangle
    target_co = target.co

    user_centered_rect = Rectangle(target_co.x - amount, target_co.x + amount, target_co.y - amount, target_co.y + amount)

    new_rect: Rectangle = level_rect.boolian_intersect(user_centered_rect)

    def gen_coords_in_rect():
        for y in range(new_rect.topEdge, new_rect.bottomEdge):
            for x in range(new_rect.leftEdge, new_rect.rightEdge):
                dist = Coords.distance_static(x, target_co.x, y, target_co.y)
                if dist <= amount and gl.grid[y][x].moveThru:
                    yield Coords(x, y)

    random_coords = set(gen_coords_in_rect())

    entity_coords = set((c for c in gl.allEntities))

    new_coords = random_coords - entity_coords

    target.co = choice(list(new_coords))


subEffectDict = {'HEAL_HEALTH': (lambda gl, t, a: t.health.addTo(-a)),
                 'HEAL_MANA': (lambda gl, t, a: t.magic.addTo(-a)),
                 'HEAL_STAMNA': (lambda gl, t, a: t.stamna.addTo(-a)),
                 'HARM_STAMNA': (lambda gl, t, a: t.stamna.addTo(a)),
                 'HARM_HEALTH': (lambda gl, t, a: t.health.addTo(a)),
                 'ID_ITEM': (lambda gl, t, a: t.ai.item_to_affect.identify_item()),
                 'TELEPORT': _teleport
                 }

"""
effect: the they of effect that
"""


class SubEffect:
    def __init__(self, dice: int, diceSides: int, effectType: str):
        self.dice = dice
        self.diceSides = diceSides
        self.effectType = effectType
    
    def __str__(self):
        return '{}, {}d{}'.format(self.effectType, self.dice, self.diceSides)
    
    def runEffect(self, gl, t, distanceMulti=1.0):
        if distanceMulti == 1.0:

            subEffectDict[self.effectType](gl, t, rollAttack(self.dice, self.diceSides))
        else:
            a = round(rollAttack(self.dice, self.diceSides) * distanceMulti)

            subEffectDict[self.effectType](gl, t, a)

    @property
    def long_description(self):
        des = []

        number = '{} d {}'.format(self.dice, self.diceSides)

        if self.effectType.endswith('HEALTH'):
            eff = 'health'
        elif self.effectType.endswith('MANA'):
            eff = 'mana'
        elif self.effectType.endswith('STAMNA'):
            eff = 'stamna'
        else:
            eff = ''

        if self.effectType.startswith('HEAL'):
            des.append('It restores {} {}.'.format(number, eff))
        elif self.effectType.startswith('HARM'):
            des.append('It damages the targets')
            des.append(eff)
            des.append('by {}.'.format(number))
        else:
            des.append('It identifies an item')

        return ' '.join(des)

    @property
    def getAverageEffectPower(self):
        return self.dice * self.diceSides * 0.5 + self.dice * 0.5
    
    def __hash__(self):
        return hash((self.dice, self.diceSides, self.effectType))
    
    def __eq__(self, o):
        return hash(self) == hash(o)
        
class MagicEffect:
    """
    @classmethod
    def effectSelf(cls, effect, name, cost, dice, diceSides, difficulty=0,
    timesToFire=1, canLearn=True, staff=True, talisman=True, knot=True):
        return cls(effect, name, cost, dice, diceSides, difficulty=0,
        timesToFire=timesToFire, canLearn=canLearn, staff=staff,
        talisman=talisman, knot=knot)
    """

    def __str__(self):
        def strInfo(x, text):
            if x > 0:
                return ', {}: {}'.format(text, x)
            return ''

        return '{0.name} {0.effectTarget} {1}, {0.cost}{2}{3}{4}{5}'.format(
            self, ', '.join([str(s) for s in self.subEffects]), strInfo(self.maxRange, 'Range'),
            strInfo(self.radius, 'Radius'), strInfo(self.degrees, 'Degrees'), strInfo(self.toHit, 'To Hit'),
            strInfo(self.coolDown, 'Cool down'))
    
    def __init__(self, name, effectTarget: str, subEffects, cost: int=0, depth: int=0, value: int=0, difficulty:int=0,
    maxRange:int=0, radius: int=0, degrees: int=0, toHit: int=0, coolDown: int=0, costType: str='MANA', canLearn: int=True, staff=True,
    talisman=True, knot=True, abilityStatUsed='NONE',  passThruMiltipleEntities=False):
        self.name = name
        self.effectTarget = effectTarget
        self.subEffects = tuple(subEffects)
        self.difficulty = difficulty
        self.cost = cost
        self.costType = costType
        self.depth = depth
        self.value = value
        self.radius = radius
        self.maxRange = maxRange
        self.degrees = degrees
        self.toHit = toHit
        self.coolDown = coolDown
        if self.cost < 1:
            self.max_charges = self.coolDown // 12
        else:
            self.max_charges = (self.cost // self.coolDown) * 2
        self.canLearn = canLearn
        self.staff = staff
        self.talisman = talisman
        self.knot = knot
        self.abilityStatUsed = abilityStatUsed
        self.passThruMiltipleEntities = passThruMiltipleEntities

        self.fullName = str(self)

        self.__hash = hash((self.effectTarget, 
                            self.subEffects, self.name, self.effectTarget, self.cost,
                            self.radius, self.maxRange, self.degrees,
                            self.difficulty, self.canLearn, self.staff, self.knot,
                            self.abilityStatUsed,
                            self.passThruMiltipleEntities))

    def __eq__(self, o):
        return hash(self) == hash(o)

    def __hash__(self):
        return self.__hash

    def checkEquipColor(self, entity):
        return ALL_COLORS_DICT['WHITE']

    @property
    def requires_targeting(self):
        return self.effectTarget not in {'SELF', 'AREA'}

    @property
    def long_description(self) -> str:

        des = []

        if self.effectTarget == 'SELF':

            des.append('It affects the user.')

        elif self.effectTarget == 'MEELE':

            des.append('It affects any entity in meele range.')

        elif self.effectTarget == 'CONE':

            des.append('It affects all entities in a {} degree cone that are {} or less spaces to the user.'.format(
                self.degrees, self.max_charges))

        elif self.effectTarget == 'BALL':

            des.append('It affects any entites within a {} space radius sphere. '
                       'This sphere may be targeted up to {} spaces away.'.format(self.radius, self.maxRange))
        elif self.effectTarget == 'BOLT':
            des.append('It affects any entity within a range of {} spaces.'.format(self.maxRange))

        des.append('\nEffects:')

        for s in self.subEffects:
            des.append('\n')
            des.append(s.long_description)

        return ' '.join(des)

    @property
    def getAverageSubeffectsPower(self):
        return [e.getAverageEffectPower for e in self.subEffects]

    def can_use(self, user):
        if self.costType == 'MANA':
            if user.magic.amount >= self.cost:
                return True
            return user.stamna.amount >= (self.cost - user.magic.amount) * 2
        if self.costType == 'STAMINA':
            if user.stamna.amount >= self.cost:
                return True
            return False
        return user.health.amount * 1 > self.cost

    #TODO: Finish
    def calculateIfThisEffectShouldBeUsed(self, user):

        if self in user.grimore:
            sucessChance = self.calculateSuccessPercent(user.getSkillPlusBonus('SKILL_SPELLCRAFT'))
            reserve = user.magic + user.stamna * 0.5
            ajustedCost = 1.0 - (reserve / self.cost)
            power = sum(self.getAverageSubeffectsPower)

    def calculateSuccessPercent(self, skill):
        sucesses = 0
        failures = 0
        for i in range(2, 2 * 8):
            if i + skill > self.difficulty:
                sucesses += 1
            else:
                failures += 1
        return sucesses / (sucesses + failures)

    def useSpell(self, gl, user, targetCo):
        user.magic.addTo(-self.cost)
        if user.getSkillPlusBonus('SKILL_SPELLCRAFT') + rollAttack(2, 8) > self.difficulty:
            self.__magicEffect(gl, user, targetCo)
        else:
            user.incrementSkill('SKILL_SPELLCRAFT')

    def useDevice(self, gl, user, targetCo):
        if user.getSkillPlusBonus('SKILL_MAGIC_DEVICE') + rollAttack(2, 8) > self.difficulty:
            self.__magicEffect(gl, user, targetCo)

        else:
            user.incrementSkill('SKILL_MAGIC_DEVICE')

    def useAbility(self, gl, user, targetCo):
        self.__magicEffect(gl, user, targetCo)
        if self.costType == 'STAMINA':
            user.stamna.addTo(-self.cost)
        elif self.costType == 'HEALTH':
            user.health.addTo(-self.cost)
        else:
            user.magic.addTo(-self.cost)
        user.abilityCooldowns[self] = self.coolDown

    def __self_effect(self, gl, user, targetCo, runEffect):
        runEffect(user)
    
    def __meele_effect(self, gl, user, targetCo, runEffect):
        eList = list(filter(lambda e: user.co.distance(e.co) < 1.5 and e is not user, gl.allEntities))

        if len(eList) > 0:
            runEffect(eList[0])
    
    def __coneEffect(self, gl ,user, targetCo, runEffect):
        eList = gl.getEntitiesInCone(user, targetCo, self.degrees, maxRange=self.maxRange)

        for e in eList:
            dist = user.co.distance(e.co)

            #if rollAttack(2, 6) - round(dist)) > 0):#to hit roll
            runEffect(e, dist)
    
    def __ballEffect(self, gl ,user, targetCo, runEffect):
        eList = gl.getEntitiesInLineOfFire(user, targetCo, maxRange=self.maxRange)
        #eList = gl.getEntitiesBetweenPoints(user.co, targetCo, maxEntities=10000, maxRange=self.maxRange)
        ip = (user.co - targetCo).normalize()
        impactPoint = Coords(round(ip[0] * self.maxRange), round(ip[1] * self.maxRange))
        if len(eList) > 0:

            for e in eList:
                dist = user.co.distance(e.co)
                if rollAttack(2, 6) - dist > 0:#to hit roll
                    impactPoint = e.co

                    break
            if self.radius > 0:
                # entitiesInBlastArea = list(filter(lambda x: not gl.checkForObstructionBetweenPoints(x.co, impactPoint, maxRange=self.radius) and x.co != impactPoint, gl.allEntities))
                entitiesInBlastArea = list((e for e in gl.allEntities if
                                            e.co != impactPoint and not gl.checkForObstructionBetweenPoints(e.co,
                                                                                                            impactPoint,
                                                                                                            maxRange=self.radius)))
                map(lambda x: runEffect(x, x.co.distance(impactPoint)), entitiesInBlastArea)
        else:
            # entitiesInBlastArea = list(filter(lambda x: not gl.checkForObstructionBetweenPoints(x.co, impactPoint, maxRange=self.radius) and x.co != impactPoint, gl.allEntities))
            entitiesInBlastArea = list((e for e in gl.allEntities if
                                        e.co != impactPoint and not gl.checkForObstructionBetweenPoints(e.co,
                                                                                                        impactPoint,
                                                                                                        maxRange=self.radius)))

            map(lambda x: runEffect(x, x.co.distance(impactPoint)), entitiesInBlastArea)
    
    def __boltEffect(self, gl ,user, targetCo, runEffect):
        eList = gl.getEntitiesInLineOfFire(user, targetCo, maxRange=self.maxRange)
        #ip = (user.co - targetCo).normalize()

        if len(eList) > 0:

            for e in eList:
                dist = user.co.distance(e.co)
                if rollAttack(2, 6) - dist > 0:#to hit roll
                    if e.getShieldBlock < rollAttack(1, 4):
                        runEffect(e, dist)
                    break

    def __areaEffect(self, gl ,user, targetCo, runEffect):

        entitiesInBlastArea = list((e for e in gl.allEntities if
                                    e.co != user.co and not gl.checkForObstructionBetweenPoints(e.co,
                                                                                                    user.co,
                                                                                                    maxRange=self.maxRange)))
        map(lambda x: runEffect(x, x.co.distance(user.co)), entitiesInBlastArea)

    effectDict = {
        'SELF': __self_effect,
        'MEELE': __meele_effect,
        'CONE': __coneEffect,
        'BALL': __ballEffect,
        'BOLT': __boltEffect,
        'AREA': __areaEffect
        }
    
    def __magicEffect(self, gl, user, targetCo):

        def runEffect(target, distance=0):
            d = (self.maxRange - distance)
            for se in self.subEffects:
                se.runEffect(gl, target, d)
            #for ti in range(self.timesToFire):
            #    self.effect(gl, target, max(0, rollDice(self.dice, self.diceSides) - round(distance)) + user.getTotalStat('STAT_MAG'))
        
        self.effectDict[self.effectTarget](gl, user, targetCo, runEffect)

DUMMY_EFFECT = MagicEffect('', 'NONE', [])

def buildEffectsDict(fileName):
    """Returns a string : MagicEffect dictionary"""

    allEffects = dict()

    s = open(FILE_LOCATION_NAME + fileName, 'r')

    a = s.read()

    eList = re.split('NAME:', a)

    for ep in eList:

        if re.match(r'(.+)\n', ep):

            i = re.findall(r'^(.+)\n', ep)


            key, name = re.split(r'[:]', i[0])

            def effectMandatoryCheck(textToLookFor, dataType, isList=False, listLength=-1):
                return checkForMandatoryInfo(textToLookFor, ep, dataType, 'effects.txt', key, isList, listLength)
            
            def effectOptionalCheck(textToLookFor, dataType, default, isList=False, acceptNewlines=False):
                return checkForOptionalInfo(textToLookFor, ep, dataType, default, isList, acceptNewlines)
            
            def effectFlagPresent(textToLookFor):
                return re.search(textToLookFor, ep)

            value, depth = effectMandatoryCheck('DATA:', 'INT', True, 2)

            effectType = effectMandatoryCheck('EFFECT:', 'STR')

            cost = effectMandatoryCheck('COST:', 'INT')

            coolDown = effectOptionalCheck('COOLDOWN:', 'INT', cost)

            effectsList = []

            for eff in re.finditer(r'DICE:(.+)\n', ep):

                aSplit = re.split(r'[:]', eff.group(0))

                effectsList.append(SubEffect(int(aSplit[1]), int(aSplit[2]), aSplit[3]))


            difficulty = effectMandatoryCheck('DIFFICULTY:', 'INT')

            statUsed = effectOptionalCheck('STAT:', 'STR', 'NONE')

            toHit = effectOptionalCheck('TO_HIT:', 'INT', 0)

            maxRange = effectOptionalCheck('RANGE:', 'INT', 0)

            radius = effectOptionalCheck('RADIUS:', 'INT', 0)

            degrees = effectOptionalCheck('DEGREES:', 'FLOAT', 0.0)

            costType = effectOptionalCheck('COST_TYPE:', 'STR', 'MANA')

            def checkVailidEffectUses():
                if effectFlagPresent(r'ABILITY_ONLY'):
                    return False, False, False, False
                else:
                    return not effectFlagPresent(r'NO_LEARN'), not effectFlagPresent(r'NO_TALISMAN'), \
not effectFlagPresent(r'NO_KNOT'), not effectFlagPresent(r'NO_STAFF')

            canLearn, canTalisman, canKnot, canStaff = checkVailidEffectUses()

            allEffects[key] = MagicEffect(name, effectType, effectsList, cost, depth, value,
                                          difficulty,  maxRange, radius, costType=costType,
                                          degrees=degrees, toHit=toHit, coolDown=coolDown,
                                          canLearn=canLearn, talisman=canTalisman, knot=canKnot, staff=canStaff, abilityStatUsed=statUsed)

    s.close()

    return allEffects
            
ALL_EFFECT_DICT = buildEffectsDict('/library/effects.txt')

ALL_SPELLS = tuple(filter(lambda x: x.canLearn, ALL_EFFECT_DICT.values()))

ALL_SPELLS_DICT = {k: v for k, v in ALL_EFFECT_DICT.items() if v.canLearn}

ALL_KNOTS_DICT = {k: v for k, v in ALL_EFFECT_DICT.items() if v.knot}
ALL_STAFFS_DICT = {k: v for k, v in ALL_EFFECT_DICT.items() if v.staff}
ALL_TALISMANS_DICT = {k: v for k, v in ALL_EFFECT_DICT.items() if v.talisman}

EFFECTS_BY_ITEM_TYPE = {
    'GLYPH' : ALL_SPELLS_DICT,
    'KNOT' : ALL_KNOTS_DICT,
    'STAFF' : ALL_STAFFS_DICT,
    'TALISMAN' : ALL_TALISMANS_DICT
}
"""EFFECTS_BY_ITEM_TYPE is a string : dictionary dict. Each of the dictionarys 
that it uses for items is a string : MagicEffect dict."""

def getLearnableSpells(skill):
    return list(filter(lambda x: x.calculateSuccessPercent(skill) > 0.0), ALL_SPELLS)
