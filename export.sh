#!/bin/bash


function usage() {
    cat <<EOF
    Usage: $0 IPADDR PORT DBNAME COLLNAME FIELDFILE 

    Simple wrapper of mongoexport.

    1) IPADDR          IP address of mongo server
    2) PORT            Port of mongo server
    3) DBNAME          MongoDB database name
    4) COLLNAME	       MongoDB collection name
    5) FIELDFILE       A file denoting the fields to export 	


    example:
        $0 export.sh 37.139.15.22 27017 mydatabase mycollection
EOF
}


if [ $# -lt 5 ]; then
	echo -e '\nERROR: invalid number of arguments\n'
	usage
	exit 1
fi


IPADDR=$1; shift;
PORT=$1; shift;
DBNAME=$1; shift;
COLLNAME=$1; shift;
FIELDFILE=$1; shift;


mongoexport -h $IPADDR -p $PORT  -d $DBNAME -c $COLLNAME --type=csv --fieldFile $FIELDFILE --out ${COLLNAME}_ged_$(date +%Y%m%d).csv
