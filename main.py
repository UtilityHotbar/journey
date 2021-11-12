import yaml
from yaml import Loader as yamlLoader
from rpgtools import roll, delay_print
import random
from pprint import PrettyPrinter
import math
import time

random.seed(input("Enter seed: "))

DEBUG = False
STEP_THROUGH = False

namepcs = ['ae', 'th', 'er', 'al', 'bo', 're', 'ka', 'ly', 'am', 'lo', 'pi', 'ri', 'ti', 'ki']
master_ability_list = ['wisdom', 'dexterity', 'strength', 'charisma', 'intelligence', 'constitution']
master_save_list = ['hazard', 'poison', 'magic', 'exhaustion']
master_skill_list = ['lockpick', 'hide', 'search', 'forage', 'pathfind', 'decipher', 'parley', 'melee', 'archery']


class Adventurer(dict):
    def __init__(self, monologue=True, parent=None):
        self.parent = parent
        hp = roll('3d6')
        data = {
            'hp': hp,
            'hpmax': hp,
            'level': 1,
            'type': random.choices(population=['human', 'elf', 'dwarf', 'wizard'], weights=[0.7, 0.1, 0.1, 0.1])[0],
            'aggression': roll('2d6'),
            'fear': roll('2d6'),
            'age': roll('18+3d6'),
            'coin': roll('3d6'),
            'armour': 0,
            'weaponry': 0,
        }
        name = ''
        for _ in range(roll('1d3+1')):
            name += random.choice(namepcs)
        name = name.capitalize()
        data['name'] = name
        if monologue:
            delay_print(f'Their name is {name}.')
        gift = random.choices(population=['3d6', '4d6kh3', '4d6kl3'], weights=[0.7, 0.2, 0.1])[0]
        for ability in master_ability_list:
            score = roll(gift)
            if monologue:
                if self.get_mod(score) == 1:
                    delay_print(f'They demonstrated great promise in {ability}.')
                elif self.get_mod(score) == -1:
                    delay_print(f'They were not adept at {ability}.')
            data['ABL_' + ability] = score
        for skill in master_skill_list:
            score = min([roll('1d4-1'), roll('1d4-1'), roll('1d4-1')])
            if monologue:
                if score >= 1:
                    delay_print(f'In their childhood they picked up some skill in {skill}.')
            data['SKL_' + skill] = score
        for save in master_save_list:
            score = roll('20-1d4')
            if monologue:
                if score <= 17:
                    delay_print(f'They were particularly good at fending off {save}.')
            data['SAV_' + save] = score
        terms_lived = math.ceil((data['age']-18)/3)
        vocation = random.choice(['soldier', 'ranger', 'vagabond', 'scholar', 'trader', 'wanderer'])
        if monologue:
            delay_print(f'They chose a vocation as a {vocation}.')
        for term in range(terms_lived):
            if vocation == 'soldier':
                prime_req = 'strength'
                skill_list = ['melee', 'archery', 'search']
                sav_list = ['poison', 'exhaustion']
            elif vocation == 'ranger':
                prime_req = 'constitution'
                skill_list = ['forage', 'archery', 'pathfind']
                sav_list = ['exhaustion', 'hazard']
            elif vocation == 'vagabond':
                prime_req = 'dexterity'
                skill_list = ['hide', 'lockpick', 'search']
                sav_list = ['poison', 'hazard']
            elif vocation == 'scholar':
                prime_req = 'intelligence'
                skill_list = ['decipher', 'parley', 'search']
                sav_list = ['magic', 'hazard']
            elif vocation == 'trader':
                prime_req = 'charisma'
                skill_list = ['hide', 'parley', 'melee']
                sav_list = ['poison', 'exhaustion']
            elif vocation == 'wanderer':
                prime_req = 'dexterity'
                skill_list = ['forage', 'melee', 'search']
                sav_list = ['exhaustion', 'hazard']
            life_event = ['wound', 'wound', 'skill', 'save', 'save', 'none', 'promote'][min(roll('1d6+'+str(self.get_mod(data['ABL_'+prime_req]))),6)]
            if life_event == 'wound':
                if monologue:
                    delay_print('They were wounded in the course of their vocation.')
                data['hpmax'] -= roll('1d6')
                if data['hpmax'] <= 0:
                    if monologue:
                        delay_print('Their wounds caused them to leave their profession early.')
                    data['hpmax'] = roll('1d4')
                    data['hp'] = data['hpmax']
                    break  # Muster out if you get too hurt
                data['hp'] = data['hpmax']
            elif life_event == 'skill':
                chosen_skill = random.choice(skill_list)
                data['SKL_'+chosen_skill] += 1+self.get_mod(data['ABL_intelligence'])
                if monologue:
                    delay_print(f'They attained a skill in {chosen_skill}.')
            elif life_event == 'save':
                chosen_save = random.choice(sav_list)
                data['SAV_'+chosen_save] -= roll('1d4')+self.get_mod(data['ABL_constitution'])
                if monologue:
                    delay_print(f'They became adept at avoiding {chosen_save}.')
                
            elif life_event == 'none':
                if monologue:
                    delay_print('The term of service passed uneventfully.')
            elif life_event == 'promote':
                extra = roll('1d6')
                data['hp'] += extra
                data['hpmax'] += extra
                data['coin'] += roll('2d6')
                if monologue:
                    delay_print('They attained great renown in their position.')

        if DEBUG:
            PrettyPrinter().pprint(data)
        super().__init__(data)

    @staticmethod
    def get_mod(score):
        return math.floor((score - 10) / 3)

    def change_hp(self, val):
        print(f"{self['name']}'s hp changes by {val}")
        self['hp'] += val
        if self['hp'] > self['hpmax']:
            self['hp'] = self['hpmax']
        if self['hp'] <= 0:
            print(self["name"], "dies!")
            if isinstance(self.parent, Party):
                self.parent.remove(self)
            return False
        print(self["name"], "now has", self["hp"], "hp!")
        return True

    def level_up(self):
        self['level'] += 1
        self['hpmax'] += max(roll('1d6')+self.get_mod(self['ABL_constitution']), 1)
        self['hp'] = self['hpmax']
        upgrade = roll('1d3')
        if upgrade == 1:
            upgrade_ability = random.choice(master_ability_list)
            delay_print(f'{self["name"]} upgrades their {upgrade_ability}!')
            upgrade_ability = 'ABL_'+upgrade_ability
            self[upgrade_ability] += 1
            if self[upgrade_ability] > 20:
                self[upgrade_ability] = 20
        elif upgrade == 2:
            upgrade_save = random.choice(master_save_list)
            delay_print(f'{self["name"]} upgrades their {upgrade_save}!')
            upgrade_save = 'SAV_' + upgrade_save
            self[upgrade_save] -= 1
            if self[upgrade_save] < 1:
                self[upgrade_save] = 1
        elif upgrade == 3:
            upgrade_skill = random.choice(master_skill_list)
            delay_print(f'{self["name"]} upgrades their {upgrade_skill}!')
            upgrade_skill = 'SKL_' + upgrade_skill
            self[upgrade_skill] += 1

    def get_target(self, targets):
        if targets:
            getpow = lambda x: x.level
            return sorted(targets, key=getpow)[0]

    def attack(self, target):
        if target:
            print(f'{self["name"]} attacks {target.name}!')
            if roll('1d20')+math.ceil(target.level/2) < roll('1d20')+self.get_mod(self["ABL_dexterity"])+max(self["SKL_melee"], self["SKL_archery"]):
                target.change_hp(max(roll(f'1d6+{self["weaponry"]+self.get_mod(self["ABL_strength"])}'), 1)*-1)


class Party:
    def __init__(self):
        self.members = []
        self.total_score = 0
        for _ in range(roll('2d6+2')):
            self.members.append(Adventurer(monologue=False, parent=self))

    def get_wounded_members(self):
        wounded = []
        for member in self.members:
            if member['hp'] < math.ceil(member['hpmax'] / 2):
                wounded.append(member)
        return wounded

    def get_lowest(self, val):
        cand = None
        c_lowest = None
        for member in self.members:
            if not cand:
                cand = member[val]
                c_lowest = member
            elif member[val] < cand:
                cand = member[val]
                c_lowest = member
        return c_lowest, cand

    def get_highest(self, val):
        cand = 0
        c_highest = None
        for member in self.members:
            if member[val] >= cand:
                cand = member[val]
                c_highest = member
        return c_highest, cand

    def remove(self, member):
        self.total_score += member["level"]*100
        self.total_score += member["coin"]
        self.members.remove(member)
        if len(self.members) == 0:
            delay_print(f"You lose! Your final score was {self.total_score}")
            exit()

    def expand(self, amt):
        for _ in range(amt):
            self.members.append(Adventurer(monologue=False, parent=self))


def main():
    # YAML file lays out markov chain structure
    # Individual functions can deviate from chain
    # But fallback present in form of just following
    # markov chain to next node
    with open('generic_adventure.yaml') as f:
        adventuredata = yaml.load(f, Loader=yamlLoader)
    scenariodata = __import__(adventuredata['scenes']).Adv()
    curr_node = adventuredata['start']
    history = []
    myParty = Party()
    while True:
        history.append(curr_node)
        if DEBUG:
            delay_print(f'CURR NODE: {curr_node}')
            delay_print('===========')
        options = adventuredata[curr_node]
        if not hasattr(scenariodata, curr_node):
            curr_node = scenariodata.generic_encounter(curr_node, options, myParty)
        else:
            curr_node = scenariodata.__getattribute__(curr_node)(options, myParty)
            if not curr_node:
                curr_node = scenariodata.generic_encounter(curr_node, options, myParty)
        if STEP_THROUGH:
            input('<Press RETURN to continue>')


if __name__ == '__main__':
    main()