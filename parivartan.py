import argparse
import re
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

class DomainSort(object):
    def __init__(self, name, args):
        self.name = name
        self.args = args
        self.reified = list()

    def __repr__(self):
        return "DomainSort(name=%s, args=%s, reified=%s)" % (self.name, self.args, self.reified)

    def reify(self, agent_dict):
        if len(self.args) == 0:
            self.reified.append(self.name.lower())
        else:
            agent_list = [] # list of lists
            for agent in self.args:
                agent_list.append(agent_dict[agent])
            
            for permutation in list(itertools.product(*agent_list)):
                atom = self.name.lower() + "_"         # "load_"
                
                perm_list = list(permutation)
                for x in perm_list:
                    atom += x + "_"                    # "load_a1_a2_"
                
                atom = atom[:-1]                      # "load_a1_a2"

                self.reified.append(atom)


class Predicate(object):
    def __init__(self, name, args):
        self.name
        self.args

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
    agent_dict = {}
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
        
        # add agent as dictionary key
        if words[0] == "sort":
            if words[1][-1] == ".":
                words[1] = words[1][:-1]

            agent_dict[words[1]] = list()

        # add instance of agent to list in agent_dict
        elif words[0] in agent_dict.keys():
            if words[1][-1] == ".":
                words[1] = words[1][:-1]

            agent_dict[words[0]].append(words[1])

        # words[0] == "event" || "fluent" || "time"
        elif words[0] in sorts_dict.keys():
            tokens = re.findall(r'\w+', words[1])

            if words[0] == "time":
                sorts_dict[words[0]].append(tokens[0])
            else:
                sort_obj = DomainSort(tokens[0], tokens[1:])
                sorts_dict[words[0]].append(sort_obj)
    
        # words[0] == "noninertial"
        elif words[0] in interesting_dict.keys():
            pass

        # added for exception, remove later
        elif len(words) == 1:
        	pass

        else:
            pass
    
    print("Sorts=", sorts_dict)
    print("Agents=", agent_dict)

    # STEP 1: Reification
    print("Step 1:")
    for sort_type in ["event", "fluent"]:
        for sort_obj in sorts_dict[sort_type]:
            sort_obj.reify(agent_dict)

            reified_dict[sort_type].extend(sort_obj.reified)

    print("Reified:", reified_dict)

    # STEP 2: uniqueness
    print("Step 2:")

    for sort_type in ["event", "fluent"]:
        print("%% Uniqueness-of-names axioms for", sort_type)
        sort_comb = itertools.combinations(reified_dict[sort_type], 2)
        for sort_pair in list(sort_comb):
            print(sort_pair[0]," != ", sort_pair[1])

    # STEP 3: circumscription

if __name__ == "__main__":
    parser = create_cmdline_parser()
    args = parser.parse_args()

    main(args.input, args.output)
