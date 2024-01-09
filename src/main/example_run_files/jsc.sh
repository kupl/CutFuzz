#!/bin/bash

FILE_EXTENSION=js
SUBJECTS=(JSC)
BUILD_PATH=/root/benchmarks/WebKit/WebKitBuild/Release
PUT=/root/benchmarks/WebKit/WebKitBuild/Release/bin/jsc

TOTAL_RUN=1
TOTAL_MAX=2


while [ $TOTAL_RUN -lt $TOTAL_MAX ]
do

	RUN=1
	MAX=2

	rm -rf "./results"
	mkdir "./results"

	for subject in "${SUBJECTS[@]}"
	do
		echo "$subject"
		mkdir "./results/$subject"

		mkdir "./automatic_loop_list_$TOTAL_RUN"
		mkdir "./automatic_loop_list_$TOTAL_RUN/error"
		mkdir "./automatic_loop_list_$TOTAL_RUN/coverage"
		echo "output: $TOTAL_RUN"
		mkdir "./results/$subject/Iteration-1"
		timeout 43200 python3 ./scripts/train_main.py --outDir="results/$subject/Iteration-1"  --subject="$subject" --fileExtension="$FILE_EXTENSION" --list_dir="./automatic_loop_list_$TOTAL_RUN" --path="$BUILD_PATH" --pgm="$PUT"

	done

	RUN=1
	MAX=6

	rm -rf "./results"
	mkdir "./results"

	for subject in "${SUBJECTS[@]}"
	do
		echo "$subject"
		mkdir "./results/$subject"
		while [ $RUN -lt $MAX ]
		do
			echo "output: $RUN"
			mkdir "./results/$subject/Iteration-$RUN"
			timeout 43200 python3 ./scripts/test_main.py --outDir="results/$subject/Iteration-$RUN"  --subject="$subject" --fileExtension="$FILE_EXTENSION" --path="$BUILD_PATH" --pgm="$PUT"
			grep -r ": -" "./results/$subject/Iteration-$RUN/run-*/error_code.txt" > "./results/$subject/Iteration-$RUN/error_code.txt"
			true $(( RUN++ ))
		done
		RUN=1

		python3 ./scripts/analyseExceptions.py --subject="$subject"
	done

	python3 ./scripts/sumCoverage.py
	mv "../create_pl/1_best.pickle" "./results/"
	mv "./results" "./results_$TOTAL_RUN"

	true $(( TOTAL_RUN++ ))

done

echo "All done"
