#!/bin/bash

# Full test with Random Fuzzer
python3 main.py --benchmark=JerryScript --run_capture --run_test --test_pgm=/root/benchmarks/jerryscript/build/bin/jerry --test_dir=/root/benchmarks/jerryscript/build
python3 main.py --benchmark=Jsish --run_capture --run_test --test_pgm=/root/benchmarks/jsish/jsish --test_dir=/root/benchmarks/jsish
python3 main.py --benchmark=QuickJS --run_capture --run_test --test_pgm=/root/benchmarks/QuickJS/qjs --test_dir=/root/benchmarks/QuickJS
python3 main.py --benchmark=Rhino --run_capture --run_test --test_pgm=java
python3 main.py --benchmark=Argo --run_capture --run_test --test_pgm=java
python3 main.py --benchmark=Genson --run_capture --run_test --test_pgm=java
python3 main.py --benchmark=Gson --run_capture --run_test --test_pgm=java
python3 main.py --benchmark=JsonToJava --run_capture --run_test --test_pgm=java

# Full test with Probabilistic Fuzzer
python3 main.py --benchmark=JerryScript --use_pcfg --run_capture --run_test --test_pgm=/root/benchmarks/jerryscript/build/bin/jerry --test_dir=/root/benchmarks/jerryscript/build
python3 main.py --benchmark=Jsish --use_pcfg --run_capture --run_test --test_pgm=/root/benchmarks/jsish/jsish --test_dir=/root/benchmarks/jsish
python3 main.py --benchmark=QuickJS --use_pcfg --run_capture --run_test --test_pgm=/root/benchmarks/QuickJS/qjs --test_dir=/root/benchmarks/QuickJS
python3 main.py --benchmark=Rhino --use_pcfg --run_capture --run_test --test_pgm=java
python3 main.py --benchmark=Argo --use_pcfg --run_capture --run_test --test_pgm=java
python3 main.py --benchmark=Genson --use_pcfg --run_capture --run_test --test_pgm=java
python3 main.py --benchmark=Gson --use_pcfg --run_capture --run_test --test_pgm=java
python3 main.py --benchmark=JsonToJava --use_pcfg --run_capture --run_test --test_pgm=java

# Short demo test
python3 main.py --benchmark=Rhino --run_capture --run_test --test_run_num=1 --capture_time=3600 --test_time=3600 --test_pgm=java
python3 main.py --benchmark=JerryScript --use_pcfg --run_capture --run_test --test_run_num=1 --capture_time=3600 --test_time=3600 --test_pgm=/root/benchmarks/jerryscript/build/bin/jerry --test_dir=/root/benchmarks/jerryscript/build