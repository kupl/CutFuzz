#!/usr/bin/env python3
import os
import pickle
import random
import re
from tqdm import tqdm
import codecs
import exrex


def pprint_tree(tree, file=None, _prefix="", _last=True):
    result = ""
    (_, _, value, _, children) = tree
    result += (_prefix + ("└─ " if _last else "├─ ") + value+"\n")
    _prefix += "   " if _last else "│  "
    child_count = len(children)
    for i, child in enumerate(children):
        _last = i == (child_count - 1)
        result += pprint_tree(child, file, _prefix, _last)
    return result


def include_regexp(expansion):
    for i in expansion:
        if type(i) == tuple:
            return True
        elif type(i) == list:
            if include_regexp(i):
                return True
    return False


class InputGenerator():
    def __init__(self, grammar, depths_dict, config, pruning_list, log=False):
        self.grammar = grammar
        self.depths_dict = depths_dict
        self.config = config
        self.log = log
        self.pruning_list = pruning_list
        # self.s_pattern = re.compile("/\[\\\\u....\]")
        # self.l_pattern = re.compile("/\[\\\\u....-\\\\u....\]/")

    def pcfg_update(self, rule_dict):
        self.grammar = rule_dict

    def is_nonterminal(self, s):
        return s in self.grammar

    def expansions_to_children(self, d, expansions, is_random):
        # print("expansions:", expansions)
        possible_children = []
        children_probability = []
        deriv_num_list = []
        for (expansion, deriv_num, prob) in expansions:

            children = []
            for i in range(len(expansion)):
                if type(expansion[i]) == str:
                    if self.is_nonterminal(expansion[i]):
                        children.append((d, i, expansion[i], -1, None))
                    else:
                        children.append((d, i, expansion[i], -1, []))
                else:
                    raise Exception("Strange expr: " + str(expansion[i]))
            possible_children.append(children)
            deriv_num_list.append(deriv_num)
            children_probability.append(prob)

        # print("possible_children:", possible_children)
        # print("children_probability:", children_probability)
        # print("####################################################")
        return (possible_children, deriv_num_list,  children_probability)

    def dl_subset(self, derivation, sub_derivation):
        # print("********************************")
        # print("derivation:", derivation)
        # print("sub_derivation:", sub_derivation)
        d_i = 0
        s_i = 0
        while d_i < len(derivation) and s_i < len(sub_derivation):
            if derivation[d_i][1] == sub_derivation[s_i][0] and derivation[d_i][2] == sub_derivation[s_i][1]:
                if type(sub_derivation[s_i][3]) == int:
                    if sub_derivation[s_i][3] != derivation[d_i][4]:
                        d_i += 1
                    else:
                        d_i += 1
                        s_i += 1
                else:
                    simple_children = [j[2] for j in derivation[d_i][4]]
                    d_i += 1
                    if simple_children != sub_derivation[s_i][3]:
                        if d_i == len(derivation):
                            return False
                    else:
                        s_i += 1
            else:
                d_i += 1
                s_i += 1
        if s_i != len(sub_derivation):
            return False
        return True

    def is_pruning(self, symbol, pruning_list, derivation_list):
        if pruning_list == []:
            return True

        before_symbol = symbol
        pruning_idx = 0
        for derivation in range(len(derivation_list)):
            if pruning_idx >= len(pruning_list):
                return True
            # print("pruning_list[pruning_idx]:", pruning_list[pruning_idx])
            # print("derivation_list[derivation]:", derivation_list[derivation])
            derivation_symbol = derivation_list[-derivation-1][2]
            if type(pruning_list[-pruning_idx-1][2]) == int:
                if pruning_list[-pruning_idx-1][2] == derivation_list[-derivation-1][3]:
                    before_symbol = derivation_symbol
                    pruning_idx += 1
                    # print("\n\n\n\n\n")
                else:
                    return False
            else:
                derivation_num = derivation_list[-derivation-1][1]
                derivation_children = []
                for i in derivation_list[-derivation-1][4]:
                    derivation_children.append(i[2])
                # print("derivation_symbol:", derivation_symbol)
                # print("derivation_children:", derivation_children)
                # print("-----------------------------------")
                if before_symbol in derivation_children:
                    new_derivation = (derivation_symbol,
                                      derivation_num, derivation_children)
                    if pruning_list[-pruning_idx-1] != new_derivation:
                        return False
                    before_symbol = derivation_symbol
                    pruning_idx += 1
        if pruning_idx == len(pruning_list):
            return True
        return False

    def children_to_prune(self, symbol_num, symbol, derivation_list, used_pruning_rules):
        try:
            pruning_list_sub = self.pruning_list[symbol]
        except:
            pruning_list_sub = []

        to_be_pruned = []
        for pruning_idx in range(len(pruning_list_sub)):
            if pruning_list_sub[pruning_idx][0] >= 0 and pruning_list_sub[pruning_idx][0] != symbol_num:
                pass
            elif self.is_pruning(symbol, pruning_list_sub[pruning_idx][1], derivation_list):
                p_flag = True
                for dl in pruning_list_sub[pruning_idx][2]:
                    if not self.dl_subset(derivation_list, dl):
                        p_flag = False
                        break
                if p_flag:
                    to_be_pruned.append(pruning_list_sub[pruning_idx][3])
                    self.pruning_list[symbol][pruning_idx][4] += 1

                    pruning_rule = (symbol, pruning_list_sub[pruning_idx])
                    if pruning_rule not in used_pruning_rules:
                        used_pruning_rules.append(pruning_rule)
        return to_be_pruned, used_pruning_rules

    def find_child_index(self, possible_children, prune):
        # print("\tprune:", prune)
        for idx in range(len(possible_children)):
            child_list = []
            for i in possible_children[idx]:
                child_list.append(i[2])
            # print("\tchild_list:", child_list)
            if child_list == prune:
                # print("Equal! :", idx)
                return idx
        raise Exception("expansion not found")

    def expand_node_randomly(self, node, derivation_list, used_pruning_rules):
        (d, symbol_num, symbol, deriv_num, children) = node
        # if symbol == "sourceElement":
        #     print("symbol:", symbol)
        #     print("children:", children)
        #     print("derivation_list:", derivation_list, "\n\n")

        if children is None:
            expansions = self.grammar[symbol]
            # now_time = time.time()
            (possible_children, deriv_num_list, children_probability) = self.expansions_to_children(
                d+1, expansions, True)
            # if symbol == "sourceElement":
            #     print("possible_children:", possible_children)

            if len(possible_children) > 1:
                new_children_list, used_pruning_rules = self.children_to_prune(
                    symbol_num, symbol, derivation_list, used_pruning_rules)
                for prune in new_children_list:
                    try:
                        idx = self.find_child_index(possible_children, prune)
                        del possible_children[idx]
                        del deriv_num_list[idx]
                        del children_probability[idx]
                    except:
                        # print("******************************************")
                        # print("symbol:", symbol, "\n")
                        # print("new_children_list:", new_children_list, "\n")
                        # print("prune:", prune, "\n")
                        # print("possible_children:", possible_children, "\n")
                        # # print("derivation_list:", derivation_list, "\n")
                        # print("expansion not found.")
                        pass
                    if len(possible_children) == 1:
                        break

            # if possible_children == []:
                # print("expansions:", expansions)
                # print("possible_children:", possible_children)
                # print("deriv_num_list:", deriv_num_list)
                # print("children_probability:", children_probability)
            temp_idx_list = range(len(possible_children))
            chosen_child_idx = random.choices(population=temp_idx_list,
                                              weights=children_probability, k=1)[0]
            new_child = (
                d, symbol_num, symbol, deriv_num_list[chosen_child_idx], possible_children[chosen_child_idx])
            derivation_list.append(new_child)
            return new_child, derivation_list, used_pruning_rules
        else:
            new_children = []
            for i in children:
                new_child, derivation_list, used_pruning_rules = self.expand_node_randomly(
                    i, derivation_list, used_pruning_rules)
                new_children.append(new_child)
            return (d, symbol_num, symbol, deriv_num, new_children), derivation_list, used_pruning_rules

    def expansion_cost(self, symbol, expansion):
        expansions_with_depths = self.depths_dict[symbol][0]
        for expansion_with_depths in expansions_with_depths:
            if expansion_with_depths[0] == expansion:
                return expansion_with_depths[1]
        # print("expansion not found.")
        # print("symbol:", symbol)
        # print("expansion:", expansion)
        # print("expansions_with_depths:", expansions_with_depths)
        # print("Check what is strange.")
        # exit(0)
        return 999

    def expand_minimum_node(self, node, derivation_list):
        (d, symbol_num, symbol, deriv_num, children) = node

        if children is None:
            expansions = self.grammar[symbol]
            expansions_with_cost = [(expansion, 0, self.expansion_cost(
                symbol, expansion)) for (expansion, _, _) in expansions]
            (possible_children, deriv_num_list, children_cost) = self.expansions_to_children(
                d+1, expansions_with_cost, False)

            chosen_cost = min(
                [cost for cost in children_cost])

            new_possible_children = []
            new_deriv_num_list = []
            for i in range(len(children_cost)):
                if children_cost[i] == chosen_cost:
                    new_possible_children.append(possible_children[i])
                    new_deriv_num_list.append(deriv_num_list[i])
            temp_idx_list = range(len(new_possible_children))
            chosen_child_idx = random.choices(
                population=temp_idx_list, k=1)[0]
            new_child = (
                d, symbol_num, symbol, deriv_num_list[chosen_child_idx], new_possible_children[chosen_child_idx])
            derivation_list.append(new_child)
            return new_child, derivation_list
        else:
            new_children = []
            for i in children:
                new_child, derivation_list = self.expand_minimum_node(
                    i, derivation_list)
                new_children.append(new_child)
            return (d, symbol_num, symbol, deriv_num, new_children), derivation_list

    def possible_expansions(self, node):
        (_, _, _, _, children) = node
        if children is None:
            return 1
        return sum(self.possible_expansions(c) for c in children)

    def any_possible_expansions(self, node):
        (_, _, _, _, children) = node
        if children is None:
            return True
        return any(self.any_possible_expansions(c) for c in children)

    def expand_check(self, node, max_depths):
        # print(node)
        (d, _, _, _, children) = node
        if d >= max_depths:
            return False
        elif children is None:
            return True
        elif children == []:
            return False
        else:
            return any(self.expand_check(c, max_depths) for c in children)

    def tree_to_string(self, node):
        (_, _, symbol, _, children) = node
        if children == []:
            if len(symbol) > 1 and (symbol[0] == symbol[-1] == "'" or symbol[0] == symbol[-1] == '"'):
                return symbol[1:-1]
            elif len(symbol) > 4 and symbol[:2] == "/[" and symbol[-2:] == "]/":
                return exrex.getone(symbol[1:-1])
            return symbol
        elif children == None:
            raise Exception("Not expended symbol:", symbol)
        else:
            result = ""
            for i in children:
                result += self.tree_to_string(i)
            return result

    def generate_input(self, num, pbar):
        max_depths = self.config["max_depths"]
        result = []
        for i in range(num):
            # print(i)
            # (depths, n-th symbol, symbol, derivation num, child)
            tree = (1, 0, self.config["start_rule"], -1, None)
            derivation_list = []
            used_pruning_rules = []
            while self.expand_check(tree, max_depths):
                tree, derivation_list, used_pruning_rules = self.expand_node_randomly(
                    tree, derivation_list, used_pruning_rules)
            while self.any_possible_expansions(tree):
                tree, derivation_list = self.expand_minimum_node(
                    tree, derivation_list)
            result.append((self.tree_to_string(tree), tree,
                           derivation_list, used_pruning_rules))
            # print(str(i)+"th input created.")
            # print(pprint_tree(tree))
            # print(result[i][0], "\n")
            pbar.update(1)

        return result, self.pruning_list


def normalize_prob(expr_list):
    probability_sum = 0
    normalized_list = []
    for i in expr_list:
        probability_sum += i[2]

    for i in expr_list:
        if probability_sum > 0:
            normalized_list.append([i[0], i[1], i[2]/probability_sum])
        else:
            normalized_list.append([i[0], i[1], 1/len(expr_list)])
    return normalized_list


def parse_bnf(bnf_file, suffix):
    pcfg = {}
    prob_pattern = re.compile(" @@ [0-9.E-]+([ ]*\|[ ]*|;\n)")
    prob_simple = re.compile("@@ [0-9.E-]+")
    bar = re.compile("( )*\|( )*")
    with open(bnf_file, "r") as f:
        bnf_list = f.readlines()
    if suffix == ".json":
        for line in bnf_list:
            if line == '\n':
                continue
            else:
                line = codecs.decode(line, 'unicode_escape')
                splited_line = line.split(' = ', 1)
                rule_name = splited_line[0]
                pcfg[rule_name] = []
                derivations = re.split(prob_pattern, splited_line[1])
                # print("derivations:", derivations)

                prob_list_raw = prob_simple.findall(splited_line[1])
                # print("prob_list_raw:", prob_list_raw)
                prob_num = 0
                for words in derivations:
                    if words in [';\n', ''] or bar.match(words) is not None:
                        pass
                    else:
                        word_list = words.split(' ')
                        # print("word_list:", word_list)
                        i = 0
                        while(i < len(word_list)):
                            if len(word_list[i]) == 0:
                                del(word_list[i])
                            else:
                                if i+2 <= len(word_list) and word_list[i:i+2] == ['"', '"']:
                                    word_list[i:i+2] = " "
                                i += 1
                        # print("word_list_final:", word_list)
                        pcfg[rule_name].append(
                            [word_list, prob_num, float(prob_list_raw[prob_num][3:])])
                        prob_num += 1
        with open("json_depths.pickle", "rb") as f:
            depths_dict = pickle.load(f)
        # print(pcfg)
        return (pcfg, depths_dict)
    elif suffix == ".css":
        print("Not implimented.")
        exit(0)
        # return pcfg, "stylesheet"
    elif suffix == ".js":
        p = re.compile('@@[ ]?[0-9\.eE\-]+')
        with open(bnf_file, "r") as f:
            lines = f.read()
            prob_list_raw = p.findall(lines)
        prob_list = []
        for i in prob_list_raw:
            prob_list.append(float(i[2:]))

        try:
            with open("../bnf/js_base.pickle", "rb") as f:
                js_dict = pickle.load(f)
        except:
            with open("/home/yunji/Project/PGFuzzer/js_approach/bnf/js_base.pickle", "rb") as f:
                js_dict = pickle.load(f)

        js_token_list = js_dict.keys()
        pointer = 0
        try:
            for token in js_token_list:
                for i in range(len(js_dict[token])):
                    if js_dict[token][i][1] == "@@":
                        js_dict[token][i][1] = prob_list[pointer]
                        pointer += 1
        except:
            print("Total prob list:", len(prob_list))
            print("now pointer:", pointer)
            exit(0)
        js_dict = trans_regexp(js_dict)
        depths_dict = calculate_depths(js_dict)

        return (js_dict, depths_dict)
    else:
        print("Not implimented.")
        exit(0)
        # return pcfg, "program"


def trans_regexp(rule_dict):
    tokens = rule_dict.keys()
    for token in tokens:
        new_expand_list = []
        worklist = []
        for expand_idx in range(len(rule_dict[token])):
            worklist.append([rule_dict[token][expand_idx][0],
                             expand_idx, rule_dict[token][expand_idx][1]])
        while worklist != []:
            work = worklist.pop()
            work_type = [type(i) for i in work[0]]
            if list in work_type:
                idx = work_type.index(list)
                worklist.append(
                    [work[0][:idx]+work[0][idx]+work[0][idx+1:]]+work[1:])
            elif tuple in work_type:
                idx = work_type.index(tuple)
                if work[0][idx][1] == "?":
                    worklist.append(
                        [work[0][:idx]+work[0][idx+1:]]+[work[1]]+[work[2]/2])
                    worklist.append(
                        [work[0][:idx]+[work[0][idx][0]]+work[0][idx+1:]]+[work[1]]+[work[2]/2])
                elif work[0][idx][1] == "*":
                    worklist.append(
                        [work[0][:idx]+work[0][idx+1:]]+[work[1]]+[work[2]/3])
                    worklist.append(
                        [work[0][:idx]+[work[0][idx][0]]+work[0][idx+1:]]+[work[1]]+[work[2]/3])
                    worklist.append(
                        [work[0][:idx]+[work[0][idx][0]]+[work[0][idx][0]]+work[0][idx+1:]]+[work[1]]+[work[2]/3])
                elif work[0][idx][1] == "+":
                    worklist.append(
                        [work[0][:idx]+[work[0][idx][0]]+work[0][idx+1:]]+[work[1]]+[work[2]/3])
                    worklist.append(
                        [work[0][:idx]+[work[0][idx][0]]+[work[0][idx][0]]+work[0][idx+1:]]+[work[1]]+[work[2]/3])
                    worklist.append([work[0][:idx]+[work[0][idx][0]]+[work[0]
                                                                      [idx][0]]+[work[0][idx][0]]+work[0][idx+1:]]+[work[1]]+[work[2]/3])
                if work[0][idx][1] == "|":
                    temp = work[0][idx][0]
                    for i in temp:
                        worklist.append(
                            [work[0][:idx]+[i]+work[0][idx+1:]]+[work[1]]+[work[2]/len(temp)])
            else:
                if work[0] == []:
                    work[0].append("")
                new_expand_list.append(work)
        rule_dict[token] = new_expand_list
    return rule_dict


def count_none(depths_dict):
    tokens = depths_dict.keys()
    counter = [depths_dict[i][1] for i in tokens].count(None)
    for token in tokens:
        counter += [i[1] for i in depths_dict[token][0]].count(None)
    return counter


def calculate_depths(rule_dict):
    depths_dict = {}
    tokens = rule_dict.keys()
    for token in tokens:
        new_expand_list = []
        for i in rule_dict[token]:
            new_expand_list.append([i[0], None])
        depths_dict[token] = (new_expand_list, None)
    minimum_cut = 0
    count_None = count_none(depths_dict)
    while count_None > 0:
        old_count_None = count_None
        for token in tokens:
            for expand_idx in range(len(depths_dict[token][0])):
                if depths_dict[token][0][expand_idx][1] is None:
                    if token in depths_dict[token][0][expand_idx][0]:
                        depths_dict[token][0][expand_idx][1] = 999
                    else:
                        max_depth = 0
                        for term in depths_dict[token][0][expand_idx][0]:
                            if term in tokens:
                                temp = depths_dict[term][1]
                                if temp is None:
                                    max_depth = None
                                else:
                                    if max_depth is not None and temp > max_depth:
                                        max_depth = temp
                        if max_depth is not None:
                            depths_dict[token][0][expand_idx][1] = max_depth
            max_depth_list = [i[1] for i in depths_dict[token][0]]
            if depths_dict[token][1] is None and minimum_cut in max_depth_list:
                depths_dict[token] = (depths_dict[token][0], minimum_cut+1)
            elif None not in max_depth_list:
                depths_dict[token] = (
                    depths_dict[token][0], min(max_depth_list)+1)
        count_None = count_none(depths_dict)
        if old_count_None == count_None:
            minimum_cut += 1

    return depths_dict


def main(rule_dict, depths_dict, config, input_num, output_dir, pruning_list):
    for key, value in rule_dict.items():
        rule_dict[key] = normalize_prob(value)

    generator = InputGenerator(
        rule_dict, depths_dict, config, pruning_list, log=False)
    pbar = tqdm(total=input_num, desc="Generating", leave=False)
    new_inputs, counted_pruning_list = generator.generate_input(
        input_num, pbar)
    pbar.close()
    for i in range(input_num):
        input_num_string = str(i).zfill(8)
        with open(output_dir+"/"+input_num_string + config["extension"], "w") as f:
            f.write(new_inputs[i][0])
        with open(output_dir+"/"+input_num_string + ".txt", "w") as f:
            f.write(pprint_tree(new_inputs[i][1]))
        with open(output_dir+"/"+input_num_string + ".pickle", "wb") as f:
            pickle.dump(new_inputs[i][1], f)
        with open(output_dir+"/"+input_num_string + "_used_rules.pickle", "wb") as f:
            pickle.dump(new_inputs[i][3], f)
    print("Done.")
    return counted_pruning_list


def parse_args(suffix, output_dir, max_depths, input_num, rule_dict, depths_dict, pruning_list):
    input_num = input_num
    output_dir = output_dir
    if not os.path.isdir(output_dir):
        os.system("mkdir "+output_dir)
    start_rule = list(rule_dict.keys())[0]
    config = {
        "extension": suffix,
        "start_rule": start_rule,
        "max_depths": max_depths
    }

    return main(rule_dict, depths_dict, config, input_num, output_dir, pruning_list)
