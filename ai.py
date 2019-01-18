from collections import deque, Counter
from magic_effects import ALL_SPELLS_DICT, DUMMY_EFFECT, MagicEffect
from data_globals import ARMOR_SET, check_if_entity_can_wear_armor
from random import choices
from coords import Coords, NO_CENTER, DIR_CENTER, rotate_point

BEHAVOURS = ('MOVE', 'RANGED_ATTACK', 'SELF_EFFECT', 'RANGED_EFFECT', 'MELEE_EFFECT', 'SELF_ITEM', 'RANGED_ITEM',
             'PICK_UP',
             'EQUIP_ITEM', 'REMOVE_ITEM', 'SWAP', 'DROP_ITEM',
             'STAIRS_UP', 'STAIRS_DOWN', 'REST')

HUNT_BEHAVOUR = ('CAN_SEE', 'CHAISE', 'WAY_POINT', 'NO_TARGET')


def check_if_key_is_in_counter(dictionary: Counter, key, value: int):
    if key in dictionary:
        dictionary[key] += value
    else:
        dictionary[key] = value


def assignCulmativeWeights(values):
    t = 0
    for v in values:
        yield v + t
        t += v


def _move_no_target(ai, gl, entity):
    if len(ai.nearby_entities) > 0:

        ai.target = ai.nearby_entities[0]

        ai.tracking_type = 'CHAISE'

        ai.move_direction = (entity.co - ai.target.co).normalize(new_tuple=False)
    else:
        # no nearbye enemies

        if ai.destinationCo == entity.co or ai.destinationCo is None:
            # have we arrive at our destination?
            ai.findRandomDestination(gl, entity)

            ai.tracking_type = 'NO_TARGET'
            ai.move_direction = (entity.co - ai.destinationCo).normalize(new_tuple=False)

def _move_can_see(ai, gl, entity):
    if ai.nearby_entities[0] != ai.target:
        # is there somthing closer to us then what we're tracking?
        ai.target = ai.nearby_entities[0]

        ai.move_direction = (entity.co - ai.target.co).normalize(new_tuple=False)

    else:

        if gl.getEndPoint(entity, ai.target.co).distance(entity.co) < entity.co.distance(ai.target.co):
            # is there somthing blocking the way to the target?
            ai.tracking_type = 'WAY_POINT'

            ai.last_known_target_co = ai.target.co

            ai.destinationCo = ai.move_around_obstacle(gl, entity)

            if ai.destinationCo is None:
                ai.findRandomDestination(gl, entity)

            ai.move_direction = (entity.co - ai.destinationCo).normalize(new_tuple=False)

        elif entity.co.distance(ai.target.co) < entity.getSightRadius:
            # is our target out of range?

            ai.tracking_type = 'CHAISE'

            ai.destinationCo = ai.target.co

            ai.move_direction = (entity.co - ai.destinationCo).normalize(new_tuple=False)

def _move_way_point(ai, gl, entity):
    if len(ai.nearby_entities) > 0:
        ai.target = ai.nearby_entities[0]
        ai.tracking_type = 'CAN_SEE'
        ai.move_direction = (entity.co - ai.target.co).normalize(new_tuple=False)

    elif ai.destinationCo == entity.co:
        # have we arrive at the waypoint yet?
        ai.tracking_type = 'CHAISE'

        ai.destinationCo = ai.last_known_target_co

        if gl.getEndPoint(entity, ai.last_known_target_co).distance(entity.co) < entity.co.distance(
                ai.last_known_target_co):
            # is there another blockage between the last known sighting and our cennent position?

            move_around = ai.move_around_obstacle(gl, entity)

            if move_around is not None:
                # can the obstical be moved aroud?
                ai.destinationCo = move_around

                ai.tracking_type = 'WAY_POINT'
                ai.move_direction = (entity.co - ai.destinationCo).normalize(new_tuple=False)

            else:
                ai.findRandomDestination(gl, entity)

                ai.tracking_type = 'NO_TARGET'
                ai.move_direction = (entity.co - ai.destinationCo).normalize(new_tuple=False)

        else:
            # just continue towards our destination
            ai.move_direction = (entity.co - ai.destinationCo).normalize(new_tuple=False)

    else:
        # just continue towards the waypoint
        ai.move_direction = (entity.co - ai.destinationCo).normalize(new_tuple=False)

def _move_chaise(ai, gl, entity):
    if len(ai.nearby_entities) > 0:
        ai.target = ai.nearby_entities[0]
        ai.tracking_type = 'CAN_SEE'

        ai.move_direction = (entity.co - ai.target.co).normalize(new_tuple=False)

    elif entity.co == ai.destinationCo:
        # have we arrived out our destination?

        ai.tracking_type = 'NO_TARGET'

        ai.findRandomDestination(gl, entity)

        ai.move_direction = (entity.co - ai.destinationCo).normalize(new_tuple=False)

    else:
        # just continue towds our destination
        ai.move_direction = (entity.co - ai.destinationCo).normalize(new_tuple=False)

_move_dict = {
    'NO_TARGET': _move_no_target,
    'CAN_SEE': _move_can_see,
    'CHAISE': _move_chaise,
    'WAY_POINT': _move_way_point}

def _move(ai, gl, entity):
    old_tracking_type = ai.tracking_type

    _move_dict[old_tracking_type](ai, gl, entity)


def _ranged_attack(ai, gl, entity):
    ai.rangedTargetCo = ai.target.co
    ai.destinationCo = ai.target.co


def _self_effect(ai, gl, entity):
    healPercent = 1 - (entity.health.amount / entity.maxHealth)

    healthDamage = entity.maxHealth - entity.health.amount

    def check(sub_power, effect):
        return sub_power <= healthDamage and effect.can_use(entity)

    heal_effects = list((e for e in ai.healingEffects if check(sum(e.getAverageSubeffectsPower), e)))

    ai.effectToUse = sorted(heal_effects, key=lambda b: sum(b.getAverageSubeffectsPower))[0]
    """
    oldPower = 0

    for e in ai.healingEffects:
        np = sum(e.getAverageSubeffectsPower)
        if np <= healthDamage and np > oldPower and e.can_use(entity):
            oldPower = np
            ai.effectToUse = e
    """


def _ranged_effect(ai, gl, entity):
    estimated_target_health = round((ai.target.health.amount / ai.target.maxHealth) * ai.target.species.maxHealth)

    ranged_effects = list((e for e in ai.rangedEffects if e.can_use(entity)))

    ai.effectToUse = sorted(ranged_effects, key=lambda b: sum(b.getAverageSubeffectsPower))[0]

    """
    oldPower = 0

    for e in ai.rangedEffects:
        np = sum(e.getAverageSubeffectsPower)
        if np > oldPower and e.can_use(entity):
            oldPower = np
            ai.effectToUse = e
    """


def _self_item(ai, gl, entity):
    healthDamage = entity.maxHealth - entity.health.amount

    oldPower = 0

    usable_items = list((i for i in entity.inventory if i.can_be_used and sum(i.getEffect.getAverageSubeffectsPower) <= healthDamage))

    ai.itemToUse = sorted(usable_items, key=lambda i: sum(i.getEffect.getAverageSubeffectsPower))[0]

    """
    for i in entity.inventory:

        if i.can_be_used:
            e = i.getEffect
            np = sum(e.getAverageSubeffectsPower)
            if np <= healthDamage and np > oldPower:
                oldPower = np
                ai.itemToUse = e
    """


def _ranged_item(ai, gl, entity):
    oldPower = 0

    for i in entity.inventory:

        if i.can_be_used:
            e = i.getEffect
            np = sum(e.getAverageSubeffectsPower)
            if np > oldPower:
                oldPower = np
                ai.itemToUse = e


def _pick_up(ai, gl, entity):

    items = ai.check_if_item_is_worth_picking_up(gl, entity)
    items = sorted(items, key=lambda i: i.getValue)

    ai.itemToUse = items[0]


def _equip_item(ai, gl, entity):
    pass


def _stairs_up(ai, gl, entity):
    pass


def _rest(ai, gl, entity):
    ai.move_direction = DIR_CENTER


class AI:

    action_dict = {
        'MOVE': _move,
        'RANGED_ATTACK': _ranged_attack,
        'SELF_EFFECT': _self_effect,
        'RANGED_EFFECT': _ranged_effect,
        'SELF_ITEM': _self_item,
        'RANGED_ITEM': _ranged_item,
        'MELEE_EFFECT': _ranged_effect,
        'PICK_UP': _pick_up,
        'EQUIP_ITEM': _equip_item,
        'REMOVE_ITEM': _equip_item,

        'SWAP': _equip_item,
        'STAIRS_UP': _stairs_up,
        'STAIRS_DOWN': _stairs_up,
        'REST': _rest
    }

    def add_effect_to_ai(self, effect: MagicEffect):
        if effect.effectTarget == 'SELF':
            self.healingEffects.append(effect)
        elif effect.effectTarget == 'MEELE':
            self.meeleEffects.append(effect)
        else:
            self.rangedEffects.append(effect)

    def __init__(self, entity):

        aa = list(entity.grimore) + list(entity.species.innateAbilites)

        aa_set = set(aa)

        all_spells_len = len(ALL_SPELLS_DICT)

        inate_abilities_len = len(entity.species.innateAbilites)

        all_abilities = deque(aa, all_spells_len + inate_abilities_len)

        all_avaliable_effects = list(ALL_SPELLS_DICT.values()) + list(entity.species.innateAbilites)

        # deque_length = all_spells_len + inate_abilities_len

        all_ranged_effects = [e for e in all_avaliable_effects if e.effectTarget not in {'SELF', 'MEELE'}]

        self.rangedEffects = deque([e for e in all_ranged_effects if e in aa_set], len(all_ranged_effects))

        all_healing_effects = [e for e in all_avaliable_effects if e.effectTarget == 'SELF']

        self.healingEffects = deque([e for e in all_healing_effects if e in aa_set], len(all_healing_effects))

        all_meele_effects = [e for e in all_abilities if e.effectTarget == 'MEELE']

        self.meeleEffects = deque([e for e in all_meele_effects if e in aa_set], len(all_meele_effects))

        self.nextAction = 'MOVE'

        self.tracking_type = 'NO_TARGET'

        self.target = None

        self.last_known_target_co = None

        self.effectToUse = DUMMY_EFFECT

        self.itemToUse = None

        self.item_to_affect = None

        self.destinationCo = entity.co

        self.rangedTargetCo = None

        self.move_direction = DIR_CENTER

        self.nearby_entities = []

    def regenerate(self, entity):

        aa = list(entity.grimore) + list(entity.species.innateAbilites)

        aa_set = set(aa)

        all_abilities = deque(aa, len(ALL_SPELLS_DICT) + len(entity.species.innateAbilites))

        all_avaliable_effects = list(ALL_SPELLS_DICT.values()) + list(entity.species.innateAbilites)

        # deque_length = len(ALL_SPELLS_DICT) + len(entity.species.innateAbilites)

        all_ranged_effects = [e for e in all_avaliable_effects if e.effectTarget not in {'SELF', 'MEELE'}]

        self.rangedEffects = deque([e for e in all_ranged_effects if e in aa_set], len(all_ranged_effects))

        all_healing_effects = [e for e in all_avaliable_effects if e.effectTarget == 'SELF']

        self.healingEffects = deque([e for e in all_healing_effects if e in aa_set], len(all_healing_effects))

        all_meele_effects = [e for e in all_abilities if e.effectTarget == 'MEELE']

        self.meeleEffects = deque([e for e in all_meele_effects if e in aa_set], len(all_meele_effects))

        self.nextAction = 'MOVE'

        self.tracking_type = 'NO_TARGET'

        self.target = None

        self.last_known_target_co = None

        self.effectToUse = DUMMY_EFFECT

        self.itemToUse = None

        self.item_to_affect = None

        self.destinationCo = entity.co

        self.rangedTargetCo = None

        self.move_direction = DIR_CENTER

        self.nearby_entities = []

    """
    def __del__(self):
        self.rangedEffects = []
        self.healingEffects = []
        self.meeleEffects = []
    """

    def get_usable_meele_effects(self, entity):
        return list((e for e in self.meeleEffects if entity.canUsePower(e)))

    def get_usable_ranged_effects(self, entity):
        return list((e for e in self.rangedEffects if entity.canUsePower(e)))

    def get_usable_healing_effects(self, entity):
        return list((e for e in self.healingEffects if entity.canUsePower(e)))

    def findRandomDestination(self, gl, entity):

        destinations = self.findValidMovementDirections(gl, entity)

        # d0 = gl.getEndPoint(entity, destinations[0] * 10 + entity.co, 10)
        # d1 = gl.getEndPoint(entity, destinations[1] * 10 + entity.co, 10)
        # d2 = gl.getEndPoint(entity, destinations[2] * 10 + entity.co, 10)

        dest = [gl.getEndPoint(entity, destinations[d] * 10 + entity.co, 10) for d in range(len(destinations))]

        self.destinationCo = sorted(dest, key=lambda d: d.distance(entity.co))[0]

    def look_for_nearby_enemies(self, gl, entity):

        eInRange1 = [d for d in gl.allEntities if d is not entity and d.is_a_valid_target and entity.co.distance(d.co)
                     <= entity.getSightRadius]

        eInRange = [e for e in eInRange1 if
                    not gl.checkForObstructionBetweenPoints(entity.co, e.co, maxRange=entity.getSightRadius)]

        """
        eInRange = list((e for e in eInRange if entity.co.distance(e.co) <= entity.getSightRadius and
                                         not gl.checkForObstructionBetweenPoints(
                                             entity.co, e.co, maxRange=entity.getSightRadius)))
        """

        eInRange_len = len(eInRange)

        if eInRange_len > 1:
            self.nearby_entities = eInRange
            self.target = sorted(eInRange, key=lambda e: e.co.distance(entity.co), reverse=True)[0]
        elif eInRange_len == 1:
            self.nearby_entities = eInRange
            self.target = eInRange[0]
        else:
            self.nearby_entities = []
            self.target = None

    def check_if_item_is_worth_picking_up(self, gl, entity):

        def check(item):

            if item.baseData.typeOfItem in ARMOR_SET:
                # if not entity.species.canWearArmor(item):

                if not check_if_entity_can_wear_armor(entity, item):
                    return False

            if item.identified:
                if item.egopower < 0:
                    return False

                eff = item.getEffect

                if eff != DUMMY_EFFECT and eff.value < 1:
                    return False

            return True

        return list((e for e in gl.getAllItemsBelowEntity(gl.player) if check(e)))

    @property
    def has_target(self):
        return self.target is not None and self.target.is_a_valid_target

    def move_around_obstacle(self, gl, entity):
        if self.has_target:

            diffrence_co = self.target.co - entity.co

            dist = entity.co.distance(self.target.co)

            coords_to_move_to = []

            for d in range(1, 19):
                r_pos = rotate_point(diffrence_co.x, diffrence_co.y, d * 5.0)
                r_neg = rotate_point(diffrence_co.x, diffrence_co.y, d * -5.0)

                c_pos = entity.co + Coords(r_pos[0], r_pos[1]) * 2
                c_neg = entity.co + Coords(r_neg[0], r_neg[1]) * 2

                c_pos = gl.getEndPoint(entity, c_pos, dist)
                c_neg = gl.getEndPoint(entity, c_neg, dist)

                if entity.co.distance(c_pos) > dist:
                    coords_to_move_to.append(c_pos)
                if entity.co.distance(c_neg) > dist:
                    coords_to_move_to.append(c_neg)

            coords_to_move_to_len = len(coords_to_move_to)

            if coords_to_move_to_len > 1:
                coords_to_move_to = sorted(coords_to_move_to, key=lambda d: d.distance(entity))
                return coords_to_move_to[0]
            elif coords_to_move_to_len == 1:
                return coords_to_move_to[0]
            else:
                return None
        return None

    def decide(self, gl, entity):

        self.look_for_nearby_enemies(gl, entity)

        # behavourCounter = Counter({n: 0 for n in BEHAVOURS})

        behavourCounter = Counter()

        # check_if_key_is_in_counter

        if self.target is not None and not self.target.is_a_valid_target:
            self.target = None

        if self.target is not None:
            assert self.target.co != entity.co

        def check_for_pickup():
            itemsBelow = self.check_if_item_is_worth_picking_up(gl, entity)

            itemsBelow_len = len(itemsBelow)

            if itemsBelow_len > 0:
                # behavourCounter['PICK_UP'] += 75 * len(itemsBelow)
                check_if_key_is_in_counter(behavourCounter, 'PICK_UP', 75 * itemsBelow_len)

        # check ifg entity should retreat

        self_danger = entity.determinDangerLevel

        def generate_danger_points():
            y = 0
            for e in self.nearby_entities:
                yield [y, e.determinThreatLevel * e.determinDangerLevel, e.co]
                y += 1

        other_danger_points = list(generate_danger_points())

        le = len(other_danger_points)

        if le > 0:
            average_danger_level = sum([d[1] for d in other_danger_points]) / le

            retreat_factor = self_danger - average_danger_level

            inverted_retreat_factor = 1 - retreat_factor
        else:
            inverted_retreat_factor = 1

        useable_items = list((i for i in entity.get_useable_items if i.can_be_used and entity.can_use_item(i)))

        damage_taken = entity.maxHealth - entity.health.amount

        healing_items = list((i for i in useable_items if i.getEffect.effectTarget == 'SELF' and sum(i.getEffect.getAverageSubeffectsPower) < damage_taken))

        offensive_items = list((i for i in useable_items if i.getEffect.effectTarget != 'SELF'))

        for e in self.healingEffects:
            magicPower = sum(e.getAverageSubeffectsPower)

            # is e a learned ability?
            if e in entity.grimore:

                if e.can_use(entity):
                    sucessChance = e.calculateSuccessPercent(entity.getSkillPlusBonus('SKILL_SPELLCRAFT'))
                    # ehavourCounter['SELF_EFFECT'] += round(sucessChance * magicPower * inverted_retreat_factor)
                    check_if_key_is_in_counter(behavourCounter, 'SELF_EFFECT', round(sucessChance * magicPower * inverted_retreat_factor))
            else:
                if entity.abilityCooldowns[e] < 1:
                    # behavourCounter['SELF_EFFECT'] += round(magicPower * inverted_retreat_factor)
                    check_if_key_is_in_counter(behavourCounter, 'SELF_EFFECT', round(magicPower * inverted_retreat_factor))

        for i in healing_items:
            magicPower = sum(i.getEffect.getAverageSubeffectsPower)

            sucessChance = i.getEffect.calculateSuccessPercent(entity.getSkillPlusBonus('SKILL_MAGIC_DEVICE'))
            # behavourCounter['SELF_ITEM'] += round(sucessChance * magicPower * inverted_retreat_factor)
            check_if_key_is_in_counter(behavourCounter, 'SELF_ITEM', round(sucessChance * magicPower * inverted_retreat_factor))

        targ_is_player = self.target is not None and self.target.isPlayer

        # if it still dosent have a target
        if self.target is None:
            behavourCounter['MOVE'] = 100
        #if it has a target but theres a wall blocking the way
        elif not gl.checkForObstructionBetweenPoints(entity.co, self.target.co, maxRange=entity.getSightRadius):

            self.move_direction = (self.destinationCo - entity.co).normalize(new_tuple=False)
            # entity.moveDirection = (self.destinationCo - entity.co).normalize(newTuple=False)
            behavourCounter['MOVE'] = 100

        # if its next to the target
        elif entity.co.is_adjacent(self.target):

            self.destinationCo = self.target.co
            self.rangedTargetCo = self.target.co

            self.move_direction = (self.destinationCo - entity.co).normalize(new_tuple=False)

            self.destinationCo = self.target.co
            meeleDamage = entity.getAverageMeeleDamage

            usable_meele_effects = list((e for e in self.get_usable_meele_effects(entity) and sum(e.getAverageSubeffectsPower) > meeleDamage))

            if len(usable_meele_effects) == 1:

                behavourCounter['MELEE_EFFECT'] = sum(usable_meele_effects[0].getAverageSubeffectsPower)
            if len(usable_meele_effects) > 0:

                # behavourCounter['MELEE_EFFECT']+= sum([sum(e.getAverageSubeffectsPower) for e in usable_meele_effects])

                check_if_key_is_in_counter(behavourCounter, 'MELEE_EFFECT', sum(
                    [sum(e.getAverageSubeffectsPower) for e in usable_meele_effects]
                ))

                self.effectToUse = sorted(usable_meele_effects, key=lambda i: sum(i.getAverageSubeffectsPower))[0]

        # if the targets is not next to the entity
        else:
            check_for_pickup()

            if entity.getAverageLauncherDamage > 0 and entity.co.distance(self.target) <= 25:
                # self.rangedTargetCo = self.target.co
                # self.destinationCo = self.target.co

                # behavourCounter['RANGED_ATTACK'] += round(entity.getAverageLauncherDamage - (entity.co.distance(self.target) * 0.5))

                check_if_key_is_in_counter(behavourCounter, 'RANGED_ATTACK', round(
                    entity.getAverageLauncherDamage - (entity.co.distance(self.target) * 0.5)))

                #entity.setBehavour = 'RANGED_ATTACK'
            if len(self.rangedEffects) > 0:

                for e in self.rangedEffects:

                    magicPower = sum(e.getAverageSubeffectsPower)

                    # is e a learned ability?
                    if e in entity.grimore:

                        if e.can_use(entity):
                            sucessChance = e.calculateSuccessPercent(entity.getSkillPlusBonus('SKILL_SPELLCRAFT'))
                            check_if_key_is_in_counter(behavourCounter, 'RANGED_EFFECT', round(sucessChance * magicPower))
                            # behavourCounter['RANGED_EFFECT'] += round(sucessChance * magicPower)
                    else:
                        if entity.abilityCooldowns[e] < 1:
                            # behavourCounter['RANGED_EFFECT'] += round(magicPower)
                            check_if_key_is_in_counter(behavourCounter, 'RANGED_EFFECT', round(magicPower))

            if len(offensive_items) > 0:

                for i in offensive_items:
                    magicPower = sum(i.getEffect.getAverageSubeffectsPower)

                    sucessChance = i.getEffect.calculateSuccessPercent(entity.getSkillPlusBonus('SKILL_MAGIC_DEVICE'))
                    # behavourCounter['RANGED_ITEM'] += round(sucessChance * magicPower * inverted_retreat_factor)
                    check_if_key_is_in_counter(behavourCounter, 'RANGED_ITEM', round(sucessChance * magicPower * inverted_retreat_factor))

        counter_len = len(behavourCounter)

        if counter_len == 1:
            choiceOfAction = behavourCounter.most_common(1)[0]
        else:
            max_choices = min(4, counter_len)

            topChoices = behavourCounter.most_common(max_choices)

            cum_weights = [b[1] for b in topChoices]

            new_cum_weights = list(assignCulmativeWeights(cum_weights))

            choiceOfAction = choices([b[0] for b in topChoices], k=1, cum_weights=new_cum_weights)[0]

        action_name, action_value = choiceOfAction

        if action_name not in BEHAVOURS:
            raise KeyError('the value for choiceOfAction, ({}) is not in the set BEHAVOURS ({})'.format(
                action_name, BEHAVOURS))

        self.action_dict[action_name](self, gl, entity)

    def findValidMovementDirections(self, gl, entity):

        return [m + entity.co for m in NO_CENTER if gl.grid[m.y + entity.co.y][m.x + entity.co.x].moveThru]
