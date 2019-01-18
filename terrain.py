from typing import List, Union, Tuple

from data_globals import rollAttack
from random import randrange, randint, choice, uniform
from random import random as randFloat
from coords import Coords
from color_factory import ALL_COLORS_DICT
#from entites import testSpawn

def clamp(number, minNum, maxNum):
    return min(max(number, minNum), maxNum)

BLOCKS_NOTHING = 0
BLOCKS_MOVEMENT = 1 << 0
BLOCKS_SIGHT = 1 << 1
BLOCKS_FIRE = 1 << 2

BLOCKS_TUPLE = tuple([BLOCKS_MOVEMENT, BLOCKS_SIGHT, BLOCKS_FIRE])

def setTileBlockings(*args):
    bl = BLOCKS_NOTHING
    for a, b in zip(args, BLOCKS_TUPLE):
        if not a:
            bl = bl | b
    return bl

class Terrain:
    def __init__(self, symbol, fgColor, bgColor, moveThru=False, seeThru=False,
    fireThru=False, isWater=False, stairType=None, destructionTile='',
    openTile='', closeTile='', description=''):
        self.symbol = symbol
        self.fgColor = ALL_COLORS_DICT[fgColor]
        self.bgColor = ALL_COLORS_DICT[bgColor]

        self.moveThru = moveThru
        self.seeThru = seeThru
        self.fireThru = fireThru
        self.isWater = isWater
        self.stairType = stairType
        self.destructionTile = destructionTile
        self.openTile = openTile
        self.closeTile = closeTile
        self.blockTypes = setTileBlockings(moveThru, seeThru, fireThru)
        self.description = description

    def __hash__(self):
        return hash((self.symbol, self.fgColor, self.bgColor,
        self.moveThru, self.seeThru, self.fireThru, self.isWater))

    def __eq__(self, other):
        return hash(self) == hash(other)

    @property
    def isDestroyable(self):
        return self.destructionTile != ''

    def canBeMovedThru(self, isFlying):
        return (isFlying and self.isWater) or self.moveThru

    @property
    def isUpstairs(self):
        return self.stairType == 0 or self.stairType == 1

    @property
    def isDownstairs(self):
        return self.stairType == 0 or self.stairType == -1


ALL_TILE_DICT = {
    'TERRAIN_BORDER' : Terrain('&', 'WHITE', 'BLACK'),
    'TERRAIN_OPEN' : Terrain('.', 'WHITE', 'GREY_DARK', True, True, True),
    'TERRAIN_WALL' : Terrain('#', 'WHITE', 'GREY_LIGHT', destructionTile='TERRAIN_OPEN'),
    'TERRAIN_WATER' : Terrain('~', 'AQUA', 'BLUE_DARK', isWater=True),
    'TERRAIN_PILLAR' : Terrain('|', 'GREY_LIGHT', 'GREY_DARK', seeThru=True, destructionTile='TERRAIN_OPEN'),
    'TERRAIN_UP_STAIR' :  Terrain('<', 'GREY_LIGHT', 'JET', True, True, True, stairType=1, description='stairway up'),
    'TERRAIN_DOWN_STAIR' : Terrain('>', 'GREY_LIGHT', 'JET', True, True, True, stairType=-1, description='stairway down'),
    'TERRAIN_STAIR' : Terrain('^', 'GREY_LIGHT', 'JET', True, True, True, stairType=0, description='stairway up and down'),
    'TERRAIN_DOOR_CLOSED' : Terrain('+', 'BROWN', 'GREY_DARK', destructionTile='TERRAIN_OPEN', openTile='TERRAIN_DOOR_OPEN'),
    'TERRAIN_DOOR_OPEN' : Terrain(',', 'BROWN', 'GREY_DARK', destructionTile='TERRAIN_OPEN', closeTile='TERRAIN_DOOR_CLOSED'),
}

class Trap:
    def __init__(self, name, effect, detectDiff, disarmDiff, timesCanFire=1):
        self.name = name
        self.trapEffect = effect
        self.detectDiff = detectDiff
        self.disarmDiff = disarmDiff
        self.timesCanFire = timesCanFire

    def tryToDisarm(self, entity):
        roll = rollAttack(2, 4)
        if entity.getSkillPlusBonus('SKILL_TRAPS') + roll >= self.disarmDiff:
            return 1
        else:
            if entity.getSkillPlusBonus('SKILL_TRAPS') + 8 < self.disarmDiff:
                self.trapEffect.effect(entity)
                return -1
            #entity.incrementSkill('SKILL_TRAPS')
            return  0

def trapDict(name, effect, detectDiff, disarmDiff, depth, timesCanFire=1):
    return {'name' : name, 'effect' : effect, 'detectDiff' : detectDiff, 'disarmDiff' : disarmDiff, 'depth' : depth, 'timesCanFire' : timesCanFire}

TRAP_PIT =      trapDict('pit trap', None, 4, 9, 0)
TRAP_DARTS =    trapDict('dart trap', None, 3, 6, 0, 12)
TRAP_ARROWS =   trapDict('arrow trap', None, 6, 7, 0, 5)

class TrapContainer:
    def __init__(self, trap, x, y):
        self.__trap = trap
        self.co = Coords(x, y)
        self.timesFired = 0
        self.visible = False

    @property
    def canFire(self):
        return self.timesFired != self.__trap['timesCanFire']

    def __str__(self):
        if self.canFire:
            return self.__trap['name']
        else:
            return 'empty ' + self.__trap['name']

    def disarm(self):
        self.timesFired = self.__trap['timesCanFire']

    def tryToDisarm(self, entity):
        roll = rollAttack(2, 4)
        if entity.getSkillPlusBonus('SKILL_TRAPS') + roll >= self.__trap['disarmDiff']:
            self.disarm()
        else:
            if entity.getSkillPlusBonus('SKILL_TRAPS') + 8 < self.__trap['disarmDiff']:
                self.__trap['effect'](entity)

            entity.incrementSkill('SKILL_TRAPS')

    def blunderInto(self, entity):
        self.__trap['effect'](entity)
        entity.incrementSkill('SKILL_DETECT_TRAPS')
        self.visible = True

class Rectangle:
    def __init__(self, leftEdge, rightEdge, topEdge, bottomEdge):
        self.leftEdge = leftEdge
        self.rightEdge = rightEdge
        self.topEdge = topEdge
        self.bottomEdge = bottomEdge

    @property
    def width(self):
        return self.rightEdge - self.leftEdge

    @property
    def height(self):
        return self.bottomEdge - self.topEdge

    @property
    def center_x(self):
        return  self.leftEdge + self.width * 0.5

    @property
    def center_y(self):
        return self.topEdge + self.height * 0.5

    def boolian_intersect(self, other):
        if self.checkOverlap(other):

            new_left = max(self.leftEdge, other.leftEdge)
            new_right = min(self.rightEdge, other.rightEdge)

            new_top = max(self.topEdge, other.topEdge)
            new_bottom = min(self.bottomEdge, other.bottomEdge)

            return Rectangle(new_left, new_right, new_top, new_bottom)
        return False

    def checkOverlap(self, otherList):

        # assert isinstance(other, Rectangle), 'other (type %s)_is not a Rectangle or Room' % type(other)

        #if not isinstance(other, Rectangle):
        #    raise TypeError('other (type %s)_is not a Rectangle or Room'.format(type(other)))

        if isinstance(otherList, List) or isinstance(otherList, Tuple):

            for o in otherList:
                assert isinstance(o, Rectangle), 'other entry o (type %s)_is not a Rectangle or Room' % type(o)

                horizontalOverlap = self.rightEdge >= o.leftEdge and self.leftEdge <= o.rightEdge
                verticalOverlap = self.bottomEdge >= o.topEdge and self.topEdge <= o.bottomEdge
                if horizontalOverlap and verticalOverlap:
                    return True

            return False
        elif isinstance(otherList, Rectangle):
            horizontalOverlap = self.rightEdge >= otherList.leftEdge and self.leftEdge <= otherList.rightEdge
            verticalOverlap = self.bottomEdge >= otherList.topEdge and self.topEdge <= otherList.bottomEdge
            return horizontalOverlap and verticalOverlap

    def clamp_distance(self, other, distance):
        if self.rightEdge < other.leftEdge - distance:
            # shift the other towards us (ie, leftward)

            new_other_left_edge = min(other.leftEdge, other.leftEdge - distance)
            other.rightEdge = new_other_left_edge + other.width
            other.leftEdge = new_other_left_edge

        elif self.leftEdge > other.rightEdge + distance:

            new_other_right_edge = max(other.rightEdge, other.rightEdge + distance)
            other.leftEdge = new_other_right_edge - other.width
            other.rightEdge = new_other_right_edge

        if self.bottomEdge < other.topEdge - distance:

            new_other_top_edge = min(other.topEdge, other.topEdge - distance)
            other.bottomEdge = new_other_top_edge + other.height
            other.topEdge = new_other_top_edge
        elif self.topEdge > other.bottomEdge + distance:
            new_other_bottom_edge = max(other.bottomEdge, other.bottomEdge + distance)
            other.topEdge = new_other_bottom_edge - other.height
            other.bottomEdge = new_other_bottom_edge

class Room(Rectangle):

    def __init__(self, leftEdge, rightEdge, topEdge, bottomEdge):
        super().__init__(leftEdge, rightEdge, topEdge, bottomEdge)

        #self._checkerSet = set()
        self._spawnSpots = []
        self._pillarSpots = []

        for y in self.topToBottomRange:
            for x in self.leftToRightRange:
                #self._checkerSet.add(tuple([x, y]))
                self._spawnSpots.append(tuple([x, y]))
        self.placePillars()

    """
    def __del__(self):
        self._spawnSpots = []
        self._pillarSpots = []
    """


    @staticmethod
    def __calculateSize(levelWidth, levelHeigth, roomSizePercent, extraPercent=0.0, prevous_room=None):
        etra_percent_width = uniform(-extraPercent, extraPercent)
        extra_percent_height = uniform(-extraPercent, extraPercent)
        # etra_percent_width and extra_percent_height are random values between -extraPercent and extraPercent

        widthPercent = round((roomSizePercent + etra_percent_width) * levelWidth)
        heightPercent = round((roomSizePercent + extra_percent_height) * levelHeigth)
        # widthPercent and heightPercent are used to make sure that the room does not overlap the edges of the level

        if widthPercent <= 0 or heightPercent <= 0:
            raise IndexError('the value of widthPercent is {} and the value \
of heightPercent is {}. It is recomented that you increase the value of \
roomSizePercent, which is currently at {}.'.format(widthPercent, heightPercent, roomSizePercent))

        widthCenter = randrange(widthPercent, levelWidth - widthPercent)
        heightCenter = randrange(heightPercent, levelHeigth - heightPercent)

        widthCenter = clamp(widthCenter, 0, levelWidth)
        heightCenter = clamp(heightCenter, 0, levelHeigth)

        leftEdge = max(widthCenter - widthPercent, 1)
        rightEdge = min(widthCenter + widthPercent, levelWidth - 1)

        topEdge = max(heightCenter - heightPercent, 1)

        bottomEdge = min(heightCenter + heightPercent, levelHeigth - 1)

        if prevous_room is not None:

            temp_room = Rectangle(leftEdge, rightEdge, topEdge, bottomEdge)
            prevous_room.clamp_distance(temp_room, 45)
            leftEdge = temp_room.leftEdge
            rightEdge = temp_room.rightEdge
            topEdge = temp_room.topEdge
            bottomEdge = temp_room.bottomEdge
            del temp_room

        return leftEdge, rightEdge, topEdge, bottomEdge

    @classmethod
    def generate(cls, levelWidth, levelHeigth, roomSizePercent, extraPercent=0.0, prevous_room=None):
        leftEdge, rightEdge, topEdge, bottomEdge = Room.__calculateSize(levelWidth, levelHeigth, roomSizePercent, extraPercent=0.0, prevous_room=prevous_room)

        return cls(leftEdge, rightEdge, topEdge, bottomEdge)

    def regerateRoom(self, levelWidth, levelHeigth, roomSizePercent, extraPercent=0.0):
        self.leftEdge, self.rightEdge, self.topEdge, self.bottomEdge = self.__calculateSize(levelWidth, levelHeigth, roomSizePercent, extraPercent=0.0)

        self._spawnSpots = []

        for y in self.topToBottomRange:
            for x in self.leftToRightRange:
                #self._checkerSet.add(tuple([x, y]))
                self._spawnSpots.append(tuple([x, y]))

        self._pillarSpots = []
        self.placePillars()

    def placePillars(self):
        def leftToRightPillars(h, v):

            for p in range(self.leftEdge + 1, v - 1, 2):
                yield tuple([p, self.topEdge + 1])
                yield tuple([p, self.bottomEdge - 2])
            for p in range(self.rightEdge - 2, v, -2):
                yield tuple([p, self.topEdge + 1])
                yield tuple([p, self.bottomEdge - 2])
        def topToBottomPillars(h, v):
            for p in range(self.topEdge + 1, h - 1, 2):
                yield tuple([self.leftEdge + 1, p])
                yield tuple([self.rightEdge - 2, p])
            for p in range(self.bottomEdge - 2, h, -2):
                yield tuple([self.leftEdge + 1, p])
                yield tuple([self.rightEdge - 2, p])

        v, h = self.verticalLenght, self.horizontalLength
        vertPercent = v / (v + h)
        horizPercent = h / (v + h)

        if randFloat() < vertPercent * 0.75:

            halfPoint = self.topEdge + round(v / 2)
            self._pillarSpots += list(topToBottomPillars(halfPoint, halfPoint))

        if randFloat() < horizPercent * 0.75:

            halfPoint = self.leftEdge + round(h / 2)
            self._pillarSpots += list(leftToRightPillars(halfPoint, halfPoint))

        if len(self._pillarSpots) > 0:
            for p in self._pillarSpots:
                try:
                    self._spawnSpots.remove(p)
                except ValueError:
                    pass

    def checkPointOverlap(self, x, y):
        return x in range(self.leftEdge, self.rightEdge) and y in range(self.topEdge, self.bottomEdge)

    @property
    def randomPointWithinRoom(self):
        return choice(self._spawnSpots)
        # return (randrange(self.leftEdge, self.rightEdge), randrange(self.topEdge, self.bottomEdge))

    def randomSafePointWithinRoom(self, entityOrItemList):
        l = self._spawnSpots[:]

        for eOrI in entityOrItemList:
            if eOrI is None:
                print('Type of entity or items is {}'.format(type(eOrI)))
            if eOrI.co is None:
                print('Type of coord of entity or items is {}'.format(type(eOrI)))

            t = tuple([eOrI.co.x, eOrI.co.y])
            if t in l:
                l.remove(t)

        return choice(l)

    @property
    def leftToRightRange(self):
        return range(self.leftEdge, self.rightEdge)

    @property
    def topToBottomRange(self):
        return range(self.topEdge, self.bottomEdge)

    @property
    def verticalLenght(self):
        return self.bottomEdge - self.topEdge

    @property
    def horizontalLength(self):
        return self.rightEdge - self.leftEdge

    @property
    def randomSpawnSpot(self):
        return choice(self._spawnSpots)

class Hallway:
    def __init__(self, x, y, length, isVertical):
        self.x = x
        self.y = y
        self.length = length
        self.isVertical = isVertical

    @property
    def generateList(self):
        pointList = []
        if self.isVertical:
            for v in range(self.y, self.y + self.length + 1):
                pointList.append(tuple([self.x, v]))
        else:
            for h in range(self.x, self.x + self.length + 1):
                pointList.append(tuple([h, self.y]))
        return pointList

    @property
    def getDestinationPoint(self):
        if self.isVertical:
            return self.x, self.y + self.length
        else:
            return self.x + self.length, self.y

    def regerateHallway(self, x, y, length, isVertical):
        self.x = x
        self.y = y
        self.length = length
        self.isVertical = isVertical

    def trim(self, room):
        if self.isVertical:
            newY = room.bottomEdge
            subY = self.y - newY
            if room.checkPointOverlap(self.x, self.y):
                self.length -= subY
                self.y = newY
            elif room.checkPointOverlap(self.x, self.y + self.length):
                self.length -= subY
        else:
            newX = room.leftEdge
            subX = self.x - newX
            if room.checkPointOverlap(self.x, self.y):
                self.length -= newX
                self.x = newX
            elif room.checkPointOverlap(self.x + self.length, self.y):
                self.length -= subX

