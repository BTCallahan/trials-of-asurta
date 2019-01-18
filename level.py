from terrain import ALL_TILE_DICT, Terrain, Rectangle, Room, Hallway, BLOCKS_NOTHING, BLOCKS_MOVEMENT, BLOCKS_SIGHT, BLOCKS_FIRE
from random import randint, choice
from random import random as randFloat
from data_globals import ITEM_RATIO_DICT, ALL_ITEM_TYPES, ALL_IMPORTANT_ITEM_TYPES
from coords import Coords
from species import getFilteredSpecies
from entites import NPC
from color_factory import ALL_COLORS_DICT
from math import radians, atan2
from sys import getsizeof
from game_items import getListOfItemsSuitbleForDepth, UniversalGameItem, getSuitbleItemsByType
from line_of_sight import find_end_point_alt

class Level:

    LEVEL_SIZES = [100 + d * 20 for d in range(0, 100)]

    def genLevel(self, screenWidth, screenHeight):

        def genX():
            for x in range(screenWidth):
                if x is 0 or x is screenWidth - 1:
                    yield ALL_TILE_DICT['TERRAIN_BORDER']
                else:
                    yield ALL_TILE_DICT['TERRAIN_WALL']

        def genAllBorder():
            for x in range(screenWidth):
                yield ALL_TILE_DICT['TERRAIN_BORDER']

        def genY():
            for y in range(screenHeight):
                if y is 0 or y is screenHeight - 1:
                    yield list(genAllBorder())
                else:
                    yield list(genX())

        return list(genY())

    def getLevelSize(self, d):
        if d >= len(self.LEVEL_SIZES):
            return self.LEVEL_SIZES[-1]
        return self.LEVEL_SIZES[d]

    def genVisibilityGrid(self, width, height):

        def genVisibilitySlice():
            for s in range(width):
                yield False

        for s in range(height):
            yield(list(genVisibilitySlice()))


    def regerateLevel(self, depth):
        ls = self.getLevelSize(depth)
        w = ls + randint(-depth - 1, depth + 1) * 1
        h = ls + randint(-depth - 1, depth + 1) * 1
        self.size = ls

        self.grid = self.genLevel(depth, depth)
        self.widthHeight = Coords(w, h)
        self.depth = depth

        self.visibilityGrid = list(self.genVisibilityGrid(ls))

        self.rooms, self.junctions = self.generateDungeonRooms(w, h, 0.06, 0.025)

        self.assignTerrain(w, h)
        self.stairs = self.placeStairs()
        self.itemsOnFloor = []

        self.avalibleSpecies = getFilteredSpecies(depth)

        self.itemsAvalibleForDepth = getListOfItemsSuitbleForDepth(depth)
        self.itemsByTypeAvalibleForDepth = {k: getSuitbleItemsByType(self.itemsAvalibleForDepth, k) for k in
                                            ALL_IMPORTANT_ITEM_TYPES}

        self.player = None

    def __init__(self, depth=0, valueOfItemsToSpawn=50):
        ls = self.getLevelSize(depth)
        w = ls + randint(-depth - 1, depth + 1) * 5
        h = ls + randint(-depth - 1, depth + 1) * 5
        self.size = ls
        self.grid = self.genLevel(w, h)
        self.widthHeight = Coords(w, h)
        self.depth = depth

        self.visibilityGrid = list(self.genVisibilityGrid(w, h))

        self.rooms, self.junctions = self.generateDungeonRooms(w, h, 0.06, 0.025)

        self.assignTerrain(w, h)
        self.stairs = self.placeStairs()
        self.itemsOnFloor = []

        self.avalibleSpecies = getFilteredSpecies(depth)

        self.itemsAvalibleForDepth = getListOfItemsSuitbleForDepth(depth)
        self.itemsByTypeAvalibleForDepth = {k: getSuitbleItemsByType(self.itemsAvalibleForDepth, k) for k in
                                            ALL_IMPORTANT_ITEM_TYPES}
        self.player = None

        self.allEntities = []
        self.spawnInhabitants(depth)

        self.open_spaces = set()

        for r in self.rooms:
            for y in r.topToBottomRange:
                for x in r.leftToRightRange:
                    self.open_spaces.add(tuple([x, y]))

        for h in self.junctions:
            hw = h.generateList

            self.open_spaces = self.open_spaces | set(hw)

        self.number_of_open_spaces = len(self.open_spaces)



    @property
    def get_rectangle(self):
        return Rectangle(0, self.widthHeight.x, 0, self.widthHeight.y)


    def assignPlayer(self, player):
        self.player = player
        self.allEntities.append(player)
        self.spawnFloorItems(self.depth, 50)

    def getRandomItemOfType(self, itemType):

        l = self.itemsByTypeAvalibleForDepth[itemType]

        #l = list((i for i in self.itemsByTypeAvalibleForDepth.values() if i.typeOfItem == itemType))
        return choice(l)

    """
    def __del__(self):
        self.grid = []
        self.visibilityGrid = []
        self.itemsOnFloor = []
        self.rooms, self.junctions = [], []
        self.stairs = []
        #self.allEntities.remove(self.player)
        self.allEntities = []
    """

    def generateDungeonRooms(self, levelWidth, levelHeigth, roomSizePercent=1.5, extraPercent=1.0):
        #levelSpace = levelWidth * levelHeigth

        roomList = []
        junctionList = []
        junctionPointList = []

        for r in range(round(1.0 / roomSizePercent) + 1):

            if len(roomList) == 0:

                newRoom = Room.generate(levelWidth, levelHeigth, roomSizePercent, extraPercent)
            else:
                newRoom = Room.generate(levelWidth, levelHeigth, roomSizePercent, extraPercent)

            if not newRoom.checkOverlap(roomList):

                roomList.append(newRoom)

                x, y = roomList[-1].randomPointWithinRoom

                junctionPointList.append(tuple([x, y]))
                if len(roomList) > 1:

                    prevJunct = junctionPointList[-2]
                    currentJunct = junctionPointList[-1]

                    # prevX, prevY = prevJunct.getDestinationPoint

                    if randint(0, 2) is 1:
                        joinJunct = (prevJunct[0], currentJunct[1])
                        junctionPointList.insert(-1, joinJunct)
                    else:
                        joinJunct = (currentJunct[0], prevJunct[1])
                        junctionPointList.insert(-1, joinJunct)

        prevJ = None
        for j in junctionPointList:
            if prevJ is None:
                prevJ = j
            else:
                jX, jY, prevJX, prevJY = j[0], j[1], prevJ[0], prevJ[1]

                isVert = j[0] == prevJ[0]
                dif = 0
                ax = 0
                ay = 0
                if isVert:#if is vertical
                    ax = jX
                    if jY > prevJY:
                        ay = prevJY
                        dif = jY - prevJY
                    else:
                        ay = jY
                        dif = prevJY - jY
                else:
                    ay = prevJY
                    if jX > prevJX:
                        ax = prevJX
                        dif = jX - prevJX
                    else:
                        ax = jX
                        dif = prevJX - jX

                junctionList.append(Hallway(ax, ay, dif, isVert))
                prevJ = j

        return roomList, junctionList

    def assignTerrain(self, levelWidth, levelHeigth):

        #rooms, junctions = generateDungeonRooms(levelWidth, levelHeigth, roomSizePercent)

        for dRoom in self.rooms:

            for y in dRoom.topToBottomRange:
                for x in dRoom.leftToRightRange:

                    try:
                        self.grid[y][x] = ALL_TILE_DICT['TERRAIN_OPEN']
                    except IndexError:
                        print('{} {}, width: {}, height: {}'.format(x, y, levelWidth, levelHeigth))

        for dJunct in self.junctions:
            for dj in dJunct.generateList:
                try:
                    self.grid[dj[1]][dj[0]] = ALL_TILE_DICT['TERRAIN_OPEN']
                except IndexError:
                    pass

        for dRoom in self.rooms:
            for p in dRoom._pillarSpots:
                try:
                    self.grid[p[1]][p[0]] = ALL_TILE_DICT['TERRAIN_PILLAR']
                except IndexError:
                    pass

    def placeStairs(self):
        stairs = []
        startRoom = self.rooms[0]
        endRoom = self.rooms[-1]

        x, y = startRoom.randomPointWithinRoom

        stairs.append(Coords(x, y))

        self.grid[y][x] = choice([ALL_TILE_DICT['TERRAIN_DOWN_STAIR'], ALL_TILE_DICT['TERRAIN_STAIR']])

        x, y = endRoom.randomPointWithinRoom

        stairs.append(Coords(x, y))

        self.grid[y][x] = choice([ALL_TILE_DICT['TERRAIN_UP_STAIR'], ALL_TILE_DICT['TERRAIN_STAIR']])

        for r in self.rooms[1:-1]:
            if randFloat() < 1.0 / 3.0:
                x, y = r.randomPointWithinRoom
                self.grid[y][x] = choice([ALL_TILE_DICT['TERRAIN_STAIR'], ALL_TILE_DICT['TERRAIN_UP_STAIR'], ALL_TILE_DICT['TERRAIN_DOWN_STAIR']])
                stairs.append(Coords(x, y))

        for r in self.rooms:
            if randFloat() < 0.2:
                x, y = r.randomPointWithinRoom
                if self.grid[y][x] not in {ALL_TILE_DICT['TERRAIN_STAIR'], ALL_TILE_DICT['TERRAIN_UP_STAIR'], ALL_TILE_DICT['TERRAIN_DOWN_STAIR']}:
                    self.grid[y][x] = choice([ALL_TILE_DICT['TERRAIN_STAIR'], ALL_TILE_DICT['TERRAIN_UP_STAIR'], ALL_TILE_DICT['TERRAIN_DOWN_STAIR']])
                    stairs.append(Coords(x, y))
        return stairs

    def getRandomStairDown(self):
        return choice(list((s for s in self.stairs if self.grid[s.y][s.x].isDownstairs)))

    def getRandomStairUp(self):
        return choice(list((s for s in self.stairs if self.grid[s.y][s.x].isUpstairs)))

    def spawnFloorItems(self, depth, value):
        placeholder = len(ALL_ITEM_TYPES) - 2
        # we don't want to place corpses just yet, so we'll iterate through all none corpse items

        print(ALL_ITEM_TYPES)
        print(ITEM_RATIO_DICT.keys())
        print(ITEM_RATIO_DICT.values())

        totalValueOfPlayersItems, valueOfPlayersItemsByClass = self.player.checkitemValueByCategory()
        # totalValueOfPlayersItems is the total value off all item that the player is carrying
        # valueOfPlayersItemsByClass is a counter that stores the total value of all items of a specif type that the
        # players is carrying. for example, if the player is carry several 'MISC' items with a combined value of 65,
        # the entry for valueOfPlayersItemsByClass['MISC'] would be 65

        safeDivide = lambda d1, d2: 0 if d2 == 0 else d1 / d2

        itemPercentage = {k: 1.0 - safeDivide(v, totalValueOfPlayersItems) for (k, v) in valueOfPlayersItemsByClass.items()}
        # a dictionary containing one minus the percentage values for each type of item. For example, if if the total
        # value of everything the player was carrying was equal to 131, and the value of all 'SHIELD' items was 38,
        # then the entry for itemPercentage['SHIELD'] would be 1 - (38 / 131), or
        # itemPercentage['SHIELD'] = 0.70992366412
        # These number are use to multiply

        thresholdValue = ITEM_RATIO_DICT[ALL_ITEM_TYPES[placeholder]]
        currentValue = value
        # if the currentValue is less then the thresholdValue, reduce the placeholder by 1

        while placeholder > 0:
            currentItemType = ALL_ITEM_TYPES[placeholder]

            x, y = self.getRandomSpawnPoint

            c = self.getRandomItemOfType(currentItemType)

            a = UniversalGameItem.spawnItem(c, x, y, depth)
            currentValue -= a.getValue

            self.itemsOnFloor.append(a)

            valueAjuster = itemPercentage[currentItemType]

            if valueAjuster * (currentValue / value) < thresholdValue:
                placeholder -= 1
                thresholdValue = ITEM_RATIO_DICT[currentItemType]

        for cs in range(round(value * 0.05)):
            # now we can spawn corspes

            sp = choice(self.avalibleSpecies)

            x, y = self.getRandomSpawnPoint

            self.itemsOnFloor.append(UniversalGameItem.spawnItem(sp.corpseItem, x, y, depth))

    def selectRandomItem(self, itemType, slot=None):
        retList = []

        if slot == None:
            retList = list((i for i in self.itemsAvalibleForDepth if i.typeOfItem == itemType))
        else:
            retList = list((i for i in self.itemsAvalibleForDepth if i.typeOfItem == itemType and slot in i.bodySlotTypesAllowed))

        if len(retList) == 0:
            return None

        return choice(retList)

    def spawnInhabitants(self, depth):

        r = randint(0, 1 + depth // 10)

        for t in range(round(self.size * 0.15) + r):
            x, y = self.getRandomSafeSpawnPoint
            e = NPC.randomSpawnNPC(x, y, self.itemsAvalibleForDepth, self.itemsByTypeAvalibleForDepth,
                                   self.avalibleSpecies, depth)
            self.allEntities.append(e)

    def spawn_single_inhabitant(self, coords=None):

        r = randint(0, 1 + self.depth // 10)

        if len(self.allEntities) < round(self.size * 0.05) + r:

            if coords is None:

                if len(self.stairs) < 1:
                    return None

                entity_coords = set((e.co for e in self.allEntities if e.is_a_valid_target))

                list_of_stairs = [s for s in self.stairs if s not in entity_coords]

                stairwell = choice(list_of_stairs)

                x, y = stairwell.x, stairwell.y

            else:
                x = coords.x
                y = coords.y

            e = NPC.randomSpawnNPC(x, y, self.itemsAvalibleForDepth, self.itemsByTypeAvalibleForDepth,
                                       self.avalibleSpecies, self.depth)

            self.allEntities.append(e)

    def getTileChar(self, x, y):
        try:
            checkTile = self.visibilityGrid[y][x]
        except IndexError:
            print('Error: x: {}, and y: {} are out of bounds. Grid width is {} and grid height is {}.'.format(x, y, self.widthHeight.x, self.widthHeight.y))
            checkTile = False

        if checkTile:
            tile = self.grid[y][x]
            # returns a ? as the tile char, so the problem is in the self.visibilityGrid
            return tile.symbol, tile.fgColor, tile.bgColor
        else:
            return ' ', ALL_COLORS_DICT['WHITE'], ALL_COLORS_DICT['BLACK']

    def checkIfItemOrEntityIsInVisibilityGrid(self, itemOrEntity):
        return self.visibilityGrid[itemOrEntity.co.y][itemOrEntity.co.x]

    def getLocationsWithinRadius(self, radius, condition, locationX, locationY=None):

        if isinstance(locationX, Coords):
            location: Coords = locationX
        else:
            location: Coords = Coords(locationX, locationY)

        locList = []

        for y in range(max(0, location.y - radius), min(self.widthHeight.y, location.y + radius)):
            for x in range(max(0, location.x - radius), min(self.widthHeight.x, location.x + radius)):
                if location.distance(x, y) <= radius:
                    if condition(x, y):
                        locList.append(tuple([x, y]))
        return locList

    def checkForObstructionBetweenPoints(self, originPoint, destinationPoint, checkForEntitiesBetweenPoints=False,
                                         maxRange=100000) -> bool:#moveThru

        end_point = find_end_point_alt(self, originPoint, destinationPoint, BLOCKS_MOVEMENT, maxRange)

        d1 = destinationPoint - originPoint

        d2 = d1.normalize(new_tuple=False)

        d3 = (d2 * (maxRange + 1)).round

        n: Coords = d3 + originPoint

        return end_point != n

    def getEntitiesBetweenPoints(self, c1: Coords, c2: Coords, maxEntities=1000, maxRange=100000):

        diffrence = c2 - c1

        entity_list = [e for e in self.allEntities if e.co.distance(c1) <= maxRange and e.is_a_valid_target]

        distance_between_points = c1.distance(c2)

        c_atan = atan2(diffrence.y, diffrence.x)

        entities = []

        for e in entity_list:

            dist = c1.distance(e.co)
            # the distacne between the entity and c1

            d: Coords = c1 + (diffrence * (dist / distance_between_points)).round

            if d == e.co:
                entities.append(e)

            """

            local_e_co = e.co - c1

            local_atan = atan2(local_e_co.y, local_e_co.x)

            if c_atan == local_atan:
                entities.append(e)
            """

        return sorted(entities, key= lambda e: e.co.distance(c1), reverse=True)

    def getEndPoint(self, caster, targetCo, maxRange=100000):

        return find_end_point_alt(self, caster.co, targetCo, BLOCKS_MOVEMENT, maxRange)

    """
    __check_if_number_is_negative = (lambda x: -1 if x < 0 else 1)

    def getEntitiesInLineOfFire(self, caster, targetCo, maxRange=100000):

        caster_co = caster.co

        end_point = find_end_point_alt(caster_co, targetCo, BLOCKS_FIRE, maxRange)

        maxRange = min(maxRange, caster_co.distance(end_point))

        diffrence = targetCo - caster_co

        if abs(diffrence.x) > abs(diffrence.y):

            x_range = range(caster_co.x, targetCo.x, self.__check_if_number_is_negative(diffrence.x))

            y_factor = abs(diffrence.y / diffrence.x) * self.__check_if_number_is_negative(diffrence.y)

            y_list = [caster_co.y + round(y * y_factor) for y in range(abs(diffrence.y))]

            return x_range, y_list

        elif abs(diffrence.y) > abs(diffrence.x):

            y_range = range(caster_co.y, targetCo.y, self.__check_if_number_is_negative(diffrence.y))

            x_factor = abs(diffrence.x / diffrence.y) * self.__check_if_number_is_negative(diffrence.x)

            x_list = [caster_co.x + round(x + x_factor) for x in range(abs(diffrence.x))]

            return x_list, y_range
        else:
            return range(caster_co.x, targetCo.x, self.__check_if_number_is_negative(diffrence.x)), range(caster_co.y, targetCo.y, self.__check_if_number_is_negative(diffrence))




        distance_between_points = caster_co.distance(targetCo)

        entity_list = [e for e in self.allEntities if e.co.distance(caster_co) <= maxRange and e is not caster and e.is_a_valid_target]

        c_atan = atan2(diffrence.y, diffrence.x)

        entities = []



        return sorted(entities, key=lambda e: e.co.distance(caster), reverse=True)
    """

    def getEntitesInRange(self, caster, maxRange=100000, allEntieiesExceptThis=None):
        if allEntieiesExceptThis is None:
            return list((e for e in self.allEntities if e.co.distance(caster.co) <= maxRange))
        else:
            return list((e for e in self.allEntities if e is not allEntieiesExceptThis and
                         e.co.distance(caster.co) <= maxRange))

    def getEntitiesInCone(self, caster, targetCo, degrees, maxRange=100000):
        r = radians(degrees)
        offset = (targetCo - caster.co).normalize
        angleToTarget = atan2(offset.x, offset.y)

        otherWithin = list((e for e in self.allEntities if
                            abs(atan2((e.co - caster.co).x, (e.co - caster.co).y)) <= r + angleToTarget))

        return sorted(otherWithin, key=lambda d: d.co.distance(caster.co))

    @property
    def getRandomSpawnPoint(self):
        return choice(self.rooms).randomPointWithinRoom

    @property
    def getRandomSafeSpawnPoint(self):
        if len(self.allEntities) < 1:
            return choice(self.rooms).randomPointWithinRoom
        return choice(self.rooms).randomSafePointWithinRoom(self.allEntities)

    def setTerrain(self, x, y, tile):
        try:
            self.grid[y][x] = tile
        except IndexError:
            pass

    def checkIfAnyItemsBelowEntity(self, entity):
        for i in self.itemsOnFloor:
            if i.co == entity.co:
                return i
        return None

    def getAllItemsBelowEntity(self, entity):
        return list((i for i in self.itemsOnFloor if i.co == entity.co))

    def pickUp(self, entity):
        for i in self.itemsOnFloor:
            if i.co == entity.co:
                entity.pickUp(self, i)
                break

    def removeDeadEntities(self):
        self.allEntities = list((e for e in self.allEntities if e.is_a_valid_target))

    @property
    def debugMemoryUsage(self):

        itemMemory = sum(list(map(lambda x: getsizeof(x), self.itemsOnFloor)))
        entityMemory = sum(list(map(lambda x: getsizeof(x) + x.getEquipmentMemory, self.allEntities)))
        levelMemory = getsizeof(self)
        total = itemMemory + entityMemory + levelMemory
        return itemMemory, entityMemory, levelMemory, total

def prep_level_for_unit_testing(level):

    level.stairs = []

    level.itemsOnFloor = []

    for y in range(1, level.widthHeight.y - 1):
        for x in range(1, level.widthHeight.x - 1):
            level.grid[y][x] = ALL_TILE_DICT['TERRAIN_OPEN']




