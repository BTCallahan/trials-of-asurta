import timeit, time, tdl

# import tcod as libtcod
from collections import deque
from data_globals import ALPHABET, FILE_LOCATION_NAME, ACTIVATIABLE_SET, ALL_STATS, check_if_entity_can_use_equip_item
from coords import Coords, DIR_CENTER, DIR_DOWN, DIR_DOWN_LEFT, DIR_DOWN_RIGHT, DIR_LEFT, DIR_RIGHT, DIR_UP, \
    DIR_UP_LEFT, DIR_UP_RIGHT
from character_builder import SpeciesSelector
from color_factory import ALL_COLORS_DICT

WHITE = list(ALL_COLORS_DICT['WHITE'])

BLACK = list(ALL_COLORS_DICT['BLACK'])

PURPLE = list(ALL_COLORS_DICT['PURPLE'])

def check_quit(input):
    return input.keychar in {'q', "Q"} and input.control

def init():
    """Initalizes the game by reading from the init.txt file and returns a dictionary containing
    important values."""
    # global valueDict, windowDict, blankEventText, blankMainScreenText, blankInvenText
    directory = FILE_LOCATION_NAME

    fontDirectory = directory + '/arial10x10.png'

    tdl.set_font(fontDirectory, greyscale=True, altLayout=True)

    dataValues = ('SCREEN_WIDTH', 'SCREEN_HEIGHT', 'INFO_WINDOW_HEIGHT', 'INVEN_WINDOW_WIDTH')
    initDirectory = directory + '/init.txt'

    f = open(initDirectory, 'r')
    rDict = dict()

    flines = f.read().split('\n')

    for fl in flines:
        for d in dataValues:

            if fl.startswith(d):

                rDict[d] = int(fl.split(':')[1])
    f.close()

    rDict['screenOffset'] = Coords(0, 0)
    rDict['showEquipment'] = False
    rDict['turnPassed'] = 0
    rDict['TIME'] = 0
    rDict['lowestDepth'] = 0
    rDict['runInDirection'] = False
    rDict['timeDelay'] = 0.15

    rDict['player_used_stairs'] = False

    # rDict['SCREEN_WIDTH'] = 60
    # rDict['SCREEN_HEIGHT'] = 40

    blankEventText = '{:<' + str(rDict['SCREEN_WIDTH'] - 2) + '}'  # ' ' * (SCREEN_WIDTH - 2)
    blankMainScreenText = ' ' * rDict['SCREEN_WIDTH']
    blankInvenText = '{:<' + str(rDict['INVEN_WINDOW_WIDTH'] - 2) + '}'

    halfBlankInvenText = '{:<' + str(rDict['INVEN_WINDOW_WIDTH'] // 2 - 2) + '}'

    rDict['need_to_update_item_view'] = True

    rDict['blankEventText'] = blankEventText
    rDict['blankMainScreenText'] = blankMainScreenText
    rDict['blankInvenText'] = blankInvenText
    rDict['halfBlankInvenText'] = halfBlankInvenText

    rDict['inventory_display_type'] = 'INVENTORY'

    rDict['centered'] = False

    initialBlankEventTextList = list((blankInvenText.format(' ') for t in range(rDict['INFO_WINDOW_HEIGHT'] - 2)))

    eventsToPrint = deque(list(initialBlankEventTextList), maxlen=rDict['INFO_WINDOW_HEIGHT'] - 2)

    rDict['eventsToPrint'] = eventsToPrint

    rDict['exit_game'] = False

    charGenerator = SpeciesSelector(0, 12, 25, rDict['lowestDepth'])

    rDict['charGenerator'] = charGenerator

    console = tdl.init(rDict['SCREEN_WIDTH'] + rDict['INVEN_WINDOW_WIDTH'],
                       rDict['SCREEN_HEIGHT'] + rDict['INFO_WINDOW_HEIGHT'], title="Trial of Asturta",
                       fullscreen=False)

    mainWindow = tdl.Window(console, 0, 0, rDict['SCREEN_WIDTH'],
                            rDict['SCREEN_HEIGHT'])

    textWindow = tdl.Window(console, 0, rDict['SCREEN_HEIGHT'],
                            rDict['SCREEN_WIDTH'], rDict['INFO_WINDOW_HEIGHT'])

    textWindow.draw_frame(0, 0, rDict['SCREEN_WIDTH'],
                          rDict['INFO_WINDOW_HEIGHT'], '%')

    invenWindow = tdl.Window(console, rDict['SCREEN_WIDTH'], 0,
                             rDict['INVEN_WINDOW_WIDTH'], rDict['SCREEN_HEIGHT'])

    invenWindow.draw_frame(0, 0, rDict['INVEN_WINDOW_WIDTH'],
                           rDict['SCREEN_HEIGHT'], '&')

    statusWindow = tdl.Window(console, rDict['SCREEN_WIDTH'],
                              rDict['SCREEN_HEIGHT'], rDict['INVEN_WINDOW_WIDTH'], rDict['INFO_WINDOW_HEIGHT'])

    statusWindow.draw_frame(0, 0, rDict['INVEN_WINDOW_WIDTH'],
                            rDict['INFO_WINDOW_HEIGHT'], '*')

    windowDict = {'console': console,
                  'mainWindow': mainWindow,
                  'textWindow': textWindow,
                  'invenWindow': invenWindow,
                  'statusWindow': statusWindow
                  }

    rDict['windowDict'] = windowDict

    directionDict = {
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

    action_dict = {'g': pickup,
                   'y': drop,

                   'r': remove_item,
                   'p': equip_item,

                   't': throw_item,
                   'f': ranged_attack,

                   'u': use_item,
                   'b': use_ability,

                   '>': stairs_down,
                   '.': stairs_down,

                   '<': stair_up,
                   ',': stair_up,

                   '/': toggle_inventory,

                   'l': swap_equipment
                   }

    rDict['action_dict'] = action_dict

    rDict['directionDict'] = directionDict

    return rDict

# debugBalance()


def handle_ingame_help(vDict):

    windowDict = vDict['windowDict']

    mainWindow = windowDict['mainWindow']

    mainWindow.draw_str(1, 1, """""")


def gen_events_to_draw(vDict):
    """Generates several strings consisting only of spaces for initalizing the text window."""
    blankEventText = vDict['blankEventText']
    for i in range(vDict['INFO_WINDOW_HEIGHT'] - 2):
        yield blankEventText.format(' ')


def gen_invertory_text(vDict):
    blankInvenText = vDict['blankInvenText']
    for i in range(vDict['SCREEN_HEIGHT'] - 2):
        yield blankInvenText.format(' ')


def safe_divide(a, b):
    if b == 0:
        return 0
    return a / b


def blank_main_screen(vDict):
    """Overwrites the main screen with blank characters then calls tdl.flush()."""

    blankMainScreenText = vDict['blankMainScreenText']

    wDict = vDict['windowDict']

    for y in range(vDict['SCREEN_HEIGHT']):
        wDict['mainWindow'].draw_str(0, y, blankMainScreenText)
        # mainWindow.
    tdl.flush()


def add_to_events_to_draw(vDict, textEvent):
    """Adds a string to the eventsToPrint list and paints its contents to the event window."""

    windowDict = vDict['windowDict']

    textWindow = windowDict['textWindow']

    blankEventText = vDict['blankEventText']

    windowDict = vDict['windowDict']

    textWindow = windowDict['textWindow']

    lastEvent = vDict['eventsToPrint'][-1]

    match = textEvent == lastEvent.rstrip(' ')

    if match:
        # if textEvent equals the last line in the eventsToPrint list
        vDict['eventsToPrint'][-1] = '{} <x{}>'.format(textEvent, '2')
    elif vDict['eventsToPrint'][-1].startswith(textEvent):
        # elif the last line in the eventsToPrint starts with textEvent
        st = vDict['eventsToPrint'][-1].split(' <x')
        try:
            st1, st2 = st[0], int(st[1].strip('>'))
            vDict['eventsToPrint'][-1] = '{} <x{}>'.format(textEvent, st2 + 1)
        except IndexError:
            print('Index error')
            print(st)
    else:
        vDict['eventsToPrint'].popleft()
        vDict['eventsToPrint'].append(blankEventText.format(textEvent))
    #l = vDict['eventsToPrint'].pop(0)
    #vDict['eventsToPrint'].append(blankEventText.format(textEvent))

    for t in range(vDict['INFO_WINDOW_HEIGHT'] - 2):
        try:
            textWindow.draw_str(1, 1 + t, blankEventText)
            events_print = vDict['eventsToPrint'][t]
            textWindow.draw_str(1, 1 + t, events_print)
        except tdl.TDLError:
            pass

    # tdl.flush()

def splash_screen(vDict):
    """Draws the splash screen."""

    wDict = vDict['windowDict']

    mainWindow = wDict['mainWindow']

    titleText = 'Trial of Asturta'
    subtitleText = 'Wreck (or save) the World'

    titleX = (vDict['SCREEN_WIDTH'] // 2) - len(titleText) // 2
    titleY = (vDict['SCREEN_HEIGHT'] // 6) * 2

    subtitleX = (vDict['SCREEN_WIDTH'] // 2) - len(subtitleText) // 2
    subtitleY = titleY + 1

    mainWindow.draw_str(titleX, titleY, titleText)

    mainWindow.draw_str(subtitleX, subtitleY, subtitleText)

    optionInfoX = (vDict['SCREEN_WIDTH'] // 5) * 1
    optionInfoY = (vDict['SCREEN_HEIGHT'] // 4) * 3

    mainWindow.draw_str(optionInfoX, optionInfoY, '(n)new game, (o)pen saved game, (h)elp')
    # tdl.flush()

def splash_input(vDict):
    """Handles any input to the splash screen using the tdl.event.key_wait() method
to return an event, then checks the keychar. If the keychar is 'n', it returns true.
If it is 'l', then it prints the games background information to the screen and calls
tdl.flush(). If it is 'h', it prints the help text and calls tdl.flush(). If it is 'o',
it handles the open game dioluge (not implmented)."""
    wDict = vDict['windowDict']

    mainWindow = wDict['mainWindow']
    q = tdl.event.get()

    user_input = tdl.event.key_wait()

    if check_quit(user_input):
        vDict['exit_game'] = True
        return True

    if user_input.keychar == 'n':

        return True

    elif user_input.keychar == 'l':
        blank_main_screen(vDict)

        mainWindow.draw_str(1, 1, 'a')
        tdl.flush()

    elif user_input.keychar == 'h':
        blank_main_screen(vDict)
        mainWindow.draw_str(1, 1, 'a')
        tdl.flush()

    elif user_input.keychar == 'o':
        pass


def handle_help_input(vDict):

    startX = 12
    startY = 5
    """This 
    game is unlike the majority of roguelikes in that it is not based of an experince system - the player improves his or 
    her skills soley through practise - there is no benfit, save materiral, for slaying another creature. Indeed, it is 
    completly possible to win the game without killing another creature. Another major difference is that as there are no 
    classes, a player's skill progression is limited only by one's species aptitude."""

    wDict = vDict['windowDict']

    mainWindow = wDict['mainWindow']

    blank_main_screen(vDict)

    helpChoicesTup = tuple(['General Information', 'What is a roguelike, anyway? A rant', 'Background and Lore',
                            'Creating a Character', 'Gameplay', 'Keyboard commands'])

    help_output_text = (
        '',  # 0
        '''Welcome the the world of the Trial of Asturta: Wreck (or Save) the World! 
    
        Trial of Asturta is a procedurally single player RPG in which the player seeks to descend to the depths of the 
        dungeon, recover an item of great power, and return the the surface.
    
        When starting a new game, the player is prompted with a list of species to choose from. Not all species are 
        availiable 
        when begining a new game, these must be unlocked by exploring the depths below.
    
                        ''',  # 1
        '''That's a very good question! Unlike terms such as \'first person shooter\' (a game in which the player 
        observes 
        the game world from a first person view and shoots at enemies), \'real time statagy\' (a game requires the use 
        of strategic level unit managment that 
        takes place in real time) the word roguelike has no obvious meaning. It simply means \'like or pertaining to 
        rogue\'. In this case rogue refers to the 1980 video game by Michael Toy and Glenn Wichman, so the term 
        \'roguelike\' can be understood to mean \'a game possessing gameplay and characteristics similar to the 1980 
        Unix game Rogue\'. Wordy, but it gets the job done.
        
        Characteristics of Rogue:
        1. Turn-based gameplay
        2. Permanent consequences (no reloading a saved game)
        3. Procedurally generated levels
        4. No player race or class selections
        5. No non-player characters to peacefully interact with (e.g. shoopkeepers), only monsters
        6. No overworld or town level
        7. No shops
        8. No non-endgame related quests
        9. No spells
        10. The player improves his or her abilities through mass homicide
        11. Single character, no parties
        12. Player achieves victory by retrieving a specific object from the dungeon
        
        Of these characteristics, Angband fails 4, 6, 7, 9 and 12, Dungeon Crawl Stone Soup fails 4, 5, 7, and 9, 
        Nethack fails 4, 5, 7, 9, and ADOM fails 4, 6, 7, 9 and 12.
        
        It appears most roguelikes are not actually roguelikes.
        
        Complicating the matter is that the games Beneath Apple Manor (1978, Don Worth), and Star Trek (1971, Mike 
        Mayfield) both predate Rogue. Of these two Beneath Apple Manor fails only 7, and Star Trek fails only 10 and 12.
        
        tself is inherently is in ''',  # 2

        '''Before the Beginning of all Beginnings:
    
        Before Time existed, there was only perfect Symmetry. It was stillness and silence, and it extended without end. But 
        this symmetry was unstable and shattered. Thus the imperfect WORLD came into existence, and so did the Cycle.
    
        Of the Cycle:
    
        The Cycle has no beginning and no end. It is a process, by which the WORLD is created and destroyed. Every incarnation 
        is different. Even the Powers of the WORLD are bound to it. As it dies and is reborn, so are they. The current 
        incarnation is know by the name Asurta.
    
        The Coming End and Rebirth:
    
        After tens of thousands of years, Asurta is nearing its end. As the WORLDS's rebirth approaches, thousands pits have 
        open up all across its surface. Each of these pits is an entrance to the Vault of Trial. This Vault is a massive 
        underground structure made up of over a hundred floor and thousands of rooms and corridors. At the bottom of the Vault 
        lies the Mantle.
    
                ''',  # 3

        '''Character creation is divided into two steps. In the first, the player chooses 
        the gender and species of their character and allocates stat and skill points as they see fit. 
    
        The screen will displayer the details of the currently selected species and a background description on the left hand 
        side of the screen. On the right, 
    
        There is a wide variety of species to choose from, however not all will be available from the start. These must 
        unlocked by exploring the depths of the Vault. Something to keep in mind is that each species has bonuses and penalty 
        to stats and skills, as well as additional attributes such as size and movement speed. Others may have abilities that 
        can be activated during the game.
    
        Also, some species might have difficulty finding useful equipment because of their unusually shaped bodies. 
    
        To toggle between which stat or skill to change, use the up or down arrows, the 8 or 2 keys on the keypad, or the W or 
        X keys. To increment the selected stat or skill, use the right arrow, the number 6 on the keypad, or the D key. To 
        decrement it, use the left arrow, the number 4 or the A key.
    
        To cycle though the available species, use the left and right brackets or the comma and period keys.
    
        To toggle between genders, use the forward slash and back slash keys.
    
        Once the player is satisfied with his or her desisions, they can progress to the next phase of character generation by 
        pressing the enter key.
    
        In the second part, the player can \'buy\' items from a pre-generated list. 
        ''',  # 4

        '''One thing to keep in mind is that all actions require energy. Each living 
        character has a \'battery\' of energy that has a cap of 1.0 and replenishes itself at a rate of 1.0 per turn. Most 
        actions consume 1.0 worth of energy, so the rate evens out. Should a character performs an action that consumes more 
        then 1.0 units, the replenishment rate will be insufficent to raise their energy to 1.0 and they will be unable to take 
        any actions until it is restored. In the vast majority of case, this will simply mean \'looseing\' a turn. 
    
        Movement is slightly more complecated then most roguelikes. To move, use the number pad, the alphbetical keys on the 
        left side of the keyboard, or the arrow keys. Each move consumes an amount of energy based on the direction - diagonal 
        moves consume aproxminly 1.293 times as much energy as moving horizontaly or verticaly.
    
        One thing to keep in mind is that in order to move diagionaly, both the horizontal and vertical directions must be 
        unblocked. For example, if the player pressed a key to move in the upper right direction, then the game will check to 
        see if there is a wall blocking the grid square above the player\'s position, as well as checking to see if the square 
        to their right is blocked. If the grid square above the player\'s position is blocked, then they will move to the 
        right.
        ''',  # 5
        '''Arrow keys/Numberpad/QWEASDZXC: Movement control. Pressing 5 or S will make the player wait a turn.
        G: Pick up an item from the ground. If there is more then one item the player will be propmted to choose an item.
        R: Removes an equiped item and places it in the player's inventory.
        '''
        )

    inc = 0

    for h in helpChoicesTup:
        mainWindow.draw_str(startX, startY + inc, '{}. {}'.format(inc + 1, h))
        inc += 1

    q = tdl.event.get()

    user_input = tdl.event.key_wait()

    input_int = int(user_input.keychar)

    if 0 < input_int < len(help_output_text):
        mainWindow.draw_str(2, 2, help_output_text[input_int])


def handle_char_selection(vDict):
    """Handles input for character creation, alocateting stat and skill points, and purchesing equipment using the
tdl.event.key_wait() method to return an event object. If the user presses enter, then it switches to the second part
of character creation allowing the player to 'purches' equipment."""

    wDict = vDict['windowDict']

    # directionDict = vDict['directionDict']

    charGenerator = vDict['charGenerator']

    mainWindow = wDict['mainWindow']

    selectorUp = {'w', 'KP8', 'UP'}
    selectorDown = {'x', 'KP2', 'DOWN'}
    selectorInc = {'d', 'KP6', 'RIGHT'}
    selectorDeinc = {'a', 'KP4', 'LEFT'}

    q = tdl.event.get()
    user_input = tdl.event.key_wait()

    redraw = True

    if not charGenerator.buyItems:

        if check_quit(user_input):
            vDict['exit_game'] = True
            return True

        elif user_input.key in selectorUp or user_input.keychar in selectorUp:
            charGenerator.toggleStatOrSkill(True)
            charGenerator.statInfo(mainWindow)
            charGenerator.skillInfo(mainWindow)

        elif user_input.key in selectorDown or user_input.keychar in selectorDown:
            charGenerator.toggleStatOrSkill()
            charGenerator.statInfo(mainWindow)
            charGenerator.skillInfo(mainWindow)

        elif user_input.key in selectorInc or user_input.keychar in selectorInc:
            charGenerator.incrementStatOrSkill()
            charGenerator.statInfo(mainWindow)
            charGenerator.skillInfo(mainWindow)

        elif user_input.key in selectorDeinc or user_input.keychar in selectorDeinc:
            charGenerator.incrementStatOrSkill(True)
            charGenerator.statInfo(mainWindow)
            charGenerator.skillInfo(mainWindow)

        elif user_input.keychar in {'<', '[', '{', '(', ','}:
            charGenerator.toggleSpecies(True)
            charGenerator.speciesInfo(mainWindow)
            charGenerator.genderInfo(mainWindow)
            charGenerator.appearinceInfo(mainWindow)

        elif user_input.keychar in {'>', ']', '}', ')', '.'}:
            charGenerator.toggleSpecies(False)
            charGenerator.speciesInfo(mainWindow)
            charGenerator.genderInfo(mainWindow)
            charGenerator.appearinceInfo(mainWindow)

        elif user_input.keychar in {'\\', '/', '|'}:
            charGenerator.toggleGender()
            charGenerator.genderInfo(mainWindow)

        elif user_input.keychar == 'r':
            charGenerator.reRollColors()
            charGenerator.appearinceInfo(mainWindow)

        else:
            redraw = False

        if redraw:
            tdl.flush()

        if user_input.key in {'ENTER', 'KPENTER'}:
            if charGenerator.isReady:

                blank_main_screen(vDict)
                charGenerator.buyItems = True
                charGenerator.ajustForChosenSpecies()
                charGenerator.clearItems(mainWindow)

        # if charGenerator.isReady and user_input.key in {'ENTER', 'KPENTER'}:
        #   charGenerator.clearItems(mainWindow)

    else:
        redraw = True
        if user_input.key in selectorUp or user_input.keychar in selectorUp:
            charGenerator.cycleThruItems()
            charGenerator.infoBuyItems(mainWindow)
        elif user_input.key in selectorDown or user_input.keychar in selectorDown:
            charGenerator.cycleThruItems(True)
            charGenerator.infoBuyItems(mainWindow)
        elif user_input.key == 'SPACE':
            charGenerator.buySelectedItem()
            charGenerator.infoBuyItems(mainWindow)
            charGenerator.infoBoughtItems(mainWindow)
        elif user_input.keychar == 'c':
            charGenerator.clearItems(mainWindow)


        else:
            redraw = False

        if redraw:
            tdl.flush()

        if user_input.key in {'ENTER', 'KPENTER'}:
            blank_main_screen(vDict)
            return True

# gameplay related functions:


def redraw_status_window(vDict):
    """Redraws the status window based on the player's information, such as health, stamna,
mana, food, and stats."""
    player = vDict['gameLevel'].player

    windowDict = vDict['windowDict']
    statusWindow = windowDict['statusWindow']

    blankInvenText = vDict['blankInvenText']

    halfBlankInvenText = vDict['halfBlankInvenText']

    y = 1

    for i in ('Species: {0.species.name}', 'Health: {0.health.amount}/{0.maxHealth}',
              'Stamna: {0.stamna.amount}/{0.maxStamna}', '{0.magic.amount}/{0.maxMagic}',
              '{0.describeHunger}'):
        statusWindow.draw_str(
            1, y, halfBlankInvenText.format(
                i.format(player)
            ))

        y += 1

    y = 1

    halfWidth = statusWindow.width // 2

    for i, s in zip(('STR', 'END', 'AGI', 'DEX', 'MIN', 'WIL', 'PER', 'MAG'), ALL_STATS):
        statusWindow.draw_str(halfWidth, y, halfBlankInvenText.format('{}: {}'.format(i, player.getTotalStat(s))))

        y += 1

    tdl.flush()


# screen centering
def alternateCenterScreen(vDict):
    """An alternate (and unused) functon for centering the screen on the player."""
    gameLevel = vDict['gameLevel']

    screenOffset = vDict['screenOffset']

    newOffsetX = vDict['screenOffset'].x
    newOffsetY = vDict['screenOffset'].y

    quarterWidth = vDict['SCREEN_WIDTH'] // 4
    quarterHeight = vDict['SCREEN_HEIGHT'] // 4

    if gameLevel.player.co.x - screenOffset.x < quarterWidth:
        newOffsetX += quarterWidth
    elif gameLevel.player.co.x - screenOffset.x >= quarterWidth * 3:
        newOffsetX -= quarterWidth
    if gameLevel.player.co.y - screenOffset.y < quarterHeight:
        newOffsetY += quarterHeight
    elif gameLevel.player.co.y - screenOffset.y >= quarterHeight * 3:
        newOffsetY -= quarterHeight

    if newOffsetX < 0:
        newOffsetX = 0
    elif newOffsetX >= gameLevel.size - vDict['SCREEN_WIDTH'] // 2:
        newOffsetX = (gameLevel.size - vDict['SCREEN_WIDTH'] // 2) - 1
    if newOffsetY < 0:
        newOffsetY = 0
    elif newOffsetY >= gameLevel.size - vDict['SCREEN_HEIGHT'] // 2:
        newOffsetY = (gameLevel.size - vDict['SCREEN_HEIGHT'] // 2) - 1
    '''
    assume that player location is 132, the screen width is 60, and the current offset is 30
    the new offset needs to be less then the player location, but greater then the player location - screen width

    half offset = screen width // 2
    30 = 60 // 2

    number of screen widths = player location // screen width
    2 = 132 // 60

    new offset = number of screen widths * screen width
    120 = 2 * 60
    '''


def centerScreenOnPlayer(vDict):
    gameLevel = vDict['gameLevel']

    def determinNewOffset(playerXorY, levelWidthOrHeight, screenWidthOrHeight):
        # test 1:

        # playerXorY = 15
        # levelWidthOrHeight = 60
        # screenWidthOrHeight = 40

        # screenWidthOrHeight // 2 = 20
        # playerXorY < screenWidthOrHeight // 2
        # 15 < 20
        # true
        # return 0

        # test 2:

        # playerXorY = 50
        # playerXorY >= levelWidthOrHeight - (screenWidthOrHeight // 2)
        # 50 >= 60 - 20 = 40
        # true
        # return 60 - 40

        # test 3:
        # playerXorY = 25
        # return 25 - (screenWidthOrHeight // 2)
        # return 25 - 20 = 5

        if playerXorY < screenWidthOrHeight // 2:
            # if player position is close to zero
            return 0
        elif playerXorY >= levelWidthOrHeight - (screenWidthOrHeight // 2):
            # elif player position is close to maximum
            return levelWidthOrHeight - screenWidthOrHeight
        else:
            return playerXorY - (screenWidthOrHeight // 2)

    # modDivide = lambda a, b: round(a / b) * (b + 0)

    # assume that
    # the player x location is 250,
    # the player y location is 125

    # the screen x offset is 100,
    # the screen y offset is 50

    # and the screen width is 80
    # the screen height is 60

    playerLocationX = gameLevel.player.co.x
    playerLocationY = gameLevel.player.co.y

    newOffsetX = determinNewOffset(playerLocationX, gameLevel.widthHeight.x, vDict['SCREEN_WIDTH'])
    newOffsetY = determinNewOffset(playerLocationY, gameLevel.widthHeight.y, vDict['SCREEN_HEIGHT'])

    modified = newOffsetX != vDict['screenOffset'].x or newOffsetY != vDict['screenOffset'].y

    if modified:
        vDict['screenOffset'] = Coords(newOffsetX, newOffsetY)

    return modified

def drawItems(vDict):
    """Draws all items that the player can see on the main window. If the player moves out of
    visual range, then the items will still be drawn as long as noone picks it up."""
    gameLevel = vDict['gameLevel']

    # assume e co.x is 75 and e.co.y is 31 and that
    # vDict['screenOffset'].x is 30 and vDict['screenOffset'].y is 30
    #
    drawableItems = list((e for e in gameLevel.itemsOnFloor if e.co.check_if_is_in_range(
        vDict['screenOffset'].x + vDict['SCREEN_WIDTH'],
        vDict['screenOffset'].y + vDict['SCREEN_HEIGHT'],
        vDict['screenOffset'].x,
        vDict['screenOffset'].y
    )))

    for i in drawableItems:
        if i.seen:
            paint_character(vDict, i.getSymbol, i.co.x, i.co.y, BLACK, i.getColor)

        elif gameLevel.checkIfItemOrEntityIsInVisibilityGrid(i):
            i.seen = True
            paint_character(vDict, i.getSymbol, i.co.x, i.co.y, BLACK, i.getColor)


def checkForVisibleItems(vDict):
    gameLevel = vDict['gameLevel']
    player = gameLevel.player
    itemsToCheck = list((i for i in gameLevel.itemsOnFloor if
                         player.co.distance(i.co) <= player.getSightRadius and not
                         gameLevel.checkForObstructionBetweenPoints(player.co, i.co)
                         ))

    for i in itemsToCheck:
        i.seen = True


def drawEntities(vDict, limited: bool=False):
    """Draws all entites visible to the player to the main window."""
    gameLevel = vDict['gameLevel']
    player = gameLevel.player

    entitiesOnScreen = list((e for e in gameLevel.allEntities if e.co.check_if_is_in_range(
        vDict['screenOffset'].x + vDict['SCREEN_WIDTH'],
        vDict['screenOffset'].y + vDict['SCREEN_HEIGHT'],
        vDict['screenOffset'].x,
        vDict['screenOffset'].y
    )))

    drawableEntities = list((e for e in entitiesOnScreen if e is not player and
                             not gameLevel.checkForObstructionBetweenPoints(
                                 player.co, e.co, maxRange=player.getSightRadius)))

    drawableItems = list((i for i in gameLevel.itemsOnFloor if i.co.distance(player.co) <= player.getSightRadius))

    distances = ' '.join([str(player.co.distance(d.co)) for d in drawableEntities])
    positions = ' '.join([str(d.co - player.co) for d in drawableEntities])

    if limited:
        # limited is used if the screen offset did not change
        prevousLocations = list((el.co + el.behavour_ai.move_direction for el in drawableEntities if
                                 el.behavour_ai.move_direction != DIR_CENTER))

        setOfLocations = set(prevousLocations) - set((e.co for e in drawableEntities))

        setOfItemLocations = setOfLocations & set((i.co for i in drawableItems))

        setOfEmptyLocations = setOfLocations - setOfItemLocations

        itemsToDraw = list((i for i in drawableItems if i.co in list(setOfItemLocations)))

        for it in itemsToDraw:
            paint_character(vDict, it.getSymbol, it.co.x, it.co.y, BLACK, it.checkEquipColor(player))

        for bs in list(setOfEmptyLocations):

            s, fg, bg = gameLevel.getTileChar(bs.x, bs.y)

            paint_character(vDict, s, bs.x, bs.y, bg, fg)

    for e in drawableEntities:
        paint_character(vDict, e.getSymbol, e.co.x, e.co.y, BLACK, list(e.getColor))

    #paintCharacter(vDict, '@', player.co.x, player.co.y, BLACK, WHITE)


# inventory commands
def _draw_equipment(vDict):
    windowDict = vDict['windowDict']
    invenWindow = windowDict['invenWindow']

    blankInvenText = vDict['blankInvenText']

    player = vDict['gameLevel'].player

    def check_and_generate(check_these, print_these):

        for c, p in zip(check_these, print_these):
            if c is not None and c.isValidItem:
                yield (p, WHITE)
                yield (c.fullName, c.checkEquipColor(player))

    equip = list(
        check_and_generate(
            [player.wornDict['HEAD'], player.wornDict['UPPER_BOD'], player.wornDict['HANDS'],
             player.wornDict['LOWER_BOD'], player.wornDict['FEET'], player.handItem, player.offHandItem,
             player.swapHandItem, player.swapOffHandItem, player.quiver],
            ['Wearing on head:', 'Wearing on torso:', 'Wearing on hands:', 'Wearing on feet:',
             'Weilding with main hand:', 'Weilding with off hand:' 'Reserve main hand:', 'Reserve off hand:',
             'In quiver:']
        )
    )

    misc = player.miscItems

    if len(misc) > 0:
        miscText = [('Misc items:', WHITE)]
        miscText += list((m.fullName, m.checkEquipColor(player)) for m in misc if m is not None and m.isValidItem)
        equip += miscText

    y = 1

    for e in equip:
        invenWindow.draw_str(1, y, blankInvenText.format(e[0], fg=e[1]))
        y += 1

    be = blankInvenText.format(' ')

    for i in range(y, vDict['SCREEN_HEIGHT']):

        invenWindow.draw_str(1, i, be)

    tdl.flush()


def _draw_inventory(vDict):
    """Draws the players inventory to the inventory screen"""

    windowDict = vDict['windowDict']
    invenWindow = windowDict['invenWindow']

    blankInvenText = vDict['blankInvenText']

    player = vDict['gameLevel'].player

    inven = player.inventory

    invenText = [('Inventory:', WHITE)]
    invenText += list((i.fullName, i.checkEquipColor(player)) for i in inven if i is not None and i.isValidItem)

    y = 1

    for i in invenText:
        invenWindow.draw_str(1, y, blankInvenText.format(i[0]), fg=tuple(i[1]))
        y += 1

    tdl.flush()


def _draw_abilities(vDict):
    """Draws the players inate abilities and known grime to the inventory screen"""
    windowDict = vDict['windowDict']
    invenWindow = windowDict['invenWindow']

    blankInvenText = vDict['blankInvenText']

    player = vDict['gameLevel'].player

    y = 1

    innate_abilities = player.species.innateAbilites

    abil_text = []

    check_color = lambda c, co1, co2: co1 if c else co2

    if len(innate_abilities) > 0:
        abil_text += [('Inate abilities:', WHITE)]
        abil_text += [(str(a), check_color(player.canUsePower(a), WHITE, PURPLE)) for a in innate_abilities]

    grimore = player.grimore

    if len(grimore) > 0:
        abil_text += [('Grimore:', WHITE)]
        abil_text += [(str(a), check_color(player.canUsePower(a), WHITE, PURPLE)) for a in grimore]

    for a in abil_text:
        invenWindow.draw_str(1, y, blankInvenText.format(blankInvenText.format(a[0])), a[1])

    tdl.flush()


redraw_dict = {
    'INVENTORY': _draw_inventory,
    'EQUIPMENT': _draw_equipment,
    'ABILITIES': _draw_abilities
}


def redraw_inventory(vDict):
    """Draws the player's inventory window depending on weither their equipment, inventory, or abilities are
    selected."""
    blankInvenText = vDict['blankInvenText']
    gameLevel = vDict['gameLevel']
    wDict = vDict['windowDict']
    invenWindow = wDict['invenWindow']

    inventory_display_type = vDict['inventory_display_type']

    y = 1

    redraw_dict[inventory_display_type](vDict)
    vDict['need_to_update_item_view'] = False

    """
    if vDict['showEquipment']:
        equ = gameLevel.player.printEquipment()
        for e in equ:
            # forg = gameLevel.player.getItemColorToDisplay(e)
            invenWindow.draw_str(1, y, blankInvenText.format(e), bg=BLACK, fg=WHITE)
            y += 2
    else:
        inv, col = gameLevel.player.printInventory()

        for i, c in zip(inv, col):
            # forg = gameLevel.player.getItemColorToDisplay(i)
            try:
                invenWindow.draw_str(1, y, blankInvenText.format(i), bg=BLACK, fg=tuple(c))
            except TypeError:
                print('Type Error')
                print(type(c))
                print(c)
                print(i.fullName)
                pass
            y += 1

    for r in range(y, vDict['SCREEN_HEIGHT']):
        invenWindow.draw_str(1, r, blankInvenText.format(' '))
    """

def _handle_inventory_window(vDict, item_dict):

    windowDict = vDict['windowDict']

    invenWindow = windowDict['invenWindow']
    gameLevel = vDict['gameLevel']
    blankInvenText = vDict['blankInvenText']

    be = blankInvenText.format(' ')

    y = 1

    player = gameLevel.player

    for i in item_dict.items():

        k, v = i

        text = blankInvenText.format(
            '{}, {}'.format(k, v.fullName)
        )

        fg = tuple(v.checkEquipColor(player))

        invenWindow.draw_str(1, y, text, fg=fg)

        y += 1

    for i in range(y, vDict['SCREEN_HEIGHT']):

        invenWindow.draw_str(1, i, be)

    tdl.flush()

    return item_dict


def equip_item(vDict):

    gameLevel = vDict['gameLevel']

    player = gameLevel.player

    if len(player.inventory) > 0:
        # WIELDABLE
        equipable_items = [e for e in player.inventory if check_if_entity_can_use_equip_item(player, e)]

        if len(equipable_items) == 1:
            player.behavour_ai.nextAction = 'EQUIP_ITEM'
            player.behavour_ai.itemToUse = equipable_items[0]

            vDict['turnPassed'] = True
            return True

        elif len(equipable_items) > 1:

            char_item_dict = player.generate_char_item_dict(gameLevel, inventory=True, only_equipable=True)

            items = _handle_inventory_window(
                vDict, char_item_dict)

            last_key = list(items.keys())[-1]

            add_to_events_to_draw(vDict, 'Equip which item (a - {})?'.format(last_key))
            tdl.flush()

            # tdl.event.get()
            # q = tdl.event.get()
            # problem here: tdl.event.get() dosnet flust the

            user_input = tdl.event.key_wait()

            # this is a temp hack

            user_input.keychar = 'a'

            if user_input.keychar in items:

                ite = items[user_input.keychar]

                player.behavour_ai.nextAction = 'EQUIP_ITEM'
                player.behavour_ai.itemToUse = ite

                vDict['turnPassed'] = True
                return True
            else:
                add_to_events_to_draw(vDict, 'Canceled.')
                return False
        else:
            add_to_events_to_draw(vDict, 'You have nothing to equip.')
    else:
        add_to_events_to_draw(vDict, 'You have nothing to equip.')


def remove_item(vDict):

    gameLevel = vDict['gameLevel']

    player = gameLevel.player

    equip = _handle_inventory_window(
        vDict, player.generate_char_item_dict(gameLevel, equiped_items=True))

    if len(equip) == 1:
        player.behavour_ai.nextAction = 'REMOVE_ITEM'
        player.behavour_ai.itemToUse = equip['a']
        vDict['turnPassed'] = True
        vDict['inventory_display_type'] = 'EQUIPMENT'
        vDict['need_to_update_item_view'] = True

        return True

    elif len(equip) > 1:
        last_key = list(equip.keys())[-1]
        add_to_events_to_draw(vDict, 'Remove which item (a - {})?'.format(last_key))
        tdl.flush()

        q = tdl.event.get()

        user_input = tdl.event.key_wait()

        # this is a temp hack

        user_input.keychar = 'a'

        if user_input.keychar in equip:
            player.behavour_ai.nextAction = 'REMOVE_ITEM'
            player.behavour_ai.itemToUse = equip[user_input.keychar]
            vDict['turnPassed'] = True
            vDict['inventory_display_type'] = 'EQUIPMENT'
            vDict['need_to_update_item_view'] = True

            return True
        else:
            add_to_events_to_draw(vDict, 'Canceled.')
            return False
    else:
        add_to_events_to_draw(vDict, 'You have no usable items.')
        return False


def pickup(vDict):

    gameLevel = vDict['gameLevel']

    player = gameLevel.player

    items = _handle_inventory_window(vDict,
                                     player.generate_char_item_dict(gameLevel, floor_items=True))

    if len(items) == 1:
        player.behavour_ai.nextAction = 'PICK_UP'
        player.behavour_ai.itemToUse = items['a']
        vDict['turnPassed'] = True
        vDict['inventory_display_type'] = 'INVENTORY'
        vDict['need_to_update_item_view'] = True

        return True

    elif len(items) > 1:
        last_key = list(items.keys())[-1]
        add_to_events_to_draw(vDict, 'Pick up which item (a - {})?'.format(last_key))
        tdl.flush()

        q = tdl.event.get()

        user_input = tdl.event.key_wait()

        if user_input.keychar in items:
            player.behavour_ai.nextAction = 'PICK_UP'
            player.behavour_ai.itemToUse = items[user_input.keychar]
            vDict['turnPassed'] = True
            vDict['inventory_display_type'] = 'INVENTORY'
            vDict['need_to_update_item_view'] = True

            return True
        else:
            add_to_events_to_draw(vDict, 'Canceled.')
            return False

    else:
        add_to_events_to_draw(vDict, 'There are no objects below you.')
        return False


def drop(vDict):
    gameLevel = vDict['gameLevel']

    player = gameLevel.player

    items = _handle_inventory_window(vDict,
                                     player.generate_char_item_dict(gameLevel, equiped_items=True, inventory=True))

    if len(items) == 1:
        player.behavour_ai.nextAction = 'DROP_ITEM'
        player.behavour_ai.itemToUse = items['a']
        vDict['turnPassed'] = True
        vDict['inventory_display_type'] = 'INVENTORY'
        vDict['need_to_update_item_view'] = True
    elif len(items) > 1:
        last_key = list(items.keys())[-1]

        add_to_events_to_draw(vDict, 'Drop which item (a - {})?'.format(last_key))
        tdl.flush()

        q = list(tdl.event.get())

        user_input = tdl.event.key_wait()

        if user_input.keychar in items:
            player.behavour_ai.nextAction = 'DROP_ITEM'
            player.behavour_ai.itemToUse = items[user_input.keychar]
            vDict['turnPassed'] = True
            vDict['inventory_display_type'] = 'INVENTORY'
            vDict['need_to_update_item_view'] = True
            return True
        else:
            add_to_events_to_draw(vDict, 'Canceled.')
            return False
    else:
        add_to_events_to_draw(vDict, 'You have nothing to drop.')

        return False


def throw_item(vDict):
    gameLevel = vDict['gameLevel']

    player = gameLevel.player

    items = _handle_inventory_window(vDict,
                                     player.generate_char_item_dict(gameLevel, equiped_items=True, inventory=True,
                                                                   item_type='WEAPON'))

    if len(items) == 1:
        item_to_use = items['a']
    elif len(items) > 1:
        last_key = list(items.keys())[-1]

        add_to_events_to_draw(vDict, 'Throw which item (a - {})?'.format(last_key))
        tdl.flush()

        q = tdl.event.get()

        user_input = tdl.event.key_wait()

        if user_input.keychar in items:

            cursor = targetCursior(vDict)

            if cursor is None:
                add_to_events_to_draw(vDict, 'Canceled.')
                return False

            player.behavour_ai.itemToUse = items[user_input.keychar]
            player.behavour_ai.rangedTargetCo = cursor
            player.behavour_ai.nextAction = 'RANGED_ITEM'
            vDict['turnPassed'] = True
            vDict['inventory_display_type'] = 'INVENTORY'
            vDict['need_to_update_item_view'] = True
            return True

        else:
            add_to_events_to_draw(vDict, 'Canceled.')
            return False
    else:
        add_to_events_to_draw(vDict, 'You have no items that can be thrown.')

        return False


def use_item(vDict):
    gameLevel = vDict['gameLevel']

    player = gameLevel.player

    items = _handle_inventory_window(vDict,
                                     player.generate_char_item_dict(gameLevel, equiped_items=True, inventory=True,
                                                                   only_useable=True))
    if len(items) == 1:
        item_to_use = items['a']
    elif len(items) > 1:
        last_key = list(items.keys())[-1]

        add_to_events_to_draw(vDict, 'Use which item (a - {})?'.format(last_key))
        tdl.flush()

        q = tdl.event.get()

        user_input = tdl.event.key_wait()

        if user_input.keychar in items:

            item_to_use = items[user_input.keychar]
        else:
            add_to_events_to_draw(vDict, 'Canceled.')
            return False
    else:
        add_to_events_to_draw(vDict, 'You have no usable items.')

        return False

    effect = item_to_use.getEffect

    if effect.requires_targeting:
        add_to_events_to_draw(vDict, 'Which position?')

        cursor = targetCursior(vDict)

        if cursor is None:
            add_to_events_to_draw(vDict, 'Canceled.')
            return False
        else:
            player.behavour_ai.nextAction = 'USE_ITEM'
            player.behavour_ai.itemToUse = item_to_use
            player.behavour_ai.rangedTargetCo = cursor
            vDict['turnPassed'] = True
            vDict['inventory_display_type'] = 'INVENTORY'
            vDict['need_to_update_item_view'] = True

            return True
    else:
        player.behavour_ai.nextAction = 'USE_ITEM'

        player.behavour_ai.itemToUse = item_to_use
        vDict['turnPassed'] = True
        vDict['inventory_display_type'] = 'INVENTORY'
        vDict['need_to_update_item_view'] = True


def use_ability(vDict):
    gameLevel = vDict['gameLevel']

    player = gameLevel.player

    items = _handle_inventory_window(
        vDict, player.generate_char_ability_dict(gameLevel, ability=True, grimore=True, only_useable=True))

    if len(items) == 1:
        item_to_use = items['a']
    elif len(items) > 1:
        last_key = list(items.keys())[-1]
        add_to_events_to_draw(vDict, 'Use which ability (a - {})?'.format(last_key))
        tdl.flush()

        q = tdl.event.get()

        user_input = tdl.event.key_wait()

        if user_input.keychar in items:

            item_to_use = items[user_input.keychar]

            if item_to_use.requires_targeting:
                add_to_events_to_draw(vDict, 'Which position?')

                cursor = targetCursior(vDict)

                if cursor is None:
                    add_to_events_to_draw(vDict, 'Canceled.')
                    return False
                else:
                    player.behavour_ai.nextAction = 'RANGED_EFFECT'
                    player.behavour_ai.rangedTargetCo = cursor
                    player.behavour_ai.itemToUse = item_to_use
                    vDict['turnPassed'] = True
                    vDict['inventory_display_type'] = 'ABILITIES'
                    vDict['need_to_update_item_view'] = True
                    return True


def stairs_down(vDict):
    gameLevel = vDict['gameLevel']
    player = gameLevel.player
    if gameLevel.grid[player.co.y][player.co.x].isDownstairs:
        player.behavour_ai.nextAction = 'STAIRS_DOWN'
        vDict['turnPassed'] = True

    else:
        add_to_events_to_draw(vDict, 'There are no down stair here.')


def stair_up(vDict):

    gameLevel = vDict['gameLevel']
    player = gameLevel.player

    if gameLevel.grid[player.co.y][player.co.x].isUpstairs:
        player.behavour_ai.nextAction = 'STAIRS_UP'
        vDict['turnPassed'] = True

    else:
        add_to_events_to_draw(vDict, 'There are no up stair here.')


def ranged_attack(vDict):

    gameLevel = vDict['gameLevel']

    player = gameLevel.player

    if not player.can_make_ranged_attack:
        add_to_events_to_draw(vDict, 'You are not carrying a launcher and/or enough amnunition, or your amnunition is'
                                     'not the right kind for your launcher.')
        return False

    add_to_events_to_draw(vDict, 'Shoot at which tile?')

    cursor = targetCursior(vDict)

    if cursor is None:
        add_to_events_to_draw(vDict, 'Canceled.')
        return False
    else:
        player.behavour_ai.rangedTargetCo = cursor
        player.behavour_ai.nextAction = 'RANGED_ATTACK'


def swap_equipment(vDict):

    vDict['gameLevel'].player.behavour_ai.nextAction = 'SWAP'
    vDict['turnPassed'] = True
    vDict['inventory_display_type'] = 'EQUIPMENT'
    vDict['need_to_update_item_view'] = True


def toggle_inventory(vDict):
    if vDict['inventory_display_type'] == 'EQUIPMENT':
        vDict['inventory_display_type'] = 'INVENTORY'
    elif vDict['inventory_display_type'] == 'INVENTORY':
        vDict['inventory_display_type'] = 'ABILITIES'
    else:
        vDict['inventory_display_type'] = 'EQUIPMENT'

    vDict['need_to_update_item_view'] = True

def handle_keys(vDict):
    gameLevel = vDict['gameLevel']
    # wDict = vDict['windowDict']
    player = gameLevel.player

    directionDict = vDict['directionDict']

    # q = list(tdl.event.get())

    user_input = tdl.event.key_wait()

    # movement keys
    if user_input.key in directionDict or user_input.keychar in directionDict:
        try:
            dir = directionDict[user_input.key]
        except KeyError:
            dir = directionDict[user_input.keychar]

        old_move = player.behavour_ai.move_direction

        if dir == DIR_CENTER:
            vDict['turnPassed'] = True
            player.behavour_ai.move_direction = dir
            player.behavour_ai.nextAction = 'MOVE'
        else:

            resultMove = player.canMoveToCoord(dir, gameLevel)
            if resultMove != DIR_CENTER:
                player.behavour_ai.move_direction = resultMove
                player.behavour_ai.nextAction = 'MOVE'

                vDict['runInDirection'] = user_input.shift

                vDict['turnPassed'] = True

            else:
                add_to_events_to_draw(vDict, 'There\'s a wall in the way.')

    elif user_input.keychar == '=':

        targetCursior(vDict)

    elif user_input.key == 'ENTER' and user_input.alt:
        # Alt+Enter: toggle fullscreen
        tdl.set_fullscreen(not tdl.get_fullscreen())

    elif user_input.key == 'ESCAPE':
        vDict['exit_game'] = True
        # return True  #exit game
    else:
        action_dict = vDict['action_dict']
        if user_input.keychar in action_dict:
            action_dict[user_input.keychar](vDict)


def implement_actions(vDict, addToEvents):
    gameLevel = vDict['gameLevel']

    entities = gameLevel.allEntities

    ranged_entities = list((e for e in entities if e.behavour_ai.nextAction in {
        'RANGED_ATTACK', 'MEELE_EFFECT', 'RANGED_EFFECT', 'RANGED_ITEM'}))

    for e in ranged_entities:
        e.take_action(vDict, addToEvents)

    move_entities = list((e for e in entities if e.is_a_valid_target and e.behavour_ai.nextAction == 'MOVE'))

    for e in move_entities:
        e.take_action(vDict, addToEvents)

    self_entities = list((e for e in entities if e.is_a_valid_target and e.behavour_ai.nextAction in {'SELF_EFFECT', 'SELF_ITEM'}))

    for e in self_entities:
        e.take_action(vDict, addToEvents)

    equip_entities = list((e for e in entities if e.behavour_ai.nextAction in {'PICK_UP',
             'EQUIP_ITEM', 'REMOVE_ITEM', 'SWAP', 'DROP_ITEM'}))

    for e in equip_entities:
        e.take_action(vDict, addToEvents)

    stairs_entities = list((e for e in entities if e.behavour_ai.nextAction in {'STAIRS_UP', 'STAIRS_DOWN', 'REST'}))

    for e in stairs_entities:
        e.take_action(vDict, addToEvents)

    gameLevel.allEntities = [e for e in gameLevel.allEntities if e.is_a_valid_target]


def can_run_in_direction(vDict):
    """Runs a serise of checks to see if the player can "run" in a direction. First it checks to see if the grid tile
    in front of the player can be moved through.

    there are any
    other enties in the player's sight. Then it checks to see if FInaly, it checks if any the 9 * 9 grid of tiles ajacent to the player is different then the 9 * 9 grid
    ajacent to the players' next position. If any of those three checks are failed, then vDict['runInDirection'] is set
    to False."""

    if not vDict['runInDirection']:
        return False

    player_coords = vDict['gameLevel'].player.co

    level = vDict['gameLevel']

    player = level.player

    player_coords = player.co

    new_coords = player_coords + player.ai.move_direction

    if not level.grid[new_coords.y][new_coords.x].moveThru:
        vDict['runInDirection'] = False
        return False

    def generateNearbyTiles(co):
        for y in range(co.y - 1, co.y + 1):
            for x in range(co.x - 1, co.x + 1):
                yield level.grid[y][x]

    nearby_tiles = tuple(generateNearbyTiles(player_coords))

    next_tiles = tuple(generateNearbyTiles(new_coords))

    t = nearby_tiles != next_tiles

    if nearby_tiles != next_tiles:
        vDict['runInDirection'] = False
        return False

    entities = list((e for e in level.getEntitesInRange(player, player.getSightRadius, allEntieiesExceptThis=player)))

    if len(entities) > 0:
        for e in entities:
            if level.checkForObstructionBetweenPoints(player.co, e.co, maxRange=player.getSightRadius):

                vDict['runInDirection'] = False
                return False

    old_coords = player_coords - player.move_direction

    ajacent_items_current = set((i for i in level.itemsOnFloor if player_coords.is_adjacent(i.co)))

    ajacent_items_prevous = set((i for i in level.itemsOnFloor if old_coords.is_adjacent(i.co)))

    diffrence = ajacent_items_current - ajacent_items_prevous

    if len(diffrence) > 0:
        vDict['runInDirection'] = False
        return False

    return True

def paint_level_in_area(startX, endX, startY, endY, vDict, distanceLimit=-1):
    gameLevel = vDict['gameLevel']
    playerLocation = gameLevel.player.co
    screenOffset = vDict['screenOffset']

    mainWindow = vDict['windowDict']['mainWindow']

    def drawTile(x, y):
        xPlusOffset = x + screenOffset.x
        yPlusOffset = y + screenOffset.y
        s, f, b = gameLevel.getTileChar(xPlusOffset, yPlusOffset)
        f2 = list(f)
        b2 = list(b)
        mainWindow.draw_char(x, y, s, bg=b2, fg=f2)

    if distanceLimit < 0:
        for y in range(startY, endY):
            for x in range(startX, endX):
                drawTile(x, y)
    else:
        # assume distanceLimit is 20
        # assume that:
        # startX = 0
        # endX = 35
        # startY = 3
        # endY = 43
        for y in range(startY, endY):
            # range(3, 43)
            for x in range(startX, endX):
                # range(0, 35)
                dist = Coords.distance_static(playerLocation.x - screenOffset.x, x, playerLocation.y - screenOffset.y, y)
                if dist <= distanceLimit:
                    drawTile(x, y)
                    #yield gameLevel.visibilityGrid[y][x]

def paint_screen(vDict):
    """Paints all of the level that is visible or has been prevously seen to the main screen."""

    gameLevel = vDict['gameLevel']
    windowDict = vDict['windowDict']
    # mainWindow = windowDict['mainWindow']

    # lookLOS(vDict)
    pX = gameLevel.player.co.x // vDict['SCREEN_WIDTH']
    pY = gameLevel.player.co.y // vDict['SCREEN_HEIGHT']

    paint_level_in_area(0, vDict['SCREEN_WIDTH'], 0, vDict['SCREEN_HEIGHT'], vDict)

def paint_screen_limited(vDict):
    """A limited version of paintScreen that only paints what is in the player's imeadiet sight radius."""
    gameLevel = vDict['gameLevel']

    windowDict = vDict['windowDict']

    mainWindow = windowDict['mainWindow']
    # lookLOS(vDict)

    pX = gameLevel.player.co.x - vDict['screenOffset'].x
    pY = gameLevel.player.co.y - vDict['screenOffset'].y
    # assume that the player position is 15, 53, and the screen offset is 0, 40
    # pX = 15 - 0 = 15
    # pY = 53 - 30 = 23

    sightRad = gameLevel.player.getSightRadius
    # assume that the sight radius is 20

    # assume that SCREEN_WIDTH is 100 and SCREEN_HEIGHT is 80

    paint_level_in_area(
        max(pX - sightRad, 0),
        # max(15, - 20, 0) = 0
        min(pX + sightRad, vDict['SCREEN_WIDTH']),
        # min(15 + 20, 100) = 35
        max(pY - sightRad, 0),
        # max(23 - 20, 0) = 3
        min(pY + sightRad, vDict['SCREEN_HEIGHT']),
        # min(23 + 20, 80) = 43
        vDict,
        gameLevel.player.getSightRadius
        )

def paint_character(vDict, paintChar, x, y, bgcolor=BLACK, fgcolor=WHITE):
    """Paints a character to the screen while adjusting for screen offset"""
    windowDict = vDict['windowDict']

    mainWindow = windowDict['mainWindow']
    if x - vDict['screenOffset'].x in range(vDict['SCREEN_WIDTH']) and y - vDict['screenOffset'].y in range(
            vDict['SCREEN_HEIGHT']):
        b2 = list(bgcolor)
        f2 = list(fgcolor)

        try:
            mainWindow.draw_char(x - vDict['screenOffset'].x, y - vDict['screenOffset'].y, paintChar, bg=b2, fg=f2)
        except TypeError:

            raise IndexError('Major error: b2 type: {}, b2 value: {}, f2 type: {}, f2 value: {}'.format(type(b2), b2,
                                                                                                        type(f2), f2))
            pass
            # mainWindow.draw_char(x - vDict['screenOffset'].x, y - vDict['screenOffset'].y, paintChar, bg=b2, fg=f2)


def targetCursior(vDict):
    playerCo = vDict['gameLevel'].player.co

    cursorCoords = playerCo - vDict['screenOffset']

    directionDict = vDict['directionDict']

    mainWindow = vDict['windowDict']['mainWindow']

    def invert(tup):
        r, b, g = tup
        return 255 - r, 255 - g, 255 - b

    s, fg, bg = mainWindow.get_char(cursorCoords.x, cursorCoords.y)

    mainWindow.draw_char(cursorCoords.x, cursorCoords.y, s, bg=invert(bg), fg=invert(fg))
    tdl.flush()

    # invert the current cursor location

    breakLoop = False

    while not breakLoop:

        q = tdl.event.get()

        user_input = tdl.event.key_wait()

        if user_input.key in directionDict or user_input.keychar in directionDict:
            try:
                dir = directionDict[user_input.key]
            except KeyError:
                dir = directionDict[user_input.keychar]
            if dir != DIR_CENTER:

                oldPosition = cursorCoords

                # mainWindow.draw_char(oldPosition.x, oldPosition.y, s, bg=invert(bg), fg=invert(fg))
                mainWindow.draw_char(oldPosition.x, oldPosition.y, s, bg=bg, fg=fg)

                cursorCoords += dir

                s, fg, bg = mainWindow.get_char(cursorCoords.x, cursorCoords.y)

                mainWindow.draw_char(cursorCoords.x, cursorCoords.y, s, bg=invert(bg), fg=invert(fg))
                # mainWindow.draw_char(cursorCoords.x, cursorCoords.y, s, bg=bg, fg=fg)


                tdl.flush()
        elif user_input.key in {'ENTER', 'KPENTER'}:
            # mainWindow.draw_char(cursorCoords.x, cursorCoords.y, s, bg=invert(bg), fg=invert(fg))
            mainWindow.draw_char(cursorCoords.x, cursorCoords.y, s, bg=bg, fg=fg)

            tdl.flush()

            return cursorCoords + vDict['screenOffset']
        elif user_input.key == 'ESCAPE':
            mainWindow.draw_char(cursorCoords.x, cursorCoords.y, s, bg=bg, fg=fg)
            tdl.flush()
            return None


def animate_bolt(vDict, start_co, end_co, max_range):

    timeDelay = vDict['timeDelay']

    gameLevel = vDict['gameLevel']

    windowDict = vDict['windowDict']

    mainWindow = windowDict['mainWindow']

    co_list = gameLevel._Level__generateCoords(start_co, end_co, None, max_range)

    last_position = co_list[0]

    last_ajusted_co = last_position - vDict['screenOffset']

    last_tile, last_fg, last_bg = mainWindow.get_char(last_ajusted_co.x, last_ajusted_co.y)

    mainWindow.draw_char(last_ajusted_co.x, last_ajusted_co.y, '*')
    tdl.flush()

    time.sleep(timeDelay)

    for cn in range(1, len(co_list)):
        # resets the prevous tile
        mainWindow.draw_char(last_ajusted_co.x, last_ajusted_co.y, last_tile, fg=last_fg, bg=last_bg)

        # updates the prevous tile
        last_position = co_list[cn]
        last_ajusted_co = last_position - vDict['screenOffset']
        last_tile, last_fg, last_bg = mainWindow.get_char(last_ajusted_co.x, last_ajusted_co.y)

        # paints the current tile
        mainWindow.draw_char(last_ajusted_co.x, last_ajusted_co.y, '*')
        tdl.flush()
        time.sleep(timeDelay)

    mainWindow.draw_char(last_ajusted_co.x, last_ajusted_co.y, last_tile, fg=last_fg, bg=last_bg)
    tdl.flush()
    time.sleep(timeDelay)


def animate_blast(vDict, target_co, max_range):

    timeDelay = vDict['timeDelay']

    gameLevel = vDict['gameLevel']

    windowDict = vDict['windowDict']

    mainWindow = windowDict['mainWindow']

