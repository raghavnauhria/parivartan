import argparse
import re
from typing import Set, Dict, List
import itertools
import sys

def create_cmdline_parser() -> argparse.ArgumentParser:
    """
    Simple method to create the argument parser for the app
    :return:
    """
    cmd_parser = argparse.ArgumentParser(
        description='Simple service to append words for a document')
    cmd_parser.add_argument('-i', '--input', action='store', type=str, help='input file = domain file name', default="domain.txt")
    cmd_parser.add_argument('-o', '--output', action='store', type=str, help='output file name (NOTE: file will be overwritten)', default="output.txt")
    cmd_parser.add_argument('-p', '--predicates', action='store', type=str, help='.txt file containing EC predicates', default="predicates.txt")
    cmd_parser.add_argument('-a', '--axioms', action='store', type=str, help='.txt file containing EC axioms', default="axioms.txt")

    return cmd_parser


def reification_master(sort_name: str, sort_args: List[str], agent_dict: Dict[str, List[str]]) -> List[str]:
    """
    Function to reify the given sort, i.e. event/fluent, w.r.t the agents in the argument
    :param sort_name:  name of the sort
    :param sort_args:  list of arguments to the sort
    :param agent_dict: dictionary of all agents, with agent_names as keys, which maps to instances as a list
    :return: list of reified atoms
    """
    reification_prefix = sort_name                  # "load"

    if len(sort_args) == 0:
        return [reification_prefix]
    else:
        result = []

        agent_list = []  # list of lists
        for agent in sort_args:
            if agent in agent_dict.keys():
                agent_list.append(agent_dict[agent])
            else:
                agent_list.append([agent])

        for permutation in list(itertools.product(*agent_list)):
            atom = reification_prefix + "_"         # "load_"

            perm_list = list(permutation)
            for x in perm_list:
                atom += x + "_"                     # "load_a1_a2_"

            atom = atom[:-1]                        # "load_a1_a2"

            result.append(atom)
    
    return result

class DomainSort(object):
    def __init__(self, name: str, args: List[str]):
        """
        Constructor function
        :param name: name of event/fluent declared
        :param args: input arguments to this event/fluent
        """
        self.name = name
        self.args = args
        self.reified = list()

    def __repr__(self):
        """
        Function to print the class object
        """
        return "DomainSort(name=%s, args=%s, reified=%s)" % (self.name, self.args, self.reified)

    def reify(self, agent_dict: Dict[str, List[str]]):
        """
        Function to reify the given event/fluent w.r.t the agents in the argument
        :param agent_dict: dictionary of all agents, with agent_names as keys, which maps to instances as a list
        """
        reification_prefix = self.name.lower()         # "load"

        result = reification_master(reification_prefix, self.args, agent_dict)

        self.reified.extend(result)


class Predicate(object):
    def __init__(self, name: str, args: List[str]):
        """
        Constructor function
        :param name: name of predicate
        :param args: input arguments to this predicate, e.g. [event, fluent, time]
        """
        self.name = name
        self.args = args
        self.instances = list()
        self.remarks_for_instances = list()     # e.g. to capture boolean for "HoldsAt"

    def __repr__(self):
        """
        Function to print the class object
        """
        return "Predicate(name=%s, args=%s, instances=%s, remarks=%s)" % (self.name, self.args, self.instances, self.remarks_for_instances)

    def addInstanceAndReify(self, arg_string: str, agent_dict: Dict[str, List[str]], pred_remarks: str = ""):
        """
        For the given predicate, parse the inputs, reify and append to the instances[] list
        :param arg_string: format = "EventName(Agent1,Agent2),FluentName(),time"
        :param agent_dict: dictionary of all agents, with agent_names as keys, which maps to instances as a list
        :param pred_remarks: to capture instance specific boolean values
        """
        reified_instance = []  # list of lists
        counter = 0
        while counter < len(self.args):
            # get sort name
            x = re.search(r'\w+', arg_string)
            sort_name = arg_string[0:x.end()].lower()

            arg_string = arg_string[x.end():]

            # check if sort is generic or instantiation
            if sort_name == self.args[counter]:
                reified_instance.append([None])
            # append if time but instantiated
            elif counter == len(self.args)-1:
                reified_instance.append([sort_name])
            else:
                # parse and get arguments
                parenthesis_end = re.search("\)", arg_string).end()
                sort_args = re.findall(r'\w+', arg_string[:parenthesis_end])
                arg_string = arg_string[parenthesis_end:]
                
                result = reification_master(sort_name, sort_args, agent_dict)
                
                # reify
                reified_instance.append(result)

            # skip the comma
            if arg_string and arg_string[0] == ",":
                arg_string = arg_string[1:]

            counter += 1

        combined_output = list(itertools.product(*reified_instance))
        combined_output = [list(i) for i in combined_output]

        for i in range(len(combined_output)):
            self.remarks_for_instances.append(pred_remarks)
        
        self.instances.extend(combined_output)

    def getInstanceAsFOL(self, instance_: List[str]) -> str:
        result = "("
        started = False

        for i in range(len(self.args)):
            if instance_[i] != None:
                if started:
                    result += " AND "
                else:
                    started = True
                result += (self.args[i] + " = " + instance_[i])

        result += ")"
        return result

    def circumscribe(self):
        """
        For the given predicate, print circumscribed output
        """
        # predicate boiler plate, e.g. Initiates(event, fluent, time)
        boiler = self.name + "(" + ', '.join(self.args) + ")"

        # print [event,fluent,time] or other arguments, as specified
        print("[" + ','.join(self.args) + "]", end=" ")

        if len(self.instances) == 0:
            print(boiler + ".")
        else:
            print("(", boiler, "<=>")

            inst_string = self.getInstanceAsFOL(self.instances[0])
            for i in self.instances[1:]:
                inst_string += (" OR " + self.getInstanceAsFOL(i))

            print(inst_string, ").\n")

    def circumscribe_holdsat(self):
        for i in range(len(self.instances)):
            inst_string = ""
            inst_string += (self.remarks_for_instances[i]+ self.name + "(")
            inst_string += self.instances[i][0] + "," + self.instances[i][1]
            inst_string += ")."
            print(inst_string)
        

def readPredicates(predicates_file: str) -> Dict[str, Predicate]:
    """
    Function to read the EC predicates
    :param predicates_file: Filename
    :return: dictionary mapping predicate name to it's object for O(1) access
    """
    predicates_dict = {
        # "Initiates" : Predicate(Initiates(event,fluent,time)),
    }

    pred_file = open(predicates_file, 'r')
    pred = pred_file.readlines()

    # read the predicates.txt file line-by-line
    for line in pred:
        line = line.strip()
        if line == '':
            continue

        tokens = re.findall(r'\w+', line)
        predicates_dict[tokens[0]] = Predicate(tokens[0], tokens[1:])

    # add "\\not Releases" and "\\not ReleasedAt" to predicates_dict
    for new_predicate in ["Releases", "ReleasedAt"]:
        if new_predicate in predicates_dict.keys():
            predicates_dict[("\\not " + new_predicate)] = Predicate(
                ("\\not " + new_predicate), predicates_dict[new_predicate].args)

    return predicates_dict


def helperRefiy(predicateItem: str) -> str:
    """
    Helper function for reifyStateConstraints() function
    :param predicateItem: example = "!HoldsAt(Dead(), time)."
    :return: example "!HoldsAt(dead, time)."
    """
    result = ""

    if predicateItem[0] == "!":
        result += predicateItem[0]
        predicateItem = predicateItem[1:]

    tokens = re.findall(r'\w+', predicateItem)
    result += tokens[0] + "(" + tokens[1].lower() + ", " + tokens[2] + ")"
    
    if predicateItem[-1] == ".":
        result += "."

    return result

def reifyStateConstraints(stateConstraints: List[List[str]]):
    """
    Function to reify and print State Constraints
    :param stateConstraints: example = [
        ['[time]', 'HoldsAt(Dead(),time)', '<->', '!HoldsAt(Alive(),time).'],
        ['[time]', '!HoldsAt(Dead(),time)', '<->', 'HoldsAt(Alive(),time).']]
    """
    for stateConstraint in stateConstraints:
        stateConstraint[1] = helperRefiy(stateConstraint[1])
        stateConstraint[3] = helperRefiy(stateConstraint[3])

        inst_string = " ".join(stateConstraint)

        print(inst_string)

def main(input_file_name: str, output_file: str, predicates_file: str, axioms_file: str):
    predicates_dict = readPredicates(predicates_file)

    # set output stream for "print()"
    f = open(output_file, "w")
    sys.stdout = f

    sorts_dict = {
        "event": [],
        "fluent": [],
        "time": []
    }

    agent_dict = {}

    reified_dict = {
        "event": [],
        "fluent": [],
    }

    interesting_dict = {
        "noninertial": [],
        "stateconstraints": []
    }

    domain_file = open(input_file_name, 'r')
    domain = domain_file.readlines()

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
            words[1] = words[1][:-1]
            interesting_dict[words[0]].append(words[1])
            pred_args = "event,%s,time"%(words[1])

            predicates_dict["Releases"].addInstanceAndReify(pred_args, agent_dict)

        else:
            if words[0][0] == "[":
                # simple action descriptions
                if len(words) == 2:
                    pred_name, pred_args = words[1].split("(", maxsplit=1)
                    pred_args = pred_args[:-2]

                    predicates_dict[pred_name].addInstanceAndReify(pred_args, agent_dict)
                # state constraints or other lines
                else:
                    # parse state constraints
                    if words[2] == "<->":
                        interesting_dict["stateconstraints"].append(words)
                    # compound action descriptions
                    else:
                        pass
            # parse initial state
            else:
                pred_remarks = ""
                if words[0][0] == '!':
                    words[0] = words[0][1:]
                    pred_remarks = "!"

                pred_name, pred_args = words[0].split("(", maxsplit=1)
                pred_args = pred_args[:-2]
                predicates_dict[pred_name].addInstanceAndReify(pred_args, agent_dict, pred_remarks)
    

    # STEP 1: Reification
    print("%% Step 1: Reification")
    for sort_type in ["event", "fluent"]:
        for sort_obj in sorts_dict[sort_type]:
            sort_obj.reify(agent_dict)

            reified_dict[sort_type].extend(sort_obj.reified)

    print("event", ', '.join(reified_dict["event"]))
    print("fluent", ', '.join(reified_dict["fluent"]))
    print("time", ', '.join(sorts_dict["time"]))

    # STEP 2: uniqueness
    print("\n%% Step 2: Uniqueness")

    for sort_type in ["event", "fluent"]:
        print("\n%% Uniqueness-of-names axioms for", sort_type)
        sort_comb = itertools.combinations(reified_dict[sort_type], 2)
        for sort_pair in list(sort_comb):
            print(sort_pair[0]," != ", sort_pair[1])


    # STEP 3: circumscription
    print("\n%% STEP 3: circumscription")
    for pred in ["Initiates", "Terminates", "Happens"]:
        boiler = pred + "(" + ', '.join(predicates_dict[pred].args) + ")"
        print("%% Circumscribed", boiler, "axioms")
        predicates_dict[pred].circumscribe()

    print("%% Circumscribed Releases(event,fluent,time) axioms")
    if len(interesting_dict["noninertial"]) == 0:
        predicates_dict["\\not Releases"].circumscribe()
    else:
        for fluent_ in sorts_dict["fluent"]:
            fluent_inst = fluent_.name + "(" + ','.join(fluent_.args) +  ")"
            if fluent_inst not in interesting_dict["noninertial"]:
                pred_args = "event,%s,time" % (fluent_inst)
                predicates_dict["\\not Releases"].addInstanceAndReify(pred_args, agent_dict)
        
        predicates_dict["\\not Releases"].circumscribe()
        predicates_dict["Releases"].circumscribe()

    print("\n%% reified initial conditions")
    predicates_dict["HoldsAt"].circumscribe_holdsat()

    print("\n%% Circumscribed ReleasedAt(fluent,time) axioms")
    if len(interesting_dict["noninertial"]) == 0:
        predicates_dict["\\not ReleasedAt"].circumscribe()
    else:
        for fluent_ in sorts_dict["fluent"]:
            fluent_inst = fluent_.name + "(" + ','.join(fluent_.args) +  ")"
            if fluent_inst not in interesting_dict["noninertial"]:
                pred_args = "%s,time" % (fluent_inst)
                predicates_dict["\\not ReleasedAt"].addInstanceAndReify(pred_args, agent_dict)
        
        predicates_dict["\\not ReleasedAt"].circumscribe()
        # predicates_dict["ReleasedAt"].circumscribe()

    # reified state constraints
    if len(interesting_dict["stateconstraints"]) != 0:
        print("%% The reified state constraint(s)")
        reifyStateConstraints(interesting_dict["stateconstraints"])

    print("\n%% EC Axioms")
    axioms = open(axioms_file, 'r')
    print(axioms.read())
    axioms.close()


if __name__ == "__main__":
    parser = create_cmdline_parser()
    args = parser.parse_args()

    main(args.input, args.output, args.predicates, args.axioms)
