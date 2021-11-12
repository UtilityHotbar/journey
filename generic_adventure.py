import random
import math
from rpgtools import roll, delay_print
import yaml
from yaml import Loader as yamlLoader


class Adv:
    def generic_encounter(self, nodename, options, party):
        return random.choice(options)

    def town(self, options, party):
        delay_print('The party is in town.')
        special = roll('1d12')
        if special == 1:
            delay_print('The party encounters a random event!')
            return 'encounter_town'
        elif special == 6:
            delay_print('A new member joins the party!')
            party.expand(1)
        tavern_vote = len(party.get_wounded_members())
        if tavern_vote > math.ceil(len(party.members)/2):
            delay_print('The party votes to go to a tavern!')
            return 'tavern'
        store_vote = 0
        for member in party.members:
            if member['coin'] > member['armour']*10 or member['coin'] > member['weaponry']*10:
                store_vote += 1
        if store_vote > math.ceil(len(party.members)/2):
            delay_print('The party votes to go shopping!')
            return 'store'
        delay_print('The party, with no particular desires, votes to return to adventuring.')
        return 'wilderness'

    def store(self, options, party):
        delay_print('The party visits a store...')
        for member in party.members:
            if member['fear'] > member['aggression']:
                priorities = ['armour', 'weaponry']
            else:
                priorities = ['weaponry', 'armour']
            for priority in priorities:
                if member['coin'] > member[priority]*10:
                    delay_print(f'{member["name"]} upgrades their {priority}!')
                    member['coin'] -= member[priority]*10
                    member[priority] += 1

    def tavern(self, options, party):
        delay_print('The party departs to a tavern...')
        for member in party.members:
            if member['coin'] > 1:
                delay_print(f'{member["name"]} rests inside!')
                member['coin'] -= 1
                member['hp'] = member['hpmax']
            else:
                delay_print(f'{member["name"]} lacked the funds to enter.')

    def wilderness(self, options, party):
        delay_print('The party is in the wilderness.')
        res = roll('1d6')
        if res == 1:
            delay_print('The party encounters a random event!')
            return 'encounter_travel'
        elif res in [2, 3, 4]:
            delay_print('The party wanders the wilderness...')
            return 'wilderness'
        elif res == 5:
            delay_print('The party encounters a town!')
            return 'town'
        elif res == 6:
            delay_print('The party encounters a dungeon!')
            return 'dungeon'

    def encounter_town(self, options, party):
        run_encounter('town', party)

    def encounter_travel(self, options, party):
        run_encounter('travel', party)

    def encounter_dungeon(self, options, party):
        run_encounter('dungeon', party)

    def dungeon_entrance(self, options, party):
        delay_print('The party enters the dungeon...')

    def dungeon(self, options, party):
        delay_print('The party is in a dungeon.')
        res = roll('1d6')
        if res == 1:
            delay_print('Something shifts in the darkness...')
            return 'encounter_dungeon'
        elif res == 2:
            delay_print('Something seems to be getting closer...')
            return 'spoor'
        elif res == 3:
            delay_print('The dungeon yawns...')
            return 'trap'
        elif res == 4:
            delay_print('The party attempts to explore the dungeon. It threatens to swallow you whole...')
            return 'explore'
        elif res == 5:
            delay_print('The dungeon yields a gleam of hope...')
            return 'reward'
        elif res == 6:
            delay_print('The party makes progress through the dungeon!')
            return 'progress'

    def dungeon_end(self, options, party):
        delay_print('Great treasure!')
        for member in party.members:
            member['coin'] += roll('3d6')*10*member['level']
            member.level_up()
        delay_print('The party escapes the dungeon...')
        return 'wilderness'

    def spoor(self, options, party):
        fsum = 0
        for member in party.members:
            fsum += member['fear']
        asum = 0
        for member in party.members:
            asum += member['aggression']
        if asum > fsum:
            delay_print('You decide to engage the challenge!')
            return 'encounter_dungeon'
        else:
            delay_print('The party, in fear, attempts to hide...')
            loudest, loudest_stealth = party.get_lowest('SKL_hide')
            if roll('1d20')+loudest_stealth > 15:
                delay_print('You successfully avoid whatever was out there...')
                return 'dungeon'
            else:
                delay_print(f'Your feeble attempts at stealth fail, betrayed by {loudest["name"]}!')
                return 'encounter_dungeon'

    def trap(self, options, party):
        trap_kind = random.choices(population=['mechanical', 'magical'], weights=[0.7, 0.3])[0]
        smartest, smartest_search = party.get_highest('SKL_search')
        if roll('1d20')+smartest_search > 15:
            delay_print(f'{smartest["name"]} spots the trap in advance!')
            delay_print(f'The trap is {trap_kind}!')
            if trap_kind == 'mechanical':
                target_stat = 'ABL_dexterity'
                target_skill = 'SKL_lockpick'
            elif trap_kind == 'magical':
                target_stat = 'ABL_intelligence'
                target_skill = 'SKL_decipher'
            else:
                target_skill = 'SKL_lockpick'
            fastest, fastest_pick = party.get_highest(target_skill)
            delay_print(f'{fastest["name"]} attempts to disarm the trap...')
            if roll('1d20')+fastest_pick+fastest.get_mod(fastest[target_stat]) > 15:
                delay_print('They succeed!')
                return 'dungeon'
            else:
                delay_print('They fail!')
                if not fastest.change_hp(-roll('1d6')):
                    delay_print(f'The trap kills {fastest["name"]}!')
                else:
                    delay_print(f'The trap wounds {fastest["name"]}!')
        else:
            delay_print('Nobody in the party spots the trap in time...')
            if trap_kind == 'mechanical':
                target_stat = 'ABL_dexterity'
                target_save = 'SAV_hazard'
            else:
                target_stat = 'ABL_intelligence'
                target_save = 'SAV_magic'
            for member in party.members:
                if roll('1d20')+member.get_mod(member[target_stat]) < 20:
                    delay_print(f'{member["name"]} triggers the {trap_kind} trap!')
                    if roll('1d20') > member[target_save]:
                        delay_print('They evade the trap at the last second!')
                    else:
                        delay_print(f'The trap has claimed {member["name"]}!')
                    break
            else:
                delay_print('But nobody triggers it either!')
        if roll('1d6') == 1:
            delay_print('The trap\'s makers appear...')
            return 'encounter_dungeon'
        else:
            delay_print('Picking yourselves up, you return to the dungeon proper...')
            return 'dungeon'

    def depletion(self, options, party):
        delay_print('Wandering and tired, depletion gnaws at the party...')
        for member in party.members:
            if roll('1d20') < member['SAV_exhaustion']:
                delay_print(f'{member["name"]} feels the tug of exhaustion!')
                if not member.change_hp(-roll('1d6')):
                    delay_print(f'Exhaustion has claimed {member["name"]}!')
                else:
                    delay_print('They struggle on...')

    def explore(self, options, party):
        delay_print('The party picks through the dungeon...')
        smartest, smartest_pathfind = party.get_highest('SKL_pathfind')
        if roll('1d20')+smartest_pathfind > 15:
            delay_print('Some movement is made.')
            return 'dungeon'
        else:
            delay_print('Feels like we\'re going around in circles...')
            if roll('1d6') < 2:
                return 'depletion'
            else:
                return 'explore'

    def progress(self, options, party):
        delay_print('What\'s ahead?')
        if roll('1d6') < 4:
            delay_print('Another level of the dungeon...')
            return 'dungeon'
        else:
            delay_print('At last! The end is in sight!')
            return 'dungeon_end'

    def reward(self, optioins, party):
        delay_print('Sweet, sweet treasure...')
        for member in party.members:
            if roll('1d6') < 5:
                member['coin'] += roll(str(member['level'])+'d6')
            else:
                delay_print(f'{member["name"]} finds something special!')
                member[random.choice(['weaponry', 'armour'])] += roll('1d4')
        if roll('1d6') < 4:
            return 'progress'
        else:
            return 'dungeon'


class Enemy:
    def __init__(self, name, level, parent=None):
        self.name = name
        self.level = level
        self.hp = roll(f'{level}d6')
        self.hpmax = self.hp
        self.reaction = roll('3d6')
        self.parent = parent

    def get_target(self, party):
        getagg = lambda x: x["aggression"]-x["fear"]
        return sorted(party.members, key=getagg)[0]

    def attack(self, target):
        delay_print(f'{self.name} attacks {target["name"]}!')
        if roll('1d20')+self.level > roll('1d20')+target.get_mod(target["ABL_dexterity"])+max(target["SKL_melee"], target["SKL_archery"]):
            target.change_hp(max(roll(f'1d6+{self.level}')-target["armour"], 1)*-1)

    def change_hp(self, val):
        print(f"{self.name}'s hp changes by {val}")
        self.hp += val
        if self.hp > self.hpmax:
            self.hp = self.hpmax
        if self.hp <= 0:
            print(self.name, "dies!")
            if isinstance(self.parent, list):
                self.parent.remove(self)
            return False
        print(self.name, "now has", self.hp, "hp!")
        return True


class venomous_adder(Enemy):
    def __init__(self, name, level, parent):
        self.name = 'venomous adder'
        self.level = level
        self.hp = level
        self.hpmax = self.hp
        self.reaction = 3
        self.parent = parent

    def attack(self, target):
        delay_print(f"The venomous adder snaps at {target['name']}! Their poisonous fangs gleam...")
        if roll('1d20') + self.level > roll('1d20') + target.get_mod(target["ABL_dexterity"]):
            if not roll('1d20') > target['SAV_poison']:
                target.change_hp(-roll('4d10'))


def generate_encounter(region):
    with open('generic_encounters.yaml') as f:
        bestiary = yaml.load(f, yamlLoader)
    amt = roll('1d6')
    zone = bestiary[region]
    zone_weights = []
    for creature in zone:
        c_power = int(creature.split('|')[-1])
        c_weight = 1/c_power
        zone_weights.append(c_weight)
    encounter = []
    while amt > 0:
        chosen = random.choices(zone, zone_weights)[0]
        chosen_amt = roll('1d4')
        if chosen_amt > amt:
            chosen_amt = amt
        encounter += [chosen] * chosen_amt
        amt -= chosen_amt
    created_creature_list = []
    for creature in encounter:
        div = creature.split('|')
        name = '|'.join(div[:-1]).replace(' ', '_')
        pow = int(div[-1])
        created = False
        for etype in Enemy.__subclasses__():
            if etype.__name__ == name:
                created_creature_list.append(etype(name, pow, parent=created_creature_list))
                created = True
        if not created:
            created_creature_list.append(Enemy(name, pow, parent=created_creature_list))
    return created_creature_list


def run_fight(party, enemies):
    leader, _ = party.get_highest('ABL_wisdom')
    party_roll = roll('1d20')+leader.get_mod(leader['ABL_wisdom'])
    enemy_roll = roll('1d20')
    if party_roll > enemy_roll:
        order = [party, enemies]
    else:
        order = [enemies, party]
    round = 0
    while True:
        delay_print(f'ROUND {round}')
        for group in order:
            if group == party:
                for member in group.members:
                    member.attack(member.get_target(enemies))
            else:
                for member in group:
                    member.attack(member.get_target(party))

        if enemies == []:
            delay_print('Victory!')
            break
        round += 1
    return True


def run_encounter(loc, party):
    npcs = generate_encounter(loc)
    delay_print(f'The party encounters a {" and a ".join([npc.name for npc in npcs])}!')
    total_power = 0
    total_friendliness = 0
    for npc in npcs:
        total_power += npc.level
        total_friendliness += npc.reaction
    total_friendly_power = 0
    total_fear = 0
    total_aggression = 0
    reaction_mod = math.ceil((total_friendliness-10)/2)
    for member in party.members:
        total_friendly_power += member['level']
        total_fear += member['fear']
        total_aggression += member['aggression']
    total_opinion = total_fear + total_power - total_friendly_power - total_aggression
    if total_opinion < 0:
        delay_print('The party, in fear, decides to flee!')
        slowest, _ = party.get_lowest('ABL_dexterity')
        if roll('1d20') + slowest.get_mod(slowest['ABL_dexterity']) < 15:
            delay_print('But they catch up!')
        else:
            delay_print('You escape...')
            return
    else:
        if total_fear > total_aggression:
            delay_print('The party attempts to parley!')
            nicest, nicest_skill = party.get_highest('SKL_parley')
            if roll('1d20')+nicest.get_mod(nicest["ABL_charisma"])+nicest_skill+reaction_mod > 15:
                delay_print('You talk them out of fighting!')
                return
            else:
                delay_print('The parley breaks down...')
        else:
            delay_print('The party, unafraid, attempts to fight!')
    run_fight(party, npcs)
    # If TPK game quits anyways so no need to bother with loss text
    delay_print('To the victor go the spoils...')
    loot_share = math.ceil(roll(f'{total_power}d6') / len(party.members))
    for member in party.members:
        member["coin"] += loot_share
    return
