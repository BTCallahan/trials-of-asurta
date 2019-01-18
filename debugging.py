from collections import defaultdict
from gc import get_objects
import gc, cProfile, tracemalloc, timeit
from sys import getsizeof
from entites import Player, NPC
from terrain import BLOCKS_MOVEMENT
from game_items import ALL_ITEM_DICT, UniversalGameItem

def new_player_for_testing(co):
    from species import ALL_SPECIES, newSkillDict, newStatDict
    from random import choice
    from game_items import UniversalGameItem
    from coords import DIR_CENTER
    from collections import Counter

    sp = choice(ALL_SPECIES)

    return Player(sp, choice(sp.genders), co.x, co.y, [],
                  handItem=UniversalGameItem.new_dummy_object(),
                  offHandItem=UniversalGameItem.new_dummy_object(),
                  swapHandItem=UniversalGameItem.new_dummy_object(),
                  swapOffHandItem=UniversalGameItem.new_dummy_object(),
                  miscItems=[],
                  quiver=UniversalGameItem.new_dummy_object(),
                  wornDict={'HEAD': UniversalGameItem.new_dummy_object(),
                            'UPPER_BOD': UniversalGameItem.new_dummy_object(),
                            'HANDS': UniversalGameItem.new_dummy_object(),
                            'LOWER_BOD': UniversalGameItem.new_dummy_object(),
                            'FEET': UniversalGameItem.new_dummy_object()},
                  statDict=newStatDict(1, 1, 1, 1, 1, 1, 1, 1),
                  skillDict=newSkillDict(0, 0, 0, 0, 0,
                                         0, 0, 0, 0, 0,
                                         0, 0, 0),
                  moveTimeLeft=1.0,
                  health=100,
                  stamna=100,
                  magic=100,
                  food=100000,
                  moveDirection=DIR_CENTER,
                  grimore=[],
                  grimoreLearn=Counter()
                  )


def place_specific_item(level, item_name: str, x, y):

    item = ALL_ITEM_DICT[item_name]

    level.itemsOnFloor.append(UniversalGameItem.spawnItem(item, x, y, 0, identified=True))


def debug_level_memory_usage(level):
    itemMemory = sum(list(map(lambda x: getsizeof(x), level.itemsOnFloor)))
    entityMemory = sum(list(map(lambda x: getsizeof(x) + x.getEquipmentMemory, level.allEntities)))
    levelMemory = getsizeof(level)
    total = itemMemory + entityMemory + levelMemory
    return itemMemory, entityMemory, levelMemory, total


def unit_test():
    from terrain import BLOCKS_NOTHING, BLOCKS_FIRE, BLOCKS_MOVEMENT, BLOCKS_SIGHT

    custom_block = BLOCKS_NOTHING + BLOCKS_MOVEMENT + BLOCKS_FIRE

    bitwise_checker = BLOCKS_MOVEMENT

    print('checking for movement block')

    print('custom block: {:b}'.format(custom_block))
    print('bitwise checker: {:b}'.format(bitwise_checker))

    print('combination: {:b}'.format(custom_block & bitwise_checker))
    print('check result: {}'.format(custom_block & bitwise_checker == bitwise_checker))

    bitwise_checker = BLOCKS_SIGHT

    print('checking for sight block')

    print('custom block: {:b}'.format(custom_block))
    print('bitwise checker: {:b}'.format(bitwise_checker))

    print('combination: {:b}'.format(custom_block & bitwise_checker))
    print('check result: {}'.format(custom_block & bitwise_checker == bitwise_checker))

    bitwise_checker = BLOCKS_NOTHING

    print('checking for no block')

    print('custom block: {:b}'.format(custom_block))
    print('bitwise checker: {:b}'.format(bitwise_checker))

    print('combination: {:b}'.format(custom_block & bitwise_checker))
    print('check result: {}'.format(custom_block & bitwise_checker == bitwise_checker))


def force_spawn_entity(game_level, x, y):
    assert game_level.grid[y][x].blockTypes & BLOCKS_MOVEMENT != BLOCKS_MOVEMENT

    for e in game_level.allEntities:
        assert e.co.x != x or e.co.y != y

    return NPC.randomSpawnNPC(x, y, game_level.itemsAvalibleForDepth, game_level.itemsByTypeAvalibleForDepth,
                              game_level.avalibleSpecies, game_level.depth)


def set_up_level(gameLevel, player_co, enemy_cos, put_player_in_entitiy_list=False):
    from level import prep_level_for_unit_testing
    from terrain import ALL_TILE_DICT

    prep_level_for_unit_testing(gameLevel)

    for y in range(4, 10):
        gameLevel.grid[y][9] = ALL_TILE_DICT['TERRAIN_WALL']

    for x in range(6, 12):
        gameLevel.grid[15][x] = ALL_TILE_DICT['TERRAIN_WALL']

    gameLevel.player = new_player_for_testing(player_co)

    if put_player_in_entitiy_list:
        gameLevel.allEntities = [gameLevel.player]
    else:
        gameLevel.allEntities = []
    i = 0
    il = 0

    for e in enemy_cos:
        gameLevel.allEntities.append(force_spawn_entity(gameLevel, e.x, e.y))


def unit_test2():

    from coords import Coords
    from level import Level, prep_level_for_unit_testing, BLOCKS_MOVEMENT
    from line_of_sight import find_end_point_alt

    gameLevel = Level(0)

    start_point = Coords(4, 4)

    targets = [
        Coords(4, 12),
        Coords(12, 12),
        Coords(12, 4),
        Coords(2, 2),
        Coords(2, 4),
        Coords(1, 7)
    ]

    set_up_level(gameLevel, start_point, targets)

    for t in targets:
        ep = find_end_point_alt(gameLevel, start_point, t, BLOCKS_MOVEMENT, max_range=20)
        print('Start point: {}, target: {}, end point: {}, end point tile symbol: {}'.format(
            start_point, t, ep, gameLevel.grid[ep.y][ep.x].symbol))
        print(start_point.distance(ep))

    print('Max Range of 3')

    for t in targets:
        ep = find_end_point_alt(gameLevel, start_point, t, BLOCKS_MOVEMENT, max_range=3)
        print('Start point: {}, target: {}, end point: {}, end point tile symbol: {}'.format(
            start_point, t, ep, gameLevel.grid[ep.y][ep.x].symbol))
        print(start_point.distance(ep))


    for y in range(gameLevel.widthHeight.y):
        print(''.join([x.symbol for x in gameLevel.grid[y]]))


def unit_test3():
    import tdl
    from line_of_sight import find_end_point_alt, get_entities_in_line_of_fire_hash
    from coords import Coords
    from terrain import ALL_TILE_DICT

    length_compatison = []
    increase_amount = []

    gc.set_debug(gc.DEBUG_LEAK | gc.DEBUG_STATS)

    pr = cProfile.Profile()

    from level import Level, prep_level_for_unit_testing

    gameLevel = Level(0)

    start_point = Coords(4, 4)

    targets = [
        Coords(4, 12),
        Coords(12, 12),
        Coords(12, 4),
        Coords(2, 2),
        Coords(2, 4),
        Coords(1, 7),
        Coords(5, 7),
        Coords(6, 6)
    ]

    set_up_level(gameLevel, start_point, targets)

    console = tdl.init(gameLevel.widthHeight.x, gameLevel.widthHeight.y, title="Test", fullscreen=False)

    for y in range(gameLevel.widthHeight.y):

        console.draw_str(0, y, ''.join([s.symbol for s in gameLevel.grid[y]]))

    console.draw_char(start_point.x, start_point.y, '@')

    tdl.flush()

    quit = False

    while not quit:
        pr.enable()

        for y in range(gameLevel.widthHeight.y):
            console.draw_str(0, y, ''.join([s.symbol for s in gameLevel.grid[y]]))

        console.draw_char(start_point.x, start_point.y, '@')

        for e in gameLevel.allEntities:
            console.draw_char(e.co.x, e.co.y, 'M')

        tdl.flush()

        events = tdl.event.get()

        mouse_events = [e for e in events if e.type == "MOUSEUP"]

        key_events = [e for e in events if e.type == 'KEYDOWN']

        for e in key_events:
            if e.key == 'ESCAPE':
                quit = True
                break

        if len(mouse_events) > 0:
            _x = mouse_events[0].cell[0]
            _y = mouse_events[0].cell[1]

            # console.draw_char(x, y, '^')

            end_point = find_end_point_alt(gameLevel, start_point, Coords(_x, _y), BLOCKS_MOVEMENT, 20)

            distance_to_cursor = start_point.distance(_x, _y)

            distance_to_endpoint = start_point.distance(end_point)

            console.draw_char(end_point.x, end_point.y, '%')

            diff_x = end_point.x - start_point.x
            diff_y = end_point.y - start_point.y

            console.draw_char(_x, _y, '!')

            tdl.flush()

            normed_co = Coords(diff_x, diff_y).normalize()

            hit_target = False

            new_x = start_point.x

            new_y = start_point.y

            while not hit_target:
                new_x += normed_co[0]
                new_y += normed_co[1]

                check_x = round(new_x)
                check_y = round(new_y)

                console.draw_char(check_x, check_y, '*')
                tdl.flush()

                hit_target = end_point.x == check_x and end_point.y == check_y

            ents = get_entities_in_line_of_fire_hash(gameLevel, gameLevel.player, end_point)

            for e in ents:
                console.draw_char(e.co.x, e.co.y, 'E')

            tdl.flush()

            pr.print_stats()
            print(gc.get_threshold())
            length_compatison.append(len(gc.garbage))
            if len(increase_amount) == 0:
                increase_amount.append(0)
            else:
                increase_amount.append(length_compatison[-1] - length_compatison[-2])
            print(length_compatison)
            print(increase_amount)

            # print(gc.garbage)
            pass


def unit_test4():
    import tdl
    from line_of_sight import find_end_point_alt, get_entities_in_line_of_fire_hash
    from coords import Coords
    from terrain import ALL_TILE_DICT

    length_compatison = []
    increase_amount = []

    gc.set_debug(gc.DEBUG_UNCOLLECTABLE | gc.DEBUG_STATS)

    pr = cProfile.Profile()

    from level import Level, prep_level_for_unit_testing

    gameLevel = Level(0)

    start_point = Coords(4, 4)

    targets = [
        Coords(4, 12),
        Coords(12, 12),
        Coords(12, 4),
        Coords(2, 2),
        Coords(2, 4),
        Coords(1, 7),
        Coords(5, 7),
        Coords(6, 6)
    ]

    set_up_level(gameLevel, start_point, targets)


    console = tdl.init(gameLevel.widthHeight.x, gameLevel.widthHeight.y, title="Test", fullscreen=False)

    for y in range(gameLevel.widthHeight.y):

        console.draw_str(0, y, ''.join([s.symbol for s in gameLevel.grid[y]]))

    console.draw_char(start_point.x, start_point.y, '@')

    tdl.flush()

    quit = False

    test_crood_list = [
        Coords(13, 20),
        Coords(16, 20),
        Coords(25, 20),
        Coords(30, 20),
        Coords(13, 22),
        Coords(16, 22),
        Coords(25, 22),
        Coords(30, 22),
    ]

    test_crood_list_y = [20, 22, 25, 28, 31, 35, 39, 42]

    test_crood_list_x = [13, 16, 20, 23, 25, 27, 30, 33]

    for y in test_crood_list_y:
        for x in test_crood_list_x:

            pr.enable()

            for y2 in range(gameLevel.widthHeight.y):
                console.draw_str(0, y2, ''.join([s.symbol for s in gameLevel.grid[y]]))

            console.draw_char(start_point.x, start_point.y, '@')

            for e in gameLevel.allEntities:
                console.draw_char(e.co.x, e.co.y, 'M')

            # tdl.flush()

            _x = x
            _y = y

            end_point = find_end_point_alt(gameLevel, start_point, Coords(_x, _y), BLOCKS_MOVEMENT, 20)

            distance_to_cursor = start_point.distance(_x, _y)

            distance_to_endpoint = start_point.distance(end_point)

            console.draw_char(end_point.x, end_point.y, '%')

            diff_x = end_point.x - start_point.x
            diff_y = end_point.y - start_point.y

            console.draw_char(_x, _y, '!')

            # tdl.flush()

            normed_co = Coords(diff_x, diff_y).normalize()

            hit_target = False

            new_x = start_point.x

            new_y = start_point.y

            while not hit_target:
                new_x += normed_co[0]
                new_y += normed_co[1]

                check_x = round(new_x)
                check_y = round(new_y)

                console.draw_char(check_x, check_y, '*')
                tdl.flush()

                hit_target = end_point.x == check_x and end_point.y == check_y

            ents = get_entities_in_line_of_fire_hash(gameLevel, gameLevel.player, end_point)

            for e in ents:
                console.draw_char(e.co.x, e.co.y, 'E')

            tdl.flush()

            pr.print_stats()
            print(gc.get_threshold())
            length_compatison.append(len(gc.garbage))
            if len(increase_amount) == 0:
                increase_amount.append(0)
            else:
                increase_amount.append(length_compatison[-1] - length_compatison[-2])
            print('{} {}'.format(x, y))
            print(length_compatison)
            print(increase_amount)

            # print(gc.garbage)
            pass


def unit_test5():
    import tdl
    from line_of_sight import find_end_point_alt, get_entities_in_line_of_fire_hash
    from coords import Coords, DIR_CENTER, DIR_DOWN_LEFT, DIR_RIGHT, DIR_DOWN_RIGHT, DIR_LEFT, DIR_DOWN, DIR_UP_LEFT, DIR_UP, DIR_UP_RIGHT
    from terrain import ALL_TILE_DICT

    from color_factory import ALL_COLORS_DICT

    gc.set_debug(gc.DEBUG_UNCOLLECTABLE | gc.DEBUG_STATS)

    pr = cProfile.Profile()

    from level import Level, prep_level_for_unit_testing

    from game_commands import targetCursior

    gameLevel = Level(0)

    start_point = Coords(4, 4)

    targets = [
        Coords(4, 12),
        Coords(12, 12),
        Coords(12, 4),
        Coords(2, 2),
        Coords(2, 4),
        Coords(1, 7),
        Coords(5, 7),
        Coords(6, 6)
    ]

    set_up_level(gameLevel, start_point, targets)

    console = tdl.init(gameLevel.widthHeight.x, gameLevel.widthHeight.y, title="Test", fullscreen=False)

    for y in range(gameLevel.widthHeight.y):

        console.draw_str(0, y, ''.join([s.symbol for s in gameLevel.grid[y]]))

    console.draw_char(start_point.x, start_point.y, '@')

    for e in gameLevel.allEntities:

        console.draw_char(e.co.x, e.co.y, e.getSymbol)

    cursorCoords = gameLevel.player.co

    tdl.flush()

    quit = False

    valueDict = dict()

    valueDict['directionDict'] = {
        'UP': DIR_UP,
        'KP8': DIR_UP,
        'w': DIR_UP,
        'W': DIR_UP,

        'q': DIR_UP_LEFT,
        'Q': DIR_UP_LEFT,
        'KP7': DIR_UP_LEFT,

        'DOWN': DIR_DOWN,
        'KP2': DIR_DOWN,
        'x': DIR_DOWN,
        'X': DIR_DOWN,

        'e': DIR_UP_RIGHT,
        'E': DIR_DOWN_RIGHT,
        'KP9': DIR_UP_RIGHT,

        'LEFT': DIR_LEFT,
        'KP4': DIR_LEFT,
        'a': DIR_LEFT,
        'A': DIR_LEFT,

        'c': DIR_DOWN_RIGHT,
        'C': DIR_DOWN_RIGHT,
        'KP3': DIR_DOWN_RIGHT,

        'RIGHT': DIR_RIGHT,
        'KP6': DIR_RIGHT,
        'd': DIR_RIGHT,
        'D': DIR_RIGHT,

        'z': DIR_DOWN_LEFT,
        'Z': DIR_DOWN_LEFT,
        'KP1': DIR_DOWN_LEFT,

        's': DIR_CENTER,
        'S': DIR_CENTER,
        'KP5': DIR_CENTER
    }

    valueDict['screenOffset'] = Coords(0, 0)

    valueDict['windowDict'] = {
        'mainWindow': console
    }

    valueDict['gameLevel'] = gameLevel

    targetCursior(valueDict)


def unit_test6():
    from game_commands import init, handle_keys, implement_actions, centerScreenOnPlayer, add_to_events_to_draw, \
        drawEntities, drawItems, paint_character, paint_screen, paint_screen_limited, redraw_status_window, \
        redraw_inventory, can_run_in_direction
    from level import Level, prep_level_for_unit_testing
    from coords import Coords, DIR_CENTER
    import tdl, time, cProfile
    from line_of_sight import lookLOS
    from magic_effects import EFFECTS_BY_ITEM_TYPE

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)

    def drawGameScreen(vDict):
        if vDict['centered']:
            paint_screen(vDict)
        else:
            paint_screen_limited(vDict)

        drawItems(vDict)
        drawEntities(vDict, vDict['centered'])

        player_co = vDict['gameLevel'].player.co

        paint_character(vDict, '@', player_co.x, player_co.y, BLACK, WHITE)

    pr = cProfile.Profile()

    valueDict = init()

    gameLevel = Level(0)

    start_point = Coords(30, 30)

    targets = [
        Coords(4, 12),
        Coords(12, 12),
        Coords(12, 4),
        Coords(2, 2),
        Coords(2, 4),
        Coords(1, 7),
        Coords(5, 7),
        Coords(6, 6)
    ]

    set_up_level(gameLevel, start_point, [], put_player_in_entitiy_list=True)

    item_names = ['SPEAR', 'MORNING_STAR', 'CROWN', 'LEATHER_GLOVES', 'SCALE_ARMOR', 'POT_HELM', 'REINFORCED_BOOT', 'AXE', 'ARROW', 'ROUND_SHIELD', 'WIND_BOW'] + ['KNOT_OF_' + a for a in EFFECTS_BY_ITEM_TYPE['KNOT'].keys()]
    x_list = [35, 29, 37, 34, 31, 40, 28, 39, 36, 27, 32, 38, 41]
    y_list = [34, 37, 31, 27, 29, 32, 39, 23, 27, 33, 40, 33, 28]

    for n, x, y in zip(item_names, x_list, y_list):
        place_specific_item(gameLevel, n, x, y)

    valueDict['gameLevel'] = gameLevel

    while not valueDict['exit_game']:

        valueDict['centered'] = centerScreenOnPlayer(valueDict)

        while not tdl.event.is_window_closed():

            px, py = gameLevel.player.co.x, gameLevel.player.co.y

            valueDict['centered'] = centerScreenOnPlayer(valueDict)

            if valueDict['turnPassed']:

                gameLevel.removeDeadEntities()

                pr.enable()

                ai_npcs = list((e for e in gameLevel.allEntities if e.canMove and not e.isPlayer))

                behavour_time = 0

                start_time = time.time()

                for e in ai_npcs:
                    # decide what action to take here

                    e.behavour_ai.decide(gameLevel, e)

                    # behavour_time += timeit.timeit(stmt=lambda: e.behavour_ai.decide(gameLevel, e), number=1)

                # **************************************

                # all entities implement (or try to) whatever action that they have dicided on

                # **************************************

                npcs_with_target = [e for e in ai_npcs if
                                    e.behavour_ai.target is not None and e.behavour_ai.target.isPlayer]

                implement_actions(valueDict, add_to_events_to_draw)

                if gameLevel.player.behavour_ai.move_direction != DIR_CENTER:
                    lookLOS(valueDict)

                end_time = time.time()

                # ti = timeit.timeit(stmt=lambda: lookLOS(valueDict), number=1)

                ti = end_time - start_time

                if ti > 0.05:

                    pr.print_stats()

                else:

                    pr.disable()

                empty_level_spaces = gameLevel.number_of_open_spaces

                numbert_of_entities = len(gameLevel.allEntities)

                # print('Time taken for lookLOS method: {}'.format(ti))

                redraw_status_window(valueDict)

                if valueDict['TIME'] % 5 == 0:
                    for e in gameLevel.allEntities:
                        e.tick()

                if valueDict['TIME'] % 30 == 0:
                    totalMem = valueDict['gameLevel'].debugMemoryUsage

                if valueDict['TIME'] % 45 == 0:
                    valueDict['gameLevel'].spawn_single_inhabitant()

                if valueDict['TIME'] >= 30000:
                    valueDict['TIME'] = -30000
                else:
                    valueDict['TIME'] += 1

            seenItems = tuple(i for i in valueDict['gameLevel'].itemsOnFloor if i.seen)

            totalMem = valueDict['gameLevel'].debugMemoryUsage

            mem = 'Item memory used: {0[0]}, entity memory used: {0[1]}, level memory used: {0[2]}, total memory ' \
                  'used: {0[3]}'

            # print(mem.format(totalMem))

            valueDict['turnPassed'] = False

            print(gc.get_threshold())

            # print([o for o in gc.get_objects() if isinstance(o, dict)])
            # print(gc.get_objects())
            # print(gc.get_referrers([o for o in gc.get_objects() if isinstance(o, dict)]))
            print(gc.garbage)
            print(len(gc.garbage))

            """

            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics('lineno')

            for stat in top_stats[:10]:
                print(stat)
            """

            if valueDict['need_to_update_item_view']:
                redraw_inventory(valueDict)

            if valueDict['exit_game']:
                break

            if gameLevel.player.moveTimeLeft >= 1.0:
                if not valueDict['runInDirection']:

                    drawGameScreen(valueDict)
                    tdl.flush()
                    handle_keys(valueDict)

                elif not can_run_in_direction(valueDict):

                    drawGameScreen(valueDict)
                    tdl.flush()
                    handle_keys(valueDict)

                else:
                    valueDict['turnPassed'] = True
            else:
                valueDict['turnPassed'] = True


"""

def test_gc():

    before = defaultdict(int)
    after = defaultdict(int)
    for i in get_objects():
        before[type(i)] += 1


    leaked_things = [[x] for x in range(10)]

    for i in get_objects():
        after[type(i)] += 1

    print [(k, after[k] - before[k]) for k in after if after[k] - before[k]]
"""


# [(<type 'list'>, 11)]