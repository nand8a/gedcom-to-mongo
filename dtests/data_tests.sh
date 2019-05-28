#!/bin/bash


function usage() {
    cat <<EOF
    Usage: $0 GEDCOMFILE DBNAME COLLNAME [IP_ADDR, PORT]
    
    1) GEDCOMFILE       A file in GEDCOM format
    2) DBNAME           MongoDB database name
    3) COLLNAME	        MongoDB collection name

    optional:
        IPADDR          IP address of mongo server
        PORT            Port of mongo server
    
    example:
        $0 myfile.ged mydatabase mycollection 37.139.15.22 27017
EOF
}



if [ $# -lt 3 ]; then
	echo -e '\nERROR: invalid number of arguments\n'
	usage
	exit 1
fi


GEDCOMFILE=$1; shift;
DBNAME=$1; shift;
COLLNAME=$1; shift;


while ! [ -z "$1" ]; do
	if [[ "$1" == *"."* ]]; then IPADDR=$1; else PORT=$1; fi; 
	shift;
done


function mongocmd() {
	# pass in the file to load, it gets the ipaddr and the port from env
	cmd='mongo '
	if ! [ -z "$IPADDR" ]; then
		cmd="$cmd --host $IPADDR"
	fi
	if ! [ -z "$PORT" ]; then
		cmd="$cmd --port $PORT"
	fi
	cmd="$cmd --eval $1"
	eval "$cmd"
}

query_preamble="db = db.getSiblingDB(\"$DBNAME\"); db.getCollection(\"$COLLNAME\")"
query="$query_preamble"'.find({"name.name": {$regex: "^Maria.*"}}, {"name.name": 1, "_id": 0}).forEach( function(elem) { print( elem.name.name ); } )'


if ! diff <( cat "$GEDCOMFILE" | grep NAME | sed -e 's/1 NAME //'g | grep -E ^Maria | wc -l ) <( mongocmd "'$query'" | grep -E ^Maria | wc -l ); then 
	echo "FAILURE of counting names starting with Maria"
fi
