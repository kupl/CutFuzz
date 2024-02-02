#!/usr/bin/env python
import glob
import os
import optparse
import json
import pickle


def getAllfiles(fileLocation, extension):
    files = "*." + extension

    iter_files = fileLocation + "/*/" + files

    itemlist = glob.glob(iter_files)
    return itemlist


def addExceptionsGlobalList(exceptions):
    for exception in exceptions:
        if exceptionsGlobal.count(exception) > 0:
            exceptionDictGlobal[exception] = exceptionDictGlobal[exception] + 1
        else:
            exceptionsGlobal.append(exception)
            exceptionDictGlobal[exception] = 1


def getExceptions(iteration):
    exceptionFiles = getAllfiles(
        run_dir + "/iteration-" + str(iteration) + "/", "exceptions"
    )

    exceptions = list()
    for x in exceptionFiles:
        with open(str(x), "r") as read_file:
            developer = json.load(read_file)

            for dev in developer:
                if exceptions.count(dev["name"]) == 0:
                    exceptions.append(dev["name"])

    return exceptions


def run_cov(iter_dir):
    if subject in ["JerryScript", "Jsish", "QuickJS"]:
        cov_file = os.path.join(iter_dir, "total_coverage.txt")
        with open(cov_file, "r") as f:
            cov = f.read()
        result = cov
    else:
        result = ""
        total_cov = []

        run_num = 0
        while True:
            csv_name = iter_dir + "/run-" + str(run_num).zfill(5) + "/results.pickle"
            if os.path.isfile(csv_name):
                with open(csv_name, "rb") as f:
                    cov_str = pickle.load(f)
                if total_cov == []:
                    for k in range(len(cov_str)):
                        total_cov.append(cov_str[k])
                else:
                    for k in range(len(cov_str)):
                        if cov_str[k] == "1":
                            total_cov[k] = "1"

                total_count_cov = 0
                for i in total_cov:
                    if i == "1":
                        total_count_cov += 1
                result += (
                    "run-" + str(run_num).zfill(5) + " : " + str(total_count_cov) + "\n"
                )
                run_num += 1
            else:
                break
    return result


def printResults():
    print("--------------------------------------")
    print("Coverage:")
    for iteration in range(1, test_run_num + 1):
        cov_text_name = os.path.join(
            run_dir, "iteration-" + str(iteration) + "_cov.txt"
        )
        with open(cov_text_name, "r") as f:
            cov = f.read()
        (
            print(
                "iteration-"
                + str(iteration)
                + " : "
                + cov.split("\n")[-1]
                + " lines covered"
            )
        )
    print("--------------------------------------")
    print("Exceptions:")
    for key in exceptionDictGlobal:
        print(
            str(key) + " : " + str(exceptionDictGlobal[key]) + " / " + str(test_run_num)
        )

    print("--------------------------------------")


if __name__ == "__main__":
    # Parser Options
    parser = optparse.OptionParser()
    parser.add_option("-s", "--subject", type="string", dest="sub")
    parser.add_option("-d", "--run_dir", type="string", dest="run_dir")
    parser.add_option("-t", "--test_run_num", type="int", dest="test_run_num")
    (options, args) = parser.parse_args()

    subject = options.sub
    run_dir = options.run_dir
    test_run_num = options.test_run_num

    exceptionsGlobal = list()
    exceptionDictGlobal = {}

    for iteration in range(1, test_run_num + 1):
        exceptions = getExceptions(iteration)
        addExceptionsGlobalList(exceptions)
        cov_text_name = os.path.join(
            run_dir, "iteration-" + str(iteration) + "_cov.txt"
        )
        with open(cov_text_name, "w") as f:
            f.write(run_cov(run_dir + "/iteration-" + str(iteration)).strip())

    printResults()
