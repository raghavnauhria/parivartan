import argparse
import re
from dataclasses import dataclass, field
from typing import List, Set
from collections import defaultdict
import itertools

def create_cmdline_parser() -> argparse.ArgumentParser:
    """
    Simple method to create the argument parser for the app
    :return:
    """
    cmd_parser = argparse.ArgumentParser(
        description='Simple service to append words for a document')
    cmd_parser.add_argument('-i', '--input', action='store', type=str, help='input file = domain file name', default="domain.txt")
    cmd_parser.add_argument('-o', '--output', action='store', type=str, help='output file name (NOTE: will be overwritten)', default="output.txt")

    return cmd_parser

@dataclass
class DomainSort(object):
    name: str
    args: List[str] = field(default_factory=list)


class Predicate(object):
    def __init__(self):
        self.name

def main(input_file_name, output_file):
    domain_file = open(input_file_name, 'r')
    domain = domain_file.readlines()

    # event Load(Agent1,Agent2)
    sorts_dict = {
        "event": [],
        "fluent": [],
        "time": []
    }

    # [time] Initiates(Load(a1),Loaded(),time).  event = load_a1
    agent_dict = defaultdict(list)
    # "Agent1": ["a1", "a2"]

    reified_dict = {
        "event": [],
        "fluent": [],
    }

    interesting_dict = {
        "noninertial": []
    }

    # read the Domain.txt file line-by-line
    for line in domain:
        line = line.strip()
        if line == '':
            continue

        words = line.strip().split(" ")
        
        if words[0] in sorts_dict.keys():
            tokens = re.findall(r'\w+', words[1])

            if words[0] == "time":
                sorts_dict[words[0]].append(tokens[0])
            else:
                sort_obj = DomainSort(tokens[0], tokens[1:])
                sorts_dict[words[0]].append(sort_obj)
    
        elif words[0] in interesting_dict.keys():
            pass

        # words[0] == Agent
        else:
            print('here')
            agent_dict[words[0]].append(words[1][:-1])
    
    print("Sorts=", sorts_dict)
    print("Agents=", agent_dict)

    # STEP 1: Reification
    print("Step 1")
    for sort_type in ["event", "fluent"]:
        print("For", sort_type)
        for sort_obj in sorts_dict[sort_type]:

            if len(sort_obj.args) == 0:
                reified_dict[sort_type].append(sort_obj.name.lower())
                continue

            agent_list = [] # list of lists
            for agent in sort_obj.args:
                agent_list.append(agent_dict[agent])
            
            res = list(itertools.product(*agent_list))
            for permutation in res:
                reify = sort_obj.name.lower() + "_"
                
                perm_list = list(permutation)
                for x in perm_list:
                    reify += x + "_"
                
                reify = reify[:-1]

                reified_dict[sort_type].append(reify)

    print(reified_dict)

    # STEP 2: uniqueness
    # STEP 3: circumscription

if __name__ == "__main__":
    parser = create_cmdline_parser()
    args = parser.parse_args()

    main(args.input, args.output)
