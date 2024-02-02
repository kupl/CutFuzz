import test
import capture
import optparse
import os
import subprocess


def run_capture(opt):
    if not os.path.isdir(opt.result_dir):
        os.mkdir(opt.result_dir)
    if os.path.isdir(os.path.join(opt.result_dir, "capture_data")):
        os.system("rm -rf " + os.path.join(opt.result_dir, "capture_data"))
    os.mkdir(os.path.join(opt.result_dir, "capture_data"))
    os.mkdir(os.path.join(opt.result_dir, "capture_data", "coverage"))
    os.mkdir(os.path.join(opt.result_dir, "capture_data", "error"))
    if os.path.isdir(os.path.join(opt.result_dir, "test_data")):
        os.system("rm -rf " + os.path.join(opt.result_dir, "test_data"))
    os.mkdir(os.path.join(opt.result_dir, "test_data"))

    if opt.benchmark in ["JerryScript", "Jsish", "QuickJS"] and (
        opt.test_dir is None or opt.test_pgm is None
    ):
        print("Please input test directory and program")
        exit(1)

    if opt.benchmark in ["JerryScript", "Jsish", "QuickJS"]:
        file_extension = "js"
        test_pgm = opt.test_pgm
    else:
        file_extension = "json"
        test_pgm = "java"

    if opt.benchmark == "Rhino":
        file_extension = "js"

    subprocess.call(
        f"timeout {str(opt.capture_time)} python3 capture.py --benchmark {opt.benchmark} --fileExtension {file_extension} --use_pcfg {str(opt.use_pcfg)} --list_dir {os.path.join(opt.result_dir, 'capture_data')} --result_dir {os.path.join(opt.result_dir, 'test_data')} --n_top {str(opt.n_top)} --n_chance {str(opt.n_chance)} --n_num {str(opt.n_num)} --test_dir {opt.test_dir} --test_pgm {test_pgm}",
        shell=True,
        stderr=subprocess.STDOUT,
    )

    pruning_list = os.path.join(opt.result_dir, "pruning_list.pickle")
    print("Capture finished")
    return pruning_list


def run_test(opt, pruning_list):
    if not os.path.isdir(opt.result_dir):
        os.mkdir(opt.result_dir)

    if os.path.isdir(os.path.join(opt.result_dir, "test_data")):
        os.system("rm -rf " + os.path.join(opt.result_dir, "test_data"))
    os.mkdir(os.path.join(opt.result_dir, "test_data"))

    if opt.benchmark in ["JerryScript", "Jsish", "QuickJS"] and (
        opt.test_dir is None or opt.test_pgm is None
    ):
        print("Please input test directory and program")
        exit(1)

    if opt.benchmark in ["JerryScript", "Jsish", "QuickJS"]:
        file_extension = "js"
        test_pgm = opt.test_pgm
    else:
        file_extension = "json"
        test_pgm = "java"

    if opt.benchmark == "Rhino":
        file_extension = "js"

    for iter in range(1, opt.test_run_num + 1):
        os.mkdir(os.path.join(opt.result_dir, "test_data", "iteration-" + str(iter)))
        subprocess.call(
            f"timeout {str(opt.test_time)} python3 test.py --benchmark {opt.benchmark} --fileExtension {file_extension} --use_pcfg {str(opt.use_pcfg)} --result_dir {os.path.join(opt.result_dir, 'test_data', 'iteration-' + str(iter))} --n_num {str(opt.n_num)} --test_dir {opt.test_dir} --test_pgm {test_pgm} --pruning_list {pruning_list}",
            shell=True,
            stderr=subprocess.STDOUT,
        )

    subprocess.call(
        f"python3 analyseResults.py --subject {opt.benchmark} --run_dir {os.path.join(opt.result_dir, 'test_data')} --test_run_num {str(opt.test_run_num)}",
        shell=True,
        stderr=subprocess.STDOUT,
    )

    print("Test finished")

    return


if __name__ == "__main__":
    # benchmark - Required
    # use_pcfg - default: False
    # run_capture - default: True
    # capture_time - default: 43200
    # run_test - default: True
    # test_time - default: 43200
    # test_run_num - default: 5
    # prunint_list - required: run_capture=False, run_test=True
    # result_dir - default: results
    # n_top - default: 10
    # n_chance - default: 3
    # n_num - default: 2000
    # test_dir
    # test_pgm

    # benchmarks: JerryScript, Jsish, QuickJS, Rhino, Argo, Genson, Gson, JsonToJava

    # output: covered lines number

    parser = optparse.OptionParser()
    parser.add_option(
        "--benchmark",
        dest="benchmark",
        help="Available benchmark: JerryScript, Jsish, QuickJS, Rhino, Argo, Genson, Gson, JsonToJava",
    )
    parser.add_option(
        "--use_pcfg",
        dest="use_pcfg",
        action="store_true",
        default=False,
        help="Use Probabilistic Grammar instead of random grammar (Default: False)",
    )
    parser.add_option(
        "--run_capture",
        dest="run_capture",
        action="store_true",
        default=False,
        help="Run capture (Default: False)",
    )
    parser.add_option(
        "--capture_time",
        dest="capture_time",
        type="int",
        default=43200,
        help="Capture time(sec) (Default: 43200 = 12h)",
    )
    parser.add_option(
        "--run_test",
        dest="run_test",
        action="store_true",
        default=False,
        help="Run test (Default: False)",
    )
    parser.add_option(
        "--test_time",
        dest="test_time",
        type="int",
        default=43200,
        help="Test time(sec) (Default: 43200 = 12h)",
    )
    parser.add_option(
        "--test_run_num",
        dest="test_run_num",
        type="int",
        default=5,
        help="Number of test run (Default: 5)",
    )
    parser.add_option(
        "--pruning_list", dest="pruning_list", help="Pruning list for test"
    )
    parser.add_option(
        "--result_dir",
        dest="result_dir",
        default="results",
        help="Result directory (Default: results)",
    )
    parser.add_option(
        "--n_top",
        dest="n_top",
        type="int",
        default=10,
        help="Hyperparameter: n_top (Default: 10)",
    )
    parser.add_option(
        "--n_chance",
        dest="n_chance",
        type="int",
        default=3,
        help="Hyperparameter: n_chance (Default: 3)",
    )
    parser.add_option(
        "--n_num",
        dest="n_num",
        type="int",
        default=2000,
        help="Hyperparameter: n_num (Default: 2000)",
    )
    parser.add_option(
        "--test_dir",
        dest="test_dir",
        help="Directory to capture coverage data (Required to test JerryScript, Jsish, or QuickJS)",
    )
    parser.add_option(
        "--test_pgm",
        dest="test_pgm",
        help="Program to run (Required to test JerryScript, Jsish, or QuickJS)",
    )

    (options, args) = parser.parse_args()

    if options.benchmark is None:
        print("Please input benchmark name")
        exit(1)

    if not options.run_capture and not options.run_test:
        print("Please set run_capture or run_test")
        exit(1)

    if options.run_capture:
        pruning_list = run_capture(options)
    else:
        pruning_list = options.pruning_list

    if options.run_test:
        run_test(options, pruning_list)
