#!/bin/bash

. setup.sh 

query="$query_preamble"'.find({"name.name": {$regex: "^Maria.*"}}, {"name.name": 1, "_id": 0}).forEach( function(elem) { print( elem.name.name ); } )'


if ! diff <( cat "$GEDCOMFILE" | grep NAME | sed -e 's/1 NAME //'g | grep -E ^Maria | wc -l ) <( mongocmd "'$query'" | grep -E ^Maria | wc -l ); then 
	echo "FAILURE of counting names starting with Maria"
fi

query="$query_preamble"'.count()'
if ! diff <( cat "$GEDCOMFILE" | grep -E '^0 .*[0-9]+. INDI' | wc -l ) <( mongocmd "'$query'" | tail -n -1 ); then
	echo "FAILURE of indi counts"
fi

#TODO this test should really test the embedded database - but actually - all of this should move to python auditor
#query="$query_preamble"'.count()'
#if ! diff <( cat "$GEDCOMFILE" | grep -E '^0 .*[0-9]+. FAM' | wc -l ) <( mongocmd "'$query'" | tail -n -1 ); then
#	echo "FAILURE of fam counts"
#fi

