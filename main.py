# BTCallahan, 5/2/2018
# version 6.5 7/28/2018

# Trial of Asturta: Wreck (or Save) the World


from game_commands import init, blank_main_screen, add_to_events_to_draw, splash_input, handle_char_selection, \
    redraw_status_window, centerScreenOnPlayer, drawItems, drawEntities, redraw_inventory, handle_keys, paint_screen, \
    paint_screen_limited, \
    paint_character, splash_screen, can_run_in_direction, implement_actions, BLACK, WHITE
from line_of_sight import lookLOS
import tdl, math, os, re, timeit, time, gc
# import tcod as libtcod
import cProfile
import tracemalloc

from level import Level
from species import debugBalance
from character_builder import SpeciesSelector
from entites import Player
from data_globals import FILE_LOCATION_NAME
from color_factory import ALL_COLORS_DICT
from coords import DIR_CENTER
from terrain import Terrain

tracemalloc.start()


"""
regex guide:

^ = matches the start of a string.
$ = matches the end of a string
. = matches any charcter except for a new line
[] = a class. It matches any charcter inside the brackets
- = use with brackes to match a range of charcters, e.g. [b-t]
[^] = the ^ when placed inside a bracked will invert it. e.g [^b-t] will match any character that is not in the range
() = a group
* = tells the search to match the prevsout theing, a characgter, group, or class. zero ore more repititions
+ = like *, but one or more repititions
? = zero or one repititions
{,} = matches a custon number of repititions. e.g. {5, 10} matches between five and ten repititions. {,6} matches between zero and six
    {5,} matches at least five
\1
"""

class TestClass:

    def __init__(self, name, symbol, values1, values2, optional1, optional2, optional3):
        self.name = name
        self.symbol = symbol
        self.values1 = values1
        self.values2 = values2

        self.optional1 = optional1
        self.optional2 = optional2
        self.optional3 = optional3

    def __str__(self):
        return '''Name: {0.name}, Symbol: {0.symbol}, Values 1:
{0.values1[0]}, {0.values1[1]}, {0.values1[2]}, {0.values1[3]},
{0.values1[4]}. Values 2: {0.values2[0]}, {0.values2[1]}, {0.values2[2]},
{0.values2[3]}, {0.values2[4]}. Optional 1: {0.optional1}. Optional 2:
{0.optional2[0]}, {0.optional2[1]}, {0.optional2[2]}. Optional 3:
{.optional3}'''.format(self)

def testRegrex():
    print('beginning regex')

    #reg = r'(?P<name>ff)'

    classList = []

    def checkForOptionalInfo(textToLookFor, stringToCheck, dataType, default):
        if re.search(textToLookFor, stringToCheck):

            searchResult = re.finditer(textToLookFor + '(.+)\n', stringToCheck)

            #checks if the values are an array
            if re.search(r'[:]', searchResult):
                toList = re.split(r'[:]', s)
                if dataType == 'INT':
                    return list(map(lambda l: int(l), toList))
                elif dataType == 'FLOAT':
                    return list(map(lambda l: float(l), toList))
                else:
                    return toList
            else:
                if dataType == 'INT':
                    return int(searchResult)
                elif dataType == 'FLOAT':
                    return float(searchResult)
                return searchResult
        else:
            return default

    s = open(str(FILE_LOCATION_NAME + '/testRegex.txt', 'r'))

    a = s.read()

    sList = re.split(r'NAME:', a)


    for sp in sList:


        if re.match(r'(.+)\n\n', sp):

            i = re.finditer(r'(.+)', sp)#find the name and symbol uppercase name to use as a dictionary key

            name, symbol = re.split(r'[:]', i[0])

            capName = name.upper()

            stats = re.split(r'[:]', re.finditer('VALUES1:[:.123456789]{2, 10}\n', sp))

            values1 = list(map(lambda l: int(l), stats))

            skills = re.split(r'[:]', re.finditer('VALUES2:[:.123456789]{2, 10}\n', sp))

            values2 = list (map(lambda l: int(l), skills))

            optional1 = checkForOptionalInfo('OPTIONAL1', sp, 'INT', 0)

            optional2 = checkForOptionalInfo('OPTIONAL2', sp, 'INT', [0, 0, 0])

            optional3 = checkForOptionalInfo('OPTIONAL3', sp, 'FLOAT', 0.0)

            classList.append(TestClass(name, symbol, values1, values2, optional1, optional2, optional3))

    s.close()

    for c in classList:
        print(c)

    print('ending regex')

#testRegrex()

#valueDict, windowDict = dict(), dict()
#console, mainWindow, textWindow, invenWindow, statusWindow = None, None, None, None, None

#gameLevel, charGenerator = None, None

#exit_game = False

#blankEventText, blankMainScreenText, blankInvenText = '', '', ''

def debugColors(start, end):
    it = list(ALL_COLORS_DICT.items())[start:end]
    for i in it:
        print('''color name: {0[0]}, color informal name: {0[1].name},
color r: {0[1][0]}, g: {0[1][1]}, b: {0[1][2]}'''.format(i))

#debugColors(10, 20)


#run the game
def main():
    gc.set_debug(gc.DEBUG_UNCOLLECTABLE | gc.DEBUG_STATS)

    pr = cProfile.Profile()

    def drawGameScreen(vDict):
        if vDict['centered']:
            paint_screen(vDict)
        else:
            paint_screen_limited(vDict)

        drawItems(vDict)
        drawEntities(vDict, vDict['centered'])

        player_co = vDict['gameLevel'].player.co

        paint_character(vDict, '@', player_co.x, player_co.y, BLACK, WHITE)

    valueDict = init()

    windowDict = valueDict['windowDict']

    mainWindow = windowDict['mainWindow']

    splash_screen(valueDict)

    gameLevel = None

    if not valueDict['exit_game']:
        while not tdl.event.is_window_closed():

            if splash_input(valueDict):
                break

    if not valueDict['exit_game']:
        charGenerator = SpeciesSelector(0, 12, 25, valueDict['lowestDepth'])
        blank_main_screen(valueDict)
        charGenerator.speciesInfo(mainWindow)
        charGenerator.statInfo(mainWindow)
        charGenerator.skillInfo(mainWindow)
        charGenerator.appearinceInfo(mainWindow)
        tdl.flush()

    if not valueDict['exit_game']:
        while not tdl.event.is_window_closed():

            if handle_char_selection(valueDict):
                break

    if not valueDict['exit_game']:

        gameLevel = Level(0)

        valueDict['gameLevel'] = gameLevel

        playerx, playery = gameLevel.getRandomSpawnPoint

        charGenerator = valueDict['charGenerator']

        player = Player.fromGenerator(charGenerator, playerx, playery)

        gameLevel.assignPlayer(player)

    if not valueDict['exit_game']:

        valueDict['centered'] = centerScreenOnPlayer(valueDict)

        ti = 'lookLOS(valueDict)'

        print('Time taken: {}'.format(
            timeit.timeit(stmt=lambda: lookLOS(valueDict), number=10)))

        seenItems = tuple(i for i in valueDict['gameLevel'].itemsOnFloor if i.seen)

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

                npcs_with_target = [e for e in ai_npcs if e.behavour_ai.target is not None and e.behavour_ai.target.isPlayer]

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

if __name__ == '__main__':
    # main()

    import debugging
    debugging.unit_test6()

"""
Objective: To create a simple utility AI capable of simulating diffrente actions,
evaluating the possible results of the actions, and choosing the one that has the
best results.

Let us assume that we have two objects, each of which repersent a starship, and that each
starship has several data values that repersent diffrent attributes. These attributes are:

Current energy reserves
Maximim shield strenght
Current shield strenght

"""


"""
1 ton = 907.185 ko
1 kg = 299792458 j

1 tone of tnt = 4184000000 j

def calc(tons_of_matter):
    return (tons_of_matter * 907.185 * 299792458) / 4184000000

"""