
show dbs;
use gedcom;
db.getCollection('person_duplessis').find({'name.name': {$regex: '^Maria.*'}}, {'name.name': 1, '_id': 0}).forEach( function(elem) { print( elem.name.name ); } );
