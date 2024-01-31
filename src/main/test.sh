#!/bin/bash

FILE_EXTENSION=js
SUBJECTS=()
BUILD_PATH=
PUT=

TOTAL_RUN=1
TOTAL_MAX=2


while [ $TOTAL_RUN -lt $TOTAL_MAX ]
do

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
			# timeout 43200 python3 ./scripts/test_main.py --outDir="results/$subject/Iteration-$RUN"  --subject="$subject" --fileExtension="$FILE_EXTENSION" -j
			grep -r ": -" "./results/$subject/Iteration-$RUN/run-*/error_code.txt" > "./results/$subject/Iteration-$RUN/error_code.txt"
			true $(( RUN++ ))
		done
		RUN=1

		python3 ./scripts/analyseExceptions.py --subject="$subject"
	done

	python3 ./scripts/sumCoverage.py
	mv "./results" "./results_$TOTAL_RUN"

	true $(( TOTAL_RUN++ ))

done

echo "All done"
