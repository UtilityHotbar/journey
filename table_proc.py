# RPG TOOLS v1.2 by UtilityHotbar
# Table process module

import re
import pprint
import random
import rpgtools


VERBOSE = False
special = re.compile(r'\[([^\[^\]]+)\]')
dicenot = re.compile(r'\{([^\{^\}]+)\}')
doubles = re.compile(r'^(\d+):')
numrnge = re.compile(r'^(\d+)-(\d+):')
formatting = {}


def vb_print(*args):
    if VERBOSE:
        print(args)


class Table:
    def __init__(self, filename=None, init_data=None):
        if not init_data:
            self.data = {}
            if not filename:
                filename = input('Enter table file name: ')
            with open(filename, 'r') as f:
                lines = [line.strip('\n') for line in f.readlines()]+['']  # Makes sure that last table will be terminated
            reading = None
            curr = []
            curr_format = {}
            readmode = 'Normal'
            for line in lines:
                if len(line) > 0:
                    if line[0] == '//':  # ignore comments
                        continue
                if reading:
                    if line == '' or line == ' ' or line.startswith('Endtable:'):  # End the table if separated by a blank line
                        self.data[reading] = curr
                        curr = []
                        curr_format = {}
                        reading = None
                        readmode = 'Normal'
                    elif line.startswith('Type:'):
                        curr_type = re.sub('Type:\s*', '', line, count=1)
                        if curr_type.lower() != 'lookup':
                            print('WARNING: Non-lookup tables currently not supported')
                        curr_format['type'] = curr_type
                    elif line.startswith('Roll:'):
                        readmode = 'Range' # This means that weighted entries should be treated as ranges instead of weights
                        curr_format['roll'] = re.sub('Roll:\s*', '', line, count=1)
                    else:  # Enter line into current table if table has been started
                        amt = re.match(doubles, line)
                        rangefind = re.match(numrnge, line)
                        if amt:
                            if readmode == 'Normal':
                                for i in range(int(amt.group(1))):
                                    curr.append(re.sub(str(amt.group(0))+'\s*', '', line, count=1))
                            elif readmode == 'Range':
                                curr.append(re.sub(str(amt.group(0))+'\s*', '', line, count=1))
                        elif rangefind:
                            for i in range(int(rangefind.group(2))-int(rangefind.group(1))+1):
                                curr.append(re.sub(str(rangefind.group(0))+'\s*', '', line, count=1))
                        else:
                            curr.append(line)
                if line.startswith('Table:') or line.startswith('table:'):
                    reading = re.sub('Table:\s*', '', line, count=1)
        else:
            self.data = init_data


    def table_interact(self):
        print('Use the command !help to list special commands.')
        pp = pprint.PrettyPrinter()
        while True:
            command = input('QUERY: ')
            if not command:
                continue
            elif command == '!help':
                print('!list -> List all tables'
                      '\n!data -> Show table data'
                      '\n!format -> Show table formatting'
                      '\n!random -> Fetch a result from a random table'
                      '\n!verbose -> Toggles debug output')
            elif command == '!list':
                for key in sorted(self.data.keys()):
                    print(key)
            elif command == '!data':
                pp.pprint(self.data)
            elif command == '!format':
                pp.pprint(formatting)
            elif command == '!random':
                target = random.choice(sorted(self.data.keys()))
                print('RANDOM QUERY:', target)
                print('RESULT OF RANDOM QUERY:', self.table_fetch(target))
            elif command == '!verbose':
                global VERBOSE
                if VERBOSE:
                    VERBOSE = False
                else:
                    VERBOSE = True
            else:
                try:
                    print('RESULT OF QUERY:', self.table_fetch(command))
                except KeyError:
                    print('ERROR - Please enter a valid table name or command.')

    def table_fetch(self, search_term, times=1, repeat=True, concat=True):
        vb_print('STARTING QUERY:', search_term)
        if repeat:
            result = random.choices(self.data[search_term], k=times)
        else:
            result = random.sample(self.data[search_term], times)
        vb_print('INITIAL RESULT:', result)
        for i in range(len(result)):
            result[i-1] = self.substitute_dice(result[i-1])
            while re.findall(special, result[i-1]):
                substitutions = re.findall(special, result[i-1])
                vb_print('IDENTIFIED SPECIALS:', substitutions)
                for sub in substitutions:
                    subres = self.substitute_terms(sub)
                    result[i-1] = result[i-1].replace('['+sub+']', subres, 1)
                vb_print(result[i-1])
        vb_print(result)
        vb_print('done')
        if concat:
            return ' '.join(result)
        else:
            return result

    @staticmethod
    def substitute_dice(target):
        while re.findall(dicenot, target):
            dice_substitutions = re.findall(dicenot, target)
            for sub in dice_substitutions:
                subres = rpgtools.roll(sub)
                target = target.replace('{' + sub + '}', str(subres), 1)
        return target

    def substitute_terms(self, sub):
        subres = self.substitute_dice(sub)  # Check for uncaught dice substitutions
        if sub[0] == '@':
            params = sub[1:].split()
            if len(params) > 1:
                times = int(params[0])
                target_table = params[1]
                subres = self.table_fetch(target_table, times)
            else:
                subres = self.table_fetch(params[0])
        elif sub[0] == '|':
            subres = random.choice(sub[1:].split('|'))
        elif sub[0] == '!':
            params = sub[1:].split()
            if len(params) > 1:
                times = int(params[0])
                target_table = params[1]
                subres = self.table_fetch(target_table, times, repeat=False)
            else:
                subres = self.table_fetch(params[0], 1, repeat=False)
        elif sub[0] == '#':
            params = sub[1:].split()
            item = int(params[0])-1
            target_table = params[1]
            subres = self.data[target_table][item]
        elif sub[0] == ' ':
            subres = sub[1:]
        return subres


if __name__ == '__main__':
    myTable = Table()
    myTable.table_interact()
