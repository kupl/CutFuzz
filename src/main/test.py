#!/usr/bin/env python
import os
import subprocess
import optparse
import Generator
import pickle
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


def execute_input_files(current_generation, subject):
    print(
        "---------------------------------------- Run Tests ----------------------------------------"
    )
    input_files_directory = "run-" + str(current_generation).zfill(5) + "/samples"

    input_files = os.path.join(baseDirectory, input_files_directory)

    if not is_java:
        result_info_file = os.path.join(baseDirectory, "temp_cov.info")

        to = 5

        error_code_file = os.path.join(
            baseDirectory, "run-" + str(current_generation).zfill(5), "error_code.txt"
        )
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
            with open(error_code_file, "a") as f:
                f.write(str(i).zfill(8) + " : " + str(error_code) + "\n")
            if error_code >= 0:
                os.system("rm " + input_files + "/" + str(i).zfill(8) + ".*")

        os.system(
            "lcov -c --directory " + test_dir + " --output-file " + result_info_file
        )

        with open(result_info_file, "r") as f:
            cov = f.readlines()
        cov_counter = 0
        total_counter = 0
        for l in cov:
            line = l.split(":", 1)
            if line[0] == "DA":
                temp = line[1].split(",")
                total_counter += 1
                if temp[-1] != "-\n" and int(temp[-1]) > 0:
                    cov_counter += 1

        total_cov_file = os.path.join(baseDirectory, "total_coverage.txt")
        with open(total_cov_file, "a") as f:
            f.write(
                "run-"
                + str(current_generation).zfill(5)
                + " : "
                + str(cov_counter)
                + "\n"
            )
        return
    else:
        result_csv = os.path.join(
            baseDirectory, "run-" + str(current_generation).zfill(5), "results.csv"
        )
        subprocess.call(
            f"java -jar ../tools/coverage-analyser.jar {str(subject)} file-coverage-all {input_files} {result_csv}",
            shell=True,
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
                + error_path
                + "/"
                + str(current_generation).zfill(5)
                + "_"
                + str(0).zfill(8)
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
                    + error_path
                    + "/"
                    + str(current_generation).zfill(5)
                    + "_"
                    + str(i + 1).zfill(8)
                    + "."
                    + fileExtension
                )

        result_csv = os.path.join(
            baseDirectory, "run-" + str(current_generation).zfill(5), "results.csv"
        )
        subprocess.call(
            f"java -jar ../tools/coverage-analyser.jar {str(subject)} file-coverage-l {input_files} {result_csv}",
            shell=True,
        )
        with open(result_csv, "r") as f:
            cov = f.read()
        os.system("rm -r " + input_files)

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

        result_info_file = os.path.join(
            baseDirectory, "run-" + str(current_generation).zfill(5), "results.pickle"
        )
        with open(result_info_file, "wb") as f:
            pickle.dump(cov_str, f)
        return


######################
### Util Functions ###
######################


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


def test_run(pruning_list, prob_rule_dict, depths_dict):
    time_file = os.path.join(baseDirectory, "time_record.txt")
    start_time = time.time()
    if test_dir is not None:
        os.system("find " + test_dir + ' -name "*.gcda" -exec rm {} \;')
    for current_generation in range(100000):
        generate_input_files(
            current_generation, pruning_list, prob_rule_dict, depths_dict
        )
        execute_input_files(current_generation, subject)
        with open(time_file, "a") as f:
            f.write(
                "run-"
                + str(current_generation).zfill(5)
                + " : "
                + str(time.time() - start_time)
                + "\n"
            )


if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option(
        "--benchmark",
        dest="benchmark",
    )
    parser.add_option(
        "--fileExtension",
        dest="fileExtension",
    )
    parser.add_option(
        "--use_pcfg",
        dest="use_pcfg",
        action="store_true",
    )
    parser.add_option(
        "--use_pcfg_inv",
        dest="use_pcfg_inv",
        action="store_true",
    )
    parser.add_option(
        "--result_dir",
        dest="result_dir",
    )
    parser.add_option(
        "--n_num",
        dest="n_num",
        type="int",
    )
    parser.add_option(
        "--test_dir",
        dest="test_dir",
    )
    parser.add_option(
        "--test_pgm",
        dest="test_pgm",
    )
    parser.add_option(
        "--pruning_list",
        dest="pruning_list",
    )
    (options, args) = parser.parse_args()

    subject = options.benchmark
    fileExtension = options.fileExtension
    baseDirectory = options.result_dir
    error_path = os.path.join(baseDirectory, "error")
    os.mkdir(error_path, 0o755)

    if options.test_pgm == "java":
        is_java = True
        test_dir = None
        test_pgm = None
    else:
        is_java = False
        test_dir = options.test_dir
        test_pgm = options.test_pgm

    # Parameters
    number_individuals = options.n_num // 10

    if options.use_pcfg:
        bnf_file_name = "../bnf/" + fileExtension + "_prob.bnf"
    elif options.use_pcfg_inv:
        bnf_file_name = "../bnf/" + fileExtension + "_inv.bnf"
    else:
        bnf_file_name = "../bnf/" + fileExtension + "_random.bnf"
    remove_empty_lines(bnf_file_name)
    (prob_rule_dict, depths_dict) = Generator.parse_bnf(
        bnf_file_name, "." + fileExtension
    )

    if os.path.exists(options.pruning_list):
        with open(options.pruning_list, "rb") as f:
            pruning_list = pickle.load(f)
    else:
        print("No pruning list, randomly generate inputs.")
        pruning_list = {}

    test_run(pruning_list, prob_rule_dict, depths_dict)
