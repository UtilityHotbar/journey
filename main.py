import yaml
from yaml import Loader as yamlLoader
from rpgtools import roll, delay_print
import random
from config import *


def main():
    # YAML file lays out markov chain structure
    # Individual functions can deviate from chain
    # But fallback present in form of just following
    # markov chain to next node
    with open('generic_adventure.yaml') as f:
        adventuredata = yaml.load(f, Loader=yamlLoader)
    scenariodata = __import__(adventuredata['scenes'])
    partydata = __import__(adventuredata['characters'])
    curr_node = adventuredata['start']
    history = []
    seed_cand = input('Enter seed or press RETURN to start your adventure: ')
    if seed_cand:
        random.seed(seed_cand)
    else:
        seed = str(random.random())
        print(f'Using random seed {seed}')
        random.seed(seed)
    myParty = partydata.Party()
    myScenario = scenariodata.Adv()
    while True:
        history.append(curr_node)
        if DEBUG:
            delay_print(f'CURR NODE: {curr_node}')
            delay_print('===========')
        options = adventuredata[curr_node]
        if not hasattr(myScenario, curr_node):
            curr_node = myScenario.generic_encounter(curr_node, options, myParty)
        else:
            curr_node = myScenario.__getattribute__(curr_node)(options, myParty)
            if not curr_node:
                curr_node = myScenario.generic_encounter(curr_node, options, myParty)
        if STEP_THROUGH:
            input('<Press RETURN to continue>')


if __name__ == '__main__':
    print('=====[Tales of an Endless Journey]=====')
    print('v0.1.0 by UtilityHotbar\n')
    main()