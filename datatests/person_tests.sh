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

query="$query_preamble"'.count({"birt.date": {$exists:true}}, {"_id":1})'
if ! diff <( python src_counts.py -b -f "$GEDCOMFILE" | wc -l) <( mongocmd "'$query'" | tail -n  -1); then
	echo "FAILURE of birth date counts"
fi

query="$query_preamble"'.count({"deat.date": {$exists:true}}, {"_id":1})'
if ! diff <( python src_counts.py -d -f "$GEDCOMFILE" | wc -l) <( mongocmd "'$query'" | tail -n  -1); then
	echo "FAILURE of death date counts"
fi