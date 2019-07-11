#!/bin/bash

. setup.sh

#TODO this test should really test the embedded database - but actually - all of this should move to python auditor
query="$query_preamble"'.count()'
count=$(cat "$GEDCOMFILE" | grep -E '^0 .*[0-9]+. FAM' | wc -l)
if ! diff <( echo $count ) <( mongocmd "'$query'" | tail -n -1 ); then
	echo "FAILURE of fam counts"
else
    echo "✔ Count of Families: $count"
fi

