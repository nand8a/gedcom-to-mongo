#!/bin/bash

. setup.sh 

query="$query_preamble"'.find({"name.name": {$regex: "^Maria.*"}}, {"name.name": 1, "_id": 0}).forEach( function(elem) { print( elem.name.name ); } )'


if ! diff <( cat "$GEDCOMFILE" | grep NAME | sed -e 's/1 NAME //'g | grep -E ^Maria | wc -l ) <( mongocmd "'$query'" | grep -E ^Maria | wc -l ); then 
	echo "FAILURE of counting names starting with Maria"
fi


count=$(cat "$GEDCOMFILE" | grep -E '^0 .*[0-9]+. INDI' | wc -l)
query="$query_preamble"'.count()'
if ! diff <( echo $count) <( mongocmd "'$query'" | tail -n -1 ); then
	echo "FAILURE of indi counts"
else
    echo "✔ Count of Individuals: $count"
fi



query="$query_preamble"'.count({"birt.date": {$exists:true}}, {"_id":1})'
count=$(python src_counts.py -b 'DATE' -f "$GEDCOMFILE")
if ! diff <( echo $count ) <( mongocmd "'$query'" | tail -n  -1); then
	echo "FAILURE of birth date counts"
else
    echo "✔ Count of Birth Dates: $count"
fi

query="$query_preamble"'.count({"birt.plac": {$exists:true}}, {"_id":1})'
count=$(python src_counts.py -b 'PLAC' -f "$GEDCOMFILE")
if ! diff <( echo $count ) <( mongocmd "'$query'" | tail -n  -1); then
	echo "FAILURE of birth place counts"
else
    echo "✔ Count of Birth Place: $count"
fi



query="$query_preamble"'.count({"deat.date": {$exists:true}}, {"_id":1})'
count=$(python src_counts.py -d 'DATE ' -f "$GEDCOMFILE")
if ! diff <( echo $count ) <( mongocmd "'$query'" | tail -n  -1); then
	echo "FAILURE of death date counts"
else
    echo "✔ Count of Death Dates: $count"
fi

query="$query_preamble"'.count({"deat.plac": {$exists:true}}, {"_id":1})'
count=$(python src_counts.py -d 'PLAC ' -f "$GEDCOMFILE")
if ! diff <( echo $count ) <( mongocmd "'$query'" | tail -n  -1); then
	echo "FAILURE of death place counts"
else
    echo "✔ Count of Death Place: $count"
fi

