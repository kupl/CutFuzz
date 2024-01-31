# CutFuzz

## How to Use

Testable benchmarks:

- C programs which take JavaScript or JSON files as inputs
  - Must be compiled with GCC and coverage mode(for GCOV)
- Java programs which are Our benchmarks
  - Rhino, Argo, Genson, Gson, JsonToJava

### Full Test with capturing redundant sequences

You need to modifying run.sh to run CutFuzz

- If you are testing with our specified benchmarks, you can use example run files in ```src/main/example_run_files```
- If you are testing C programs, you must modify ```BUILD_PATH``` and ```PUT``` of run file _even if you are usig example run files_
  - BUILD_PATH: build root path of PUT to compute coverage
  - PUT: executable file that takes JavaScript / JSON files
- You must specify the ```SUBJECTS``` and ```FILE_EXTENSION``` of PUT

A single run normally takes 12 hours for capturing redundant sequences, and 5 times of 12 hours for testing with captured redundant sequences

- If you want to modify time budget, modify timeout of python3 in Line 31(for capturing) and Line 50(for testing)
  - Default: 43200 seconds = 12 hours
- If you want to modify the iteration of the test, modify ```TOTAL_MAX``` or ```MAX``` of Line 9 and 37
  - TOTAL_MAX: (total number of capture-test process) + 1
  - MAX(Line 37): (total number of test using caputred redundant sequences) + 1
  - Default: 2, 6

If you want to use Probabilistic Grammar or change hyper parameters, you need to modify main.py files in ```src/main/scripts```

### Testing with existing redundant sequences

You can just run test with existing redundant sequences without capturing new sequences

- You need to modify ```test.sh```
  - Please refer to the ```run.sh``` modification method specified above. 
- CutFuzz uses ```src/create_pl/pruning_list.pickle``` for testing
  - If this file does not exist, CutFuzz generates inputs randomly due to the input grammar
