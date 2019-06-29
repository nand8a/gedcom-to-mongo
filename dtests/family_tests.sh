#!/bin/bash

. setup.sh

#TODO this test should really test the embedded database - but actually - all of this should move to python auditor
query="$query_preamble"'.count()'
if ! diff <( cat "$GEDCOMFILE" | grep -E '^0 .*[0-9]+. FAM' | wc -l ) <( mongocmd "'$query'" | tail -n -1 ); then
	echo "FAILURE of fam counts"
fi

