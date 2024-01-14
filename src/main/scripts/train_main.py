#!/usr/bin/env python
import os
import subprocess
import optparse
import Generator
import pickle
from itertools import product
import time

###############################
### Generate & Test Inputs. ###
###############################

def generate_input_files(current_generation, pruning_list, rule_dict, depths_dict):
    current_generation_directory = "run-" + str(current_generation).zfill(5)
    current_generation_path = os.path.join(baseDirectory, current_generation_directory)
    os.mkdir(current_generation_path, 0o755)

    Generator.parse_args(
        "." + fileExtension,
        current_generation_path + "/samples",
        20,
        number_individuals,
        rule_dict,
        depths_dict,
        pruning_list,
    )
    print("Generated input files.")


def create_csv(best_generation, subject):
    input_files_directory = "run-" + str(best_generation).zfill(5) + "/samples"
    csv_files_directory = "run-" + str(best_generation).zfill(5) + "/csv"

    input_files = os.path.join(baseDirectory, input_files_directory)
    csv_files = os.path.join(baseDirectory, csv_files_directory)
    if not os.path.isdir(csv_files):
        os.mkdir(csv_files, 0o755)

    error_code_file = os.path.join(
        baseDirectory, "run-" + str(best_generation).zfill(5), "error_code.txt"
    )

    if is_java:
        for i in range(number_individuals):
            input_name = input_files + "/" + str(i).zfill(8) + "." + fileExtension
            csv_name = csv_files + "/" + str(i).zfill(8) + ".csv"
            if not os.path.isfile(csv_name):
                subprocess.call(
                    [
                        "java",
                        "-jar",
                        "../tools/coverage-analyser.jar",
                        str(subject),
                        "file-coverage-l",
                        input_name,
                        csv_name,
                    ]
                )
        return

    for i in range(number_individuals):
        os.system("find " + test_dir + ' -name "*.gcda" -exec rm {} \;')
        input_name = input_files + "/" + str(i).zfill(8) + "." + fileExtension
        info_name = csv_files + "/" + str(i).zfill(8) + ".info"
        try:
            error_code = subprocess.run(
                [test_pgm, input_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5,
            ).returncode
        except:
            error_code = -999
        with open(error_code_file, "a") as f:
            f.write(str(i).zfill(8) + " : " + str(error_code) + "\n")

        os.system("lcov -c --directory " + test_dir + " --output-file " + info_name)


def test_input_files(input_set_list, subject, info_num, start_time):
    if is_java:
        cov_vec = []
        for current_generation in input_set_list:
            input_files_directory = (
                "run-" + str(current_generation).zfill(5) + "/samples"
            )
            input_files = os.path.join(baseDirectory, input_files_directory)

            result_csv = os.path.join(
                baseDirectory, "run-" + str(current_generation).zfill(5), "results.csv"
            )
            subprocess.call(
                [
                    "java",
                    "-jar",
                    "../tools/coverage-analyser.jar",
                    str(subject),
                    "file-coverage-all",
                    input_files,
                    result_csv,
                ]
            )
            with open(result_csv, "r") as f:
                cov_txt = f.readlines()

            exception_list = []
            for i in range(1, number_individuals + 1):
                exception_list.append(cov_txt[i].split(",")[-1][:-1])
            if exception_list[0] == "1":
                os.system(
                    "cp "
                    + input_files
                    + "/"
                    + str(0).zfill(8)
                    + "."
                    + fileExtension
                    + " "
                    + list_dir
                    + "/error/"
                    + str(info_num)
                    + "_"
                    + str(current_generation)
                    + "_"
                    + str(0)
                    + "."
                    + fileExtension
                )
            for i in range(number_individuals - 1):
                if exception_list[i] != exception_list[i + 1]:
                    input_name = (
                        input_files + "/" + str(i + 1).zfill(8) + "." + fileExtension
                    )
                    os.system(
                        "cp "
                        + input_name
                        + " "
                        + list_dir
                        + "/error/"
                        + str(info_num)
                        + "_"
                        + str(current_generation)
                        + "_"
                        + str(i + 1)
                        + "."
                        + fileExtension
                    )

            result_csv = os.path.join(
                baseDirectory, "run-" + str(current_generation).zfill(5), "results.csv"
            )
            subprocess.call(
                [
                    "java",
                    "-jar",
                    "../tools/coverage-analyser.jar",
                    str(subject),
                    "file-coverage-l",
                    input_files,
                    result_csv,
                ]
            )
            with open(result_csv, "r") as f:
                cov = f.read()

            cov_str = ""
            for k in range(len(cov)):
                if k + 2 > len(cov):
                    break
                elif cov[k : k + 2] == "NO":
                    cov_str += "0"
                elif k + 3 > len(cov):
                    break
                elif cov[k : k + 3] == "YES":
                    cov_str += "1"
                else:
                    continue

            if cov_vec == []:
                for k in range(len(cov_str)):
                    cov_vec.append(cov_str[k])
            else:
                for k in range(len(cov_str)):
                    if cov_str[k] == "1":
                        cov_vec[k] = "1"

        result_info_file = os.path.join(
            list_dir, "coverage", str(info_num).zfill(5) + "_cov.pickle"
        )
        with open(result_info_file, "wb") as f:
            pickle.dump(cov_vec, f)

        with open(os.path.join(list_dir, "time.txt"), "a") as f:
            f.write(
                str(info_num).zfill(5)
                + "_cov.pickle end time : "
                + str(time.time() - start_time)
                + "\n"
            )
        return cov_vec

    os.system("find " + test_dir + ' -name "*.gcda" -exec rm {} \;')
    for current_generation in input_set_list:
        input_files_directory = "run-" + str(current_generation).zfill(5) + "/samples"
        input_files = os.path.join(baseDirectory, input_files_directory)

        to = 5

        for i in range(number_individuals):
            input_name = input_files + "/" + str(i).zfill(8) + "." + fileExtension
            try:
                error_code = subprocess.run(
                    [test_pgm, input_name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=to,
                ).returncode
            except:
                error_code = 999
            if error_code < 0:
                os.system(
                    "cp "
                    + input_name
                    + " "
                    + list_dir
                    + "/error/"
                    + str(info_num)
                    + "_"
                    + str(current_generation)
                    + "_"
                    + str(i)
                    + "."
                    + fileExtension
                )

    result_info_file = os.path.join(
        list_dir, "coverage", str(info_num).zfill(5) + "_cov.info"
    )
    if subject == "JSC":
        os.system(
            "lcov -c --directory "
            + test_dir
            + " --gcov-tool /usr/bin/gcov-7 --output-file "
            + result_info_file
        )
    else:
        os.system(
            "lcov -c --directory " + test_dir + " --output-file " + result_info_file
        )

    with open(result_info_file, "r") as f:
        cov = f.readlines()

    now_file = None
    now_dict = {}
    total_dict = {}
    for l in cov:
        line = l.split(":", 1)
        if line[0] == "SF":
            now_file = line[1]
            now_dict = {}
        elif line[0] == "end_of_record\n":
            total_dict[now_file] = sorted(now_dict.items())
        elif line[0] == "DA":
            temp = line[1].split(",")
            flag = False
            if temp[-1] != "-\n" and int(temp[-1]) > 0:
                flag = True
            now_dict[str(temp[:-1])] = flag
    tuple_list = sorted(total_dict.items())

    cov_vec = []
    for _, i in tuple_list:
        for _, j in i:
            if j:
                cov_vec.append("1")
            else:
                cov_vec.append("0")

    with open(os.path.join(list_dir, "time.txt"), "a") as f:
        f.write(
            str(info_num).zfill(5)
            + "_cov.info end time : "
            + str(time.time() - start_time)
            + "\n"
        )
    return cov_vec

##############################
### Generate Pruning List. ###
##############################

def initial_total_dt(dt):
    if len(dt) == 1:
        return dt
    total_dt = [dt[0], dt[1], dt[2]]
    children = []
    for child in dt[4]:
        children.append(initial_total_dt(child))
    total_dt.append([[children, 1]])
    return total_dt


def update_total_dt(total_dt, dt):
    dt_children = []
    for i in dt[4]:
        dt_children.append(i[0])
        dt_children.append(i[1])
        dt_children.append(i[2])
    dt_updated = False
    for children_set_num in range(len(total_dt[3])):
        total_dt_children = []
        for i in total_dt[3][children_set_num][0]:
            total_dt_children.append(i[0])
            total_dt_children.append(i[1])
            total_dt_children.append(i[2])
        if dt_children == total_dt_children:
            total_dt[3][children_set_num][1] += 1
            dt_updated = True
            if len(dt[4]) == 0:
                break
            for child_num in range(len(dt[4])):
                total_dt[3][children_set_num][0][child_num] = update_total_dt(
                    total_dt[3][children_set_num][0][child_num], dt[4][child_num]
                )
            break
    if not dt_updated:
        children = []
        for child in dt[4]:
            children.append(initial_total_dt(child))
        total_dt[3].append([children, 1])
    return total_dt


def trim_dt(total_dt, trimming_cut_num):
    children_set_num = 0
    while children_set_num < len(total_dt[3]):
        if total_dt[3][children_set_num][1] < trimming_cut_num:
            del total_dt[3][children_set_num]
        else:
            for child_num in range(len(total_dt[3][children_set_num][0])):
                total_dt[3][children_set_num][0][child_num] = trim_dt(
                    total_dt[3][children_set_num][0][child_num], trimming_cut_num
                )
            children_set_num += 1
    return total_dt


def total_dt_to_dt_list(total_dt):
    result_dt_list = []
    children_set = []
    for children_set_num in range(len(total_dt[3])):
        temp_children_list = []
        for child in total_dt[3][children_set_num][0]:
            temp_children_list.append(total_dt_to_dt_list(child))
        children_set += list(product(*temp_children_list))
    for children in children_set:
        result_dt_list.append([total_dt[1], total_dt[2], children])
    if result_dt_list == []:
        result_dt_list.append([total_dt[1], total_dt[2], ()])
    return result_dt_list


def dt_to_dl_list(tree, stack):
    result = []
    [symbol_num, symbol, children] = tree
    if children != ():
        children_symbol = []
        expandible = False
        for child in children:
            children_symbol.append(child[1])
            if child[2] != ():
                expandible = True
        if expandible:
            for child in children:
                if child[2] != ():
                    result += dt_to_dl_list(
                        child, stack + [(symbol, symbol_num, children_symbol)]
                    )
        else:
            return [stack + [(symbol, symbol_num, children_symbol)]]
    return result


def initial_total_dl(dl):
    if len(dl) == 1:
        return [dl[0], 1, []]
    return [dl[-1], 1, [initial_total_dl(dl[:-1])]]


def top_down_analyze_dl(dt_list, pruning_list, parameter_set):
    total_dt = []
    for dt in dt_list:
        if total_dt == []:
            total_dt = initial_total_dt(dt)
        else:
            total_dt = update_total_dt(total_dt, dt)

    total_dt = trim_dt(total_dt, parameter_set[0] / 3 * len(dt_list))
    common_dt_list = total_dt_to_dt_list(total_dt)

    for dt in common_dt_list:
        dl_list = dt_to_dl_list(dt, [])
        checked_dl_list = []
        for dl in dl_list:
            if dl not in checked_dl_list:
                checked_dl_list.append(dl)
        dl_list = checked_dl_list
        len_list = [len(i) for i in dl_list]
        if max(len_list) == len(dl_list[-1]):
            symbol = dl_list[-1][-1][0]
            left_dl_list = dl_list[:-1]
            left_dl_list.sort()
            child = [
                dl_list[-1][-1][1],
                dl_list[-1][:-1],
                left_dl_list,
                dl_list[-1][-1][-1],
                0,
            ]
            if symbol in pruning_list and child not in pruning_list[symbol]:
                pruning_list[symbol].append(child)
            elif symbol not in pruning_list:
                pruning_list[symbol] = [child]

    return pruning_list


def remove_unused_rules(pruning_list):
    tokens = pruning_list.keys()

    for token in tokens:
        dl_idx = 0
        while dl_idx < len(pruning_list[token]):
            if pruning_list[token][dl_idx][-1] == 0:
                del pruning_list[token][dl_idx]
            else:
                dl_idx += 1

    for token in tokens:
        for dl_idx in range(len(pruning_list[token])):
            pruning_list[token][dl_idx][-1] = 0

    del_list = []
    for token in tokens:
        if pruning_list[token] == []:
            del_list.append(token)
    for token in del_list:
        del pruning_list[token]

    return pruning_list


def refine_pruning_list(pruning_list, depths_dict):
    tokens = pruning_list.keys()

    worklist = set(tokens)
    while len(worklist) > 0:
        token = worklist.pop()
        temp_dict = {}
        for dl in pruning_list[token]:
            dl_str = str((dl[0], dl[1], dl[2]))
            if dl_str in temp_dict:
                temp_dict[dl_str].append(dl[3])
            else:
                temp_dict[dl_str] = [dl[3]]
        for dl_str in temp_dict.keys():
            temp_list = []
            for i in depths_dict[token][0]:
                if i[0] not in temp_list:
                    temp_list.append(i[0])
            if len(temp_dict[dl_str]) >= len(temp_list):
                del_dl = eval(dl_str)
                if len(del_dl[1]) > 0:
                    dl_idx = 0
                    while dl_idx < len(pruning_list[token]):
                        if (
                            pruning_list[token][dl_idx][0],
                            pruning_list[token][dl_idx][1],
                            pruning_list[token][dl_idx][2],
                        ) == del_dl:
                            # print(pruning_list[token][dl_idx])
                            del pruning_list[token][dl_idx]
                        else:
                            dl_idx += 1
                    # print("del_dl:", del_dl)
                    new_dl = del_dl[1][:-1]
                    new_token = del_dl[1][-1][0]
                    new_token_num = del_dl[1][-1][1]
                    new_left_dl = del_dl[2]
                    new_pruning = del_dl[1][-1][2]
                    # print("new_dl:", new_dl)
                    # print("new_token:", new_token)
                    # print("new_token_num:", new_token_num)
                    # print("new_left_dl:", new_left_dl)
                    # print("new_pruning:", new_pruning)

                    if new_token in pruning_list:
                        pruning_list[new_token].append(
                            [new_token_num, new_dl, new_left_dl, new_pruning, 0]
                        )
                    else:
                        pruning_list[new_token] = [
                            [new_token_num, new_dl, new_left_dl, new_pruning, 0]
                        ]
                    worklist.add(new_token)

    del_list = []
    for token in tokens:
        if pruning_list[token] == []:
            del_list.append(token)
    for token in del_list:
        del pruning_list[token]

    return pruning_list


def update_pruning_list(
    before_bundle,
    before_cov_vector,
    current_generation_list,
    pruning_list,
    depths_dict,
    parameter_set,
):
    print(
        "---------------------------------------- Analyze Tests ----------------------------------------"
    )
    if before_bundle is None:
        cov_dict = {}
        total_cov_vec_list = []
        used_rule_list = []
        for current_generation in current_generation_list:
            input_files_directory = (
                "run-" + str(current_generation).zfill(5) + "/samples"
            )
            csv_files_directory = "run-" + str(current_generation).zfill(5) + "/csv"

            cov_vec_list = []
            for i in range(number_individuals):
                info_name = (
                    os.path.join(baseDirectory, csv_files_directory, str(i).zfill(8))
                    + ".info"
                )
                csv_name = (
                    os.path.join(baseDirectory, csv_files_directory, str(i).zfill(8))
                    + ".csv"
                )
                if os.path.exists(info_name):
                    print(info_name)
                    with open(info_name, "r") as f:
                        cov = f.readlines()

                    now_file = None
                    now_dict = {}
                    total_dict = {}
                    for l in cov:
                        line = l.split(":", 1)
                        if line[0] == "SF":
                            now_file = line[1]
                            now_dict = {}
                        elif line[0] == "end_of_record\n":
                            total_dict[now_file] = sorted(now_dict.items())
                        elif line[0] == "DA":
                            temp = line[1].split(",")
                            flag = False
                            if temp[-1] != "-\n" and int(temp[-1]) > 0:
                                flag = True
                            now_dict[str(temp[:-1])] = flag
                    tuple_list = sorted(total_dict.items())

                    cov_str = ""
                    for _, k in tuple_list:
                        for _, j in k:
                            if j:
                                cov_str += "1"
                            else:
                                cov_str += "0"
                elif os.path.exists(csv_name):
                    with open(csv_name, "r") as f:
                        cov = f.read()

                    cov_str = ""
                    for k in range(len(cov)):
                        if k + 2 > len(cov):
                            break
                        elif cov[k : k + 2] == "NO":
                            cov_str += "0"
                        elif k + 3 > len(cov):
                            break
                        elif cov[k : k + 3] == "YES":
                            cov_str += "1"
                        else:
                            continue
                cov_vec_list.append(cov_str)
                total_cov_vec_list.append(cov_str)

                used_rule_file_name = (
                    os.path.join(baseDirectory, input_files_directory, str(i).zfill(8))
                    + "_used_rules.pickle"
                )
                with open(used_rule_file_name, "rb") as f:
                    used_rules = pickle.load(f)
                used_rule_list.append(used_rules)
            print("cov_vec_list Done.")

            for i in range(number_individuals):
                if cov_vec_list[i] in cov_dict:
                    cov_dict[cov_vec_list[i]].append([current_generation, i])
                else:
                    cov_dict[cov_vec_list[i]] = [[current_generation, i]]

        result_tuple = sorted(cov_dict.items(), key=f1, reverse=False)
        result = []
        for i in result_tuple:
            result.append([i[0], i[1]])

        total_cov = []
        for cov in total_cov_vec_list:
            if total_cov == []:
                total_cov = list(cov)
            else:
                for i in range(len(total_cov)):
                    if len(cov) > i and cov[i] == "1":
                        total_cov[i] = "1"

        base_pruning_list = remove_unused_rules(pruning_list)
    else:
        result = before_bundle[0]
        base_pruning_list = before_bundle[1]

    top_k_cluster = result[:cluster_top_k]
    pruning_list = copy_pruning_list(base_pruning_list)

    # merge clusters
    left_cluster = result[cluster_top_k:]
    for cluster_num in range(cluster_top_k):
        print("Original cluster :", len(top_k_cluster[cluster_num][1]))
        # print("\t", top_k_cluster[cluster_num][1])
        diff_list = []
        for i in left_cluster:
            diff_list.append(cov_diff(top_k_cluster[cluster_num][0], i[0]))
        while True:
            min_diff_index = diff_list.index(min(diff_list))
            if diff_list[min_diff_index] < parameter_set[1]:
                print(
                    "Selected cluster's diff :",
                    diff_list[min_diff_index],
                    "/",
                    len(top_k_cluster[cluster_num][1]),
                    "+",
                    len(left_cluster[min_diff_index][1]),
                )
                top_k_cluster[cluster_num][1] += left_cluster[min_diff_index][1]
                # diff_list[min_diff_index] = 99999
                del diff_list[min_diff_index]
                del left_cluster[min_diff_index]
            else:
                break
        print("Cluster", cluster_num, "Done.\n")

    counter = 0
    for cluster in top_k_cluster:
        dl_list = []
        for i in cluster[1]:
            input_files_directory = "run-" + str(i[0]).zfill(5) + "/samples"
            dt_file_name = (
                os.path.join(baseDirectory, input_files_directory, str(i[1]).zfill(8))
                + ".pickle"
            )
            with open(dt_file_name, "rb") as f:
                dl_list.append(pickle.load(f))
        pruning_list = top_down_analyze_dl(dl_list, pruning_list, parameter_set)
        counter += 1

    pruning_list = refine_pruning_list(pruning_list, depths_dict)

    return (result, base_pruning_list), pruning_list

######################
### Util Functions ###
######################

def count_cov_func(cov):
    total_count_cov = 0
    for i in cov:
        if i == "1":
            total_count_cov += 1
    return total_count_cov


def choose_parameter_set(before_parameter_set):
    if before_parameter_set[0] < 0:
        exit(0)
    else:
        return (
            before_parameter_set[0] - capturing_para,
            before_parameter_set[1] + clustering_para,
        )


def cov_diff(cov1, cov2):
    diff = 0
    cov1_len = len(cov1)
    cov2_len = len(cov2)
    if cov1_len < cov2_len:
        for i in range(cov1_len):
            if cov1[i] != cov2[i]:
                diff += 1
        diff += cov2_len - cov1_len
    else:
        for i in range(cov2_len):
            if cov1[i] != cov2[i]:
                diff += 1
        diff += cov1_len - cov2_len
    return diff


def copy_pruning_list(pruning_list):
    new_pruning_list = {}
    tokens = pruning_list.keys()
    for token in tokens:
        temp_list = []
        for i in pruning_list[token]:
            temp_list.append(i)
        new_pruning_list[token] = temp_list
    return new_pruning_list


def f1(x):
    return -len(x[1])


def remove_empty_lines(filename):
    if not os.path.isfile(filename):
        print("{} does not exist ".format(filename))
        return
    with open(filename) as file:
        lines = file.readlines()

    with open(filename, "w") as file:
        lines = filter(lambda x: x.strip(), lines)
        file.writelines(lines)

######################
### Main Functions ###
######################

def run(rule_dict, depths_dict, subject):
    start_time = time.time()
    now_parameter_set = (1.0, 0)
    before_pruning_list_name = "-"
    now_pruning_list_name = None
    before_bundle = None
    pruning_list = {}

    os.system('rm -rf "./results/' + subject + '/Iteration-1"')
    os.system('mkdir "./results/' + subject + '/Iteration-1"')
    for current_generation in range(10):
        generate_input_files(current_generation, {}, rule_dict, depths_dict)
    before_cov_vec = test_input_files(range(10), subject, 0, start_time)
    before_cov_count = count_cov_func(before_cov_vec)
    with open(os.path.join(list_dir, "time.txt"), "a") as f:
        f.write(
            str(0).zfill(5)
            + "_cov.info end time : "
            + str(time.time() - start_time)
            + "\n"
        )
    logs = "--------------------------------------------------------------\n"
    logs += "base naive coverage : " + str(before_cov_count) + "\n"
    with open(list_dir + "/logs.txt", "a") as f:
        f.write(logs)

    for current_generation in range(10):
        create_csv(current_generation, subject)

    info_num = 1
    para_flag = 1
    while True:
        before_bundle, pruning_list = update_pruning_list(
            before_bundle,
            before_cov_vec,
            range(10),
            pruning_list,
            depths_dict,
            now_parameter_set,
        )
        now_pruning_list_name = (
            list_dir
            + "/pruning_list_"
            + str(info_num)
            + "_"
            + str(now_parameter_set[0])
            + "_"
            + str(now_parameter_set[1])
            + ".pickle"
        )
        with open(now_pruning_list_name, "wb") as f:
            pickle.dump(pruning_list, f)
        logs = "--------------------------------------------------------------\n"
        logs += "base pruning list : " + before_pruning_list_name + "\n"
        os.system("cp " + before_pruning_list_name + " ../create_pl/1_best.pickle")
        logs += "parameter set : " + str(now_parameter_set) + "\n"
        logs += "new pruning list name : " + now_pruning_list_name + "\n"
        with open(list_dir + "/logs.txt", "a") as f:
            f.write(logs)

        os.system('rm -rf "./results/' + subject + '/Iteration-1"')
        os.system('mkdir "./results/' + subject + '/Iteration-1"')
        for current_generation in range(10):
            generate_input_files(
                current_generation, pruning_list, rule_dict, depths_dict
            )
        new_cov_vec = test_input_files(range(10), subject, info_num, start_time)
        new_cov_count = count_cov_func(new_cov_vec)

        logs = "\n"
        logs += now_pruning_list_name + " : " + str(new_cov_count) + "\n"
        logs += "base pruning list coverage : " + str(before_cov_count) + "\n"

        if before_cov_count > new_cov_count:
            if para_flag == max_para_flag:
                now_parameter_set = choose_parameter_set(now_parameter_set)
                logs += "parameter set updated\n"
                para_flag = 1
            else:
                logs += (
                    "parameter set not updated ( "
                    + str(para_flag)
                    + " / "
                    + str(max_para_flag)
                    + " )\n"
                )
                para_flag += 1
            with open(list_dir + "/logs.txt", "a") as f:
                f.write(logs)
        else:
            logs += "pruning list updated\n"
            with open(list_dir + "/logs.txt", "a") as f:
                f.write(logs)
            before_cov_count = new_cov_count
            before_pruning_list_name = now_pruning_list_name
            for current_generation in range(10):
                create_csv(current_generation, subject)
            before_bundle = None

        info_num += 1


if __name__ == "__main__":
    # Parser Options
    parser = optparse.OptionParser()
    parser.add_option("-p", "--outDir", type="string", dest="outdir")
    parser.add_option("-e", "--fileExtension", type="string", dest="fileExt")
    parser.add_option("-s", "--subject", type="string", dest="sub")
    parser.add_option("-l", "--list_dir", type="string", dest="list_dir")
    parser.add_option("-j", "--is_java", action="store_true", dest="is_java", default=False)
    parser.add_option("--path", type="string", dest="test_dir")
    parser.add_option("--pgm", type="string", dest="test_pgm")
    (options, args) = parser.parse_args()

    subject = options.sub
    list_dir = options.list_dir
    fileExtension = options.fileExt
    baseDirectory = os.path.join(os.getcwd(), options.outdir)

    is_java = options.is_java
    if is_java:
        test_dir = None
        test_pgm = None
    else:
        test_dir = options.test_dir
        test_pgm = options.test_pgm
        
    # Parameters
    number_individuals = 200
    cluster_top_k = 10
    update_sequence = 10
    best_generation_k = 10

    clustering_para = 1
    capturing_para = 0.01
    max_para_flag = 3

    # bnf_file_name_1 = "../bnf/"+fileExtension+"_prob.bnf"
    bnf_file_name_1 = "../bnf/" + fileExtension + "_random.bnf"

    remove_empty_lines(bnf_file_name_1)
    (rule_dict, depths_dict) = Generator.parse_bnf(bnf_file_name_1, "." + fileExtension)
    run(rule_dict, depths_dict, subject)
