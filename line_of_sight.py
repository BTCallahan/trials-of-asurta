from terrain import BLOCKS_NOTHING, BLOCKS_FIRE, Terrain
from coords import Coords
from entites import Player

# los/raycasting

def old_betterLOS(gl, playerEntity, pointToLookAt):
    """gl = a Level object
    playerEntity = a Player object
    pointToLookAt = a Coords"""

    def setVisibile(cx, cy):
        # try:
        gl.visibilityGrid[cy][cx] = True
        # except IndexError:
        #    return True

    # localXY
    # pointToLookAt is a variable
    player_posX, player_posY = playerEntity.co.x, playerEntity.co.y
    # assume that:
    # pointToLookAt.x = 27 and pointToLookAt.y = 33
    # the player has a position of X: 15, Y: 61

    localXY = pointToLookAt - playerEntity.co
    # therefore:
    # localXY.x = 27 - 15 = 12
    # localXY.y = 33 - 61 = -28

    sightBlocked = False

    if localXY.x == 0:

        if localXY.y < 0:
            # if localXY is below the player

            y_increment = 1
        else:
            y_increment = -1

        y_range = range(player_posY, player_posY + (playerEntity.getSightRadius + 1) * y_increment, y_increment)

        for y in y_range:
            try:
                gridSelection = gl.grid[y][player_posX]
                # gridSelection = gl.grid[7][3]
            except IndexError:
                print('Index Error, ending range loop')
                break

            if sightBlocked:
                break
            elif not gridSelection.seeThru:
                setVisibile(player_posX, y)
                sightBlocked = True
            else:
                setVisibile(player_posX, y)

    elif localXY.y == 0:

        if localXY.x < 0:

            x_increment = 1
        else:
            x_increment = -1

        x_range = range(player_posX, player_posX + (playerEntity.getSightRadius + 1) * x_increment, x_increment)

        for x in x_range:
            try:
                gridSelection = gl.grid[player_posY][x]
                # gridSelection = gl.grid[7][3]
            except IndexError:
                print('Index Error, ending range loop')
                break

            if sightBlocked:
                break
            elif not gridSelection.seeThru:
                setVisibile(x, player_posY)
                sightBlocked = True
            else:
                setVisibile(x, player_posY)

    else:
        normalizedX, normalizedY = localXY.normalize()
        # 12 ^ 2 = 144
        # -28 ^ 2 = 64 + 160 + 160 + 400 = 784
        # normalizedX = 0.393919298579
        # normalizedY = 0.919145030018

        for l in range(playerEntity.getSightRadius + 1):
            # run until l exceeds or is equal to the player's sight radius

            iX, iY = normalizedX * l, normalizedY * l
            # assume l is 8
            # iX = 0.393919298579 * 8 = 3.15135438863
            # iY = 0.919145030018 * 8 = 7.35316024014

            combinedX, combinedY = round(player_posX + iX), round(player_posY + iY)
            # combinedX = 3, combinedY = 7
            #combinedX += posX
            #combinedY += posY

            try:
                gridSelection = gl.grid[combinedY][combinedX]
                # gridSelection = gl.grid[7][3]
            except IndexError:
                print('Index Error, ending range loop')
                break

            if sightBlocked:
                # if sightBlocked is true, break loop
                break
            elif not gridSelection.seeThru:
                # if the tile cannot be seen through
                # else set grid visability to true and set sightBlocked to true

                setVisibile(combinedX, combinedY)
                # gl.visibilityGrid[combinedY][combinedX] = True
                # setVisibile(combinedY,combinedX)
                sightBlocked = True

            else:
                # set grid visability to true

                setVisibile(combinedX, combinedY)
                gv = gl.visibilityGrid[combinedY][combinedX]

def betterLOS(gl, playerEntity: Player, pointToLookAt):
    """gl = a Level object
    playerEntity = a Player object
    pointToLookAt = a Coords"""

    def setVisibile(cx, cy):
        # try:
        gl.visibilityGrid[cy][cx] = True
        # except IndexError:
        #    return True

    # localXY
    # pointToLookAt is a variable
    player_posX, player_posY = playerEntity.co.x, playerEntity.co.y
    # assume that:
    # pointToLookAt.x = 27 and pointToLookAt.y = 33
    # the player has a position of X: 15, Y: 61

    localXY = pointToLookAt - playerEntity.co
    # therefore:
    # localXY.x = 27 - 15 = 12
    # localXY.y = 33 - 61 = -28

    sightBlocked = False

    if localXY.x == 0:

        if localXY.y < 0:
            # if localXY is below the player

            y_increment = 1
        else:
            y_increment = -1

        y_range = range(player_posY, player_posY + (playerEntity.getSightRadius + 1) * y_increment, y_increment)

        for y in y_range:
            try:
                gridSelection = gl.grid[y][player_posX]
                # gridSelection = gl.grid[7][3]
            except IndexError:
                print('Index Error, ending range loop')
                break

            if sightBlocked:
                break
            elif not gridSelection.seeThru:
                setVisibile(player_posX, y)
                sightBlocked = True
            else:
                setVisibile(player_posX, y)

    elif localXY.y == 0:

        if localXY.x < 0:

            x_increment = 1
        else:
            x_increment = -1

        x_range = range(player_posX, player_posX + (playerEntity.getSightRadius + 1) * x_increment, x_increment)

        for x in x_range:
            try:
                gridSelection = gl.grid[player_posY][x]
                # gridSelection = gl.grid[7][3]
            except IndexError:
                print('Index Error, ending range loop')
                break

            if sightBlocked:
                break
            elif not gridSelection.seeThru:
                setVisibile(x, player_posY)
                sightBlocked = True
            else:
                setVisibile(x, player_posY)

    else:
        normalizedX, normalizedY = localXY.normalize()
        # 12 ^ 2 = 144
        # -28 ^ 2 = 64 + 160 + 160 + 400 = 784
        # normalizedX = 0.393919298579
        # normalizedY = 0.919145030018

        range_range = range(playerEntity.getSightRadius + 1)

        if abs(localXY.x) > abs(localXY.y):

            x_range = range(player_posX, pointToLookAt.x, __check_if_number_is_negative(localXY.x))

            y_factor = abs(localXY.y / localXY.x) * __check_if_number_is_negative(localXY.y)

            y_range = [player_posY + round(y * y_factor) for y in range(abs(localXY.x))]

            for _x, _y, z in zip(x_range, y_range, range_range):
                gridSelection = gl.grid[_y][_x]

                if sightBlocked:
                    break
                elif not gridSelection.seeThru:
                    setVisibile(_x, _y)
                    sightBlocked = True
                else:
                    setVisibile(_x, _y)

        elif abs(localXY.x) < abs(localXY.y):
            # problem area

            # assume that:
            # player_posX = 26

            y_range = range(player_posY, pointToLookAt.y, __check_if_number_is_negative(localXY.y))

            x_factor = abs(localXY.x / localXY.y) * __check_if_number_is_negative(localXY.x)

            x_range = [player_posX + round(x * x_factor) for x in range(abs(localXY.y))]

            for _x, _y, z in zip(x_range, y_range, range_range):
                gridSelection = gl.grid[_y][_x]

                if sightBlocked:
                    break
                elif not gridSelection.seeThru:
                    setVisibile(_x, _y)
                    sightBlocked = True
                else:
                    setVisibile(_x, _y)

        else:
            x_range = range(player_posX, pointToLookAt.x, __check_if_number_is_negative(localXY.x))

            y_range = range(player_posY, pointToLookAt.y, __check_if_number_is_negative(localXY.y))

            for _x, _y, z in zip(x_range, y_range, range_range):
                gridSelection = gl.grid[_y][_x]

                if sightBlocked:
                    break
                elif not gridSelection.seeThru:
                    setVisibile(_x, _y)
                    sightBlocked = True
                else:
                    setVisibile(_x, _y)


def lookLOS(vDict):
    """A very simple and somewhat inefficiant LOS function. for defermining if a grid tile can be marked as 'seen'.
     May have bugs."""

    gameLevel = vDict['gameLevel']

    top = max(gameLevel.player.co.y - gameLevel.player.getSightRadius, 0)
    bottom = min(gameLevel.player.co.y + gameLevel.player.getSightRadius, gameLevel.widthHeight.y)
    left = max(gameLevel.player.co.x - gameLevel.player.getSightRadius, 0)
    right = min(gameLevel.player.co.x + gameLevel.player.getSightRadius, gameLevel.widthHeight.x)

    for x in range(left + 1, right - 1):
        betterLOS(gameLevel, gameLevel.player, Coords(x, top))
        betterLOS(gameLevel, gameLevel.player, Coords(x, bottom))

    for y in range(top + 1, bottom - 1):
        betterLOS(gameLevel, gameLevel.player, Coords(left, y))
        betterLOS(gameLevel, gameLevel.player, Coords(right, y))


def scanQuarter(vDict, extent, isTopOrBottom):
    gameLevel = vDict['gameLevel']

    playerPos = gameLevel.player.co

    def getGridTileTopBottom(line, subLine, visiblityGrid):
        if visiblityGrid:
            return gameLevel.visiblityGrid[line][subLine]
        return gameLevel.grid[line][subLine]

    def getGridTileLeftRight(line, subLine, visiblityGrid):
        if visiblityGrid:
            return gameLevel.visiblityGrid[subLine][line]
        return gameLevel.grid[subLine][line]

    def setVisibilityTopBottom(line, subLine, value):
        gameLevel.visiblityGrid[line][subLine] = value

    def setVisibilityLeftRight(line, subLine, value):
        gameLevel.visiblityGrid[subLine][line] = value

    hitBlockWhileScanningPrevousLine = False

    if isTopOrBottom:

        getTile = getGridTileTopBottom

        setVisTile = setVisibilityTopBottom

        extentVs = playerPos.y
    else:

        getTile = getGridTileLeftRight

        setVisTile = setVisibilityLeftRight

        extentVs = playerPos.x

    if extent < extentVs:
        addToLine = -1
    else:
        addToLine = 1

def quaterLOS(vDict):
    gameLevel = vDict['gameLevel']

    playerPos = gameLevel.player.co

    top = max(gameLevel.player.co.y - gameLevel.player.getSightRadius, 0)
    bottom = min(gameLevel.player.co.y + gameLevel.player.getSightRadius, gameLevel.widthHeight.y)
    left = max(gameLevel.player.co.x - gameLevel.player.getSightRadius, 0)
    right = min(gameLevel.player.co.x + gameLevel.player.getSightRadius, gameLevel.widthHeight.x)

    hitBlockWhileScanningPrevousLine = False

    # scan top quarter
    t = 1
    for t in range(playerPos.y, top, -1):

        if not hitBlockWhileScanningPrevousLine:

            hitBlock = False

            for l_2_r in range(playerPos.x - t, playerPos.x + t):

                if not gameLevel.grid[t][l_2_r].seeThru:

                    hitBlock = True

                gameLevel.visibilityGrid[t][l_2_r] = True

            t += -1

            if hitBlock:
                hitBlockWhileScanningPrevousLine = True
        else:

            for l_2_r in range(-t, t):

                # this is a tuple, not a Coords object
                nX, nY = (Coords(l_2_r, t) - playerPos).normalize(round_to=True)

                if not gameLevel.grid[t][l_2_r].seeThru:
                    pass
                elif not gameLevel.visibilityGrid[t + nY][l_2_r + nX]:
                    pass
                else:
                    gameLevel.visibilityGrid[t][l_2_r] = True



"""
def find_end_point(self, caster_co: Coords, target_co: Coords, condition: int = BLOCKS_NOTHING, max_range=10000):
    local_direction = target_co - caster_co

    # normalizes the x and y values of the Coords object and returns a tuple
    nX, nY = local_direction.normalize()

    caster_x, caster_y = caster_co.x, caster_co.y

    rounded_caster_x, rounded_caster_y = round(caster_x), round(caster_y)

    if condition is BLOCKS_NOTHING:

        for r in range(max_range):
            # checks if the values rounded_caster_x and rounded_caster_y are in range of the level grid
            if 0 <= rounded_caster_x < self.widthHeight.x and 0 <= rounded_caster_y < self.widthHeight.y:

                rounded_caster_x = caster_co.x + round(nX * r)
                rounded_caster_y = caster_co.y + round(nY * r)

            else:
                return Coords(rounded_caster_x, rounded_caster_y)
    else:
        for r in range(max_range):
            if 0 <= rounded_caster_x < self.widthHeight.x and 0 <= rounded_caster_y < self.widthHeight.y:

                rounded_caster_x = caster_co.x + round(nX * r)
                rounded_caster_y = caster_co.y + round(nY * r)

                tile: Terrain = self.grid[rounded_caster_y][rounded_caster_x]

                if tile.blockTypes & condition == condition:
                    return Coords(rounded_caster_x, rounded_caster_y)
            else:
                return Coords(rounded_caster_x, rounded_caster_y)

    return target_co
"""

def find_end_point_alt(self, caster_co: Coords, target_co: Coords, condition: int=BLOCKS_NOTHING, max_range=10000):
    """Explanation: the arguments caster_co and target_co are both Coord objects. The Coord class is a subclass of
    namedtuple and contain two field: x and y, as well as several methods.

    The argument condition is an int with a defult value of 0.

    Each tile has a bitmask field that is used to check for the condition

    """

    if caster_co.x < target_co.x:
        # if the caster is to the left of the target

        x_range_inc = 1
        x_dir = 1
    elif caster_co.x > target_co.x:
        # else if the caster is to the right of the target

        x_range_inc = -1
        x_dir = -1
    else:
        x_range_inc = 0
        x_dir = 1

    # if the caster is below the target
    if caster_co.y < target_co.y:
        y_range_inc = 1
        y_dir = 1
    elif caster_co.y > target_co.y:
        y_range_inc = -1
        y_dir = -1
    else:
        y_range_inc = 0
        y_dir = 1

    range_x = range(caster_co.x, target_co.x, x_dir)

    range_y = range(caster_co.y, target_co.y, y_dir)

    if len(range_y) == 0:
        # if both points are on the same y location

        range_x = range(caster_co.x, target_co.x + x_dir, x_dir)

        _x = caster_co.x

        for x, r in zip(range_x, range(max_range + 1)):

            tile: Terrain = self.grid[caster_co.y][x]

            if tile.blockTypes & condition == condition:
                return Coords(_x, caster_co.y)

            if x == target_co.x:
                return target_co

            _x = x


        return Coords(_x, caster_co.y)

    elif len(range_x) == 0:
        # if both points are on the same x location

        range_y = range(caster_co.y, target_co.y + y_dir, y_dir)

        _y = caster_co.y

        for y, r in zip(range_y, range(max_range + 1)):


            tile: Terrain = self.grid[y][caster_co.x]

            if tile.blockTypes & condition == condition:
                return Coords(caster_co.x, _y)

            if y == target_co.y:
                return target_co

            _y = y


        return Coords(caster_co.x, _y)
    else:

        # subtract the caster_co from the target_co
        local_direction = target_co - caster_co

        # normalizes the x and y values of the Coords object and returns a tuple
        nX, nY = local_direction.normalize()

        rounded_caster_x, rounded_caster_y = caster_co.x, caster_co.y

        range_range = range(max_range + 1)

        for r in range_range:

            if rounded_caster_x == target_co.x and rounded_caster_y == target_co.y:
                return target_co

            else:
                rounded_caster_x = caster_co.x + round(nX * r)#!!!!!
                rounded_caster_y = caster_co.y + round(nY * r)

                tile: Terrain = self.grid[rounded_caster_y][rounded_caster_x]

                # each tile object has a bitmask atribute called blocktype. For example:
                # tile.blockTypes = 101
                # condition = 1
                # tile.blockTypes & condition = 1
                # so 1 == 1 is true
                if tile.blockTypes & condition == condition:
                    # returns a new Coords object
                    return Coords(caster_co.x + round(nX * (r - 1)), caster_co.y + round(nY * (r - 1)))

        return Coords(rounded_caster_x, rounded_caster_y)

__check_if_number_is_negative = (lambda x: -1 if x < 0 else 1)


def generate_entities_if_co_in_list(entities, x_list, y_list):
    for x, y in zip(x_list, y_list):
        for e in entities:
            if e.co.x == x and e.co.y == y:
                yield e
                break


def getEntitiesInLineOfFire(self, caster, targetCo, maxRange=100000):

    caster_co = caster.co

    end_point = find_end_point_alt(self, caster_co, targetCo, BLOCKS_FIRE, maxRange)

    maxRange = min(maxRange, caster_co.distance(end_point))

    diffrence = targetCo - caster_co

    if abs(diffrence.x) > abs(diffrence.y):

        x_range = range(caster_co.x, targetCo.x, __check_if_number_is_negative(diffrence.x))

        y_factor = abs(diffrence.y / diffrence.x) * __check_if_number_is_negative(diffrence.y)

        y_range = [caster_co.y + round(y * y_factor) for y in range(abs(diffrence.y))]


    elif abs(diffrence.y) > abs(diffrence.x):

        y_range = range(caster_co.y, targetCo.y, __check_if_number_is_negative(diffrence.y))

        x_factor = abs(diffrence.x / diffrence.y) * __check_if_number_is_negative(diffrence.x)

        x_range = [caster_co.x + round(x + x_factor) for x in range(abs(diffrence.x))]

    else:

        x_range = range(caster_co.x, targetCo.x, __check_if_number_is_negative(diffrence.x))

        y_range = range(caster_co.y, targetCo.y, __check_if_number_is_negative(diffrence.y))

    entity_list = [e for e in self.allEntities if e is not caster and e.is_a_valid_target]

    valid_entities = list(generate_entities_if_co_in_list(entity_list, x_range, y_range))

    distance_between_points = caster_co.distance(targetCo)

    entity_list = [e for e in self.allEntities if e.co.distance(caster_co) <= maxRange and e is not caster and e.is_a_valid_target]

    return sorted(entity_list, key=lambda e: e.co.distance(caster), reverse=True)


def get_entities_in_line_of_fire_hash(self, caster, targetCo, maxRange=100000):

    caster_co = caster.co

    end_point = find_end_point_alt(self, caster_co, targetCo, BLOCKS_FIRE, maxRange)

    maxRange = min(maxRange, caster_co.distance(end_point))

    okay_entities = [e for e in self.allEntities if e is not caster and e.is_a_valid_target and e.co.distance(caster_co) <= maxRange]

    if len(okay_entities) == 0:
        return []

    if caster_co == targetCo:

        return [e for e in okay_entities if e.co == caster_co]

    diffrence = targetCo - caster_co



    if diffrence.x == 0:

        min_y = min(caster_co.y, targetCo.y)

        max_y = max(caster_co.y, targetCo.y)

        hash_set = set(hash((caster_co.x, y)) for y in range(min_y, max_y))

        return [e for e in okay_entities if hash(e.co) in hash_set]
    elif diffrence.y == 0:

        min_x = min(caster_co.x, targetCo.x)

        max_x = max(caster_co.x, targetCo.x)

        hash_set = set(hash((x, caster_co.y)) for x in range(min_x, max_x))

        return [e for e in okay_entities if hash(e.co) in hash_set]
    else:

        if abs(diffrence.x) > abs(diffrence.y):

            x_range = range(caster_co.x, targetCo.x, __check_if_number_is_negative(diffrence.x))

            y_factor = abs(diffrence.y / diffrence.x) * __check_if_number_is_negative(diffrence.y)

            y_range = [caster_co.y + round(y * y_factor) for y in range(abs(diffrence.y))]

            hash_set = set(hash((x, y)) for x, y in zip(x_range, y_range))

            return [e for e in okay_entities if hash(e.co) in hash_set]

        elif abs(diffrence.y) > abs(diffrence.x):

            y_range = range(caster_co.y, targetCo.y, __check_if_number_is_negative(diffrence.y))

            x_factor = abs(diffrence.x / diffrence.y) * __check_if_number_is_negative(diffrence.x)

            x_range = [caster_co.x + round(x * x_factor) for x in range(abs(diffrence.x))]

            hash_set = set(hash((x, y)) for x, y in zip(x_range, y_range))

            return [e for e in okay_entities if hash(e.co) in hash_set]
        else:

            x_range = range(caster_co.x, targetCo.x, __check_if_number_is_negative(diffrence.x))

            y_range = range(caster_co.y, targetCo.y, __check_if_number_is_negative(diffrence.y))

            hash_set = set(hash((x, y)) for x, y, in zip(x_range, y_range))

            return [e for e in okay_entities if hash(e.co) in hash_set]