# CutFuzz

CutFuzz is a generation-based fuzzer that minimizes the generation of less important inputs during testing by identifying and excluding redundant production rules from the grammar.
<!-- 논문 링크/파일 추가 -->

## Installation

### Use Docker

We provide a Docker image that contains all benchmark programs and dependencies required to run CutFuzz. You can use the following command to pull the image from Docker Hub:

```bash
docker pull yunji99/cutfuzz
docker run -it yunji99/cutfuzz
```

## How to Use

Here are the options for running CutFuzz:

```bash
$ python3 main.py -h
Usage: main.py [options]

Options:
  -h, --help            show this help message and exit
  --benchmark=BENCHMARK
                        Available benchmark: JerryScript, Jsish, QuickJS,
                        Rhino, Argo, Genson, Gson, JsonToJava
  --use_pcfg            Use Probabilistic Grammar instead of random grammar
                        (Default: False)
  --run_capture         Run capture (Default: False)
  --capture_time=CAPTURE_TIME
                        Capture time(sec) (Default: 43200 = 12h)
  --run_test            Run test (Default: False)
  --test_time=TEST_TIME
                        Test time(sec) (Default: 43200 = 12h)
  --test_run_num=TEST_RUN_NUM
                        Number of test run (Default: 5)
  --pruning_list=PRUNING_LIST
                        Pruning list for test
  --result_dir=RESULT_DIR
                        Result directory (Default: results)
  --n_top=N_TOP         Hyperparameter: n_top (Default: 10)
  --n_chance=N_CHANCE   Hyperparameter: n_chance (Default: 3)
  --n_num=N_NUM         Hyperparameter: n_num (Default: 2000)
  --test_dir=TEST_DIR   Directory to capture coverage data (Required to test
                        JerryScript, Jsish, or QuickJS)
  --test_pgm=TEST_PGM   Program to run (Required to test JerryScript, Jsish,
                        or QuickJS)
```

### Capturing and testing with redundant sequences

We provide an example instruction to run CutFuzz with our benchmarks. You can use the following command to try CutFuzz shortly.

```bash
cd ~/src/main
python3 main.py --benchmark=Rhino --run_capture --run_test --test_run_num=1 --capture_time=3600 --test_time=3600 --test_pgm=java
```

This command runs CutFuzz with the Rhino benchmark and captures redundant sequences for 1 hour. Then, it tests the captured redundant sequences for 1 hour once.
To run the full tests with capturing redundant sequences, please refer to the [run.sh](src/main/run.sh) file.

### Testing with existing redundant sequences

You can test with existing redundant sequences without capturing new sequences. In this case, you additionally need to specify the ```--test_run_num``` option to specify the number of test runs.

You can use pre-captured redundant sequences files included in the ```data/pruning_lists```. For example, if you want to test with redundat sequences captured with Rhino and random fuzzer:

```bash
cd ~/src/main
python3 main.py --benchmark=Rhino --run_test --test_run_num=1 --test_time=3600 --test_pgm=java --pruning_list=../../data/pruning_lists/rhino_random.pickle
```

### Testing with other benchmarks

We provide all 8 benchmarks used in our evaluation. Here is the list of the benchmarks:

- JavaScript
  - JerryScript
  - Jsish
  - QuickJS
  - Rhino
- JSON
  - Argo
  - Genson
  - Gson
  - JsonToJava

You can select a benchmark by specifying the ```--benchmark``` option in the ```main.py``` file.
Be ware that you need to specify the ```--test_pgm``` and ```--test_dir``` options for C programs such as JerryScript, Jsish, and QuickJS to measure coverage.
For java programs, you can specify the ```--test_pgm``` option to ```java```.

For more detailed examples, please refer to the [run.sh](src/main/run.sh) file.

### Additional options

If you want to use Probabilistic Grammar or change hyperparameters, you can use ```--use_pcfg```.

You can change the hyperparameters of CutFuzz by specifying the options in the ```main.py``` file. Here is the list of the options:

- ```--n_num```: The number of inputs accumulated during each iteration
- ```--n_top```: The number of groups from which the redundant sequences are captured
- ```--n_chance```: The number of chances that that our algorithm tries to capture redundant sequences from the same parameter set

If you want to change test time budget:

- ```--capture_time```: The time budget for capturing redundant sequences in seconds
- ```--test_time```: The time budget for testing with captured redundant sequences in seconds

You can also change the number of test runs by specifying the ```--test_run_num``` option.
