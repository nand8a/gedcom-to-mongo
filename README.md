# gedcom-to-mongo

Ingest a file in GEDCOM format into MongoDB.


## Summary
Embed a lineage-linked _Genealogical Data Communication  
([GEDCOM](https://en.wikipedia.org/wiki/GEDCOM))
data model, which is structured around individuals and families, 
into a _MongoDB_ database.
 
 
An example of the GEDCOM file format is:
 
```
0 HEAD
1 SOUR PAF
2 NAME Personal Ancestral File
2 VERS 5.0
1 DATE 30 NOV 2000
1 GEDC
2 VERS 5.5
2 FORM LINEAGE-LINKED
1 CHAR ANSEL
1 SUBM @U1@
0 @I1@ INDI
1 NAME John /Smith/
1 SEX M
1 FAMS @F1@
0 @I2@ INDI
1 NAME Elizabeth /Stansfield/
1 SEX F
1 FAMS @F1@
0 @I3@ INDI
1 NAME James /Smith/
1 SEX M
1 FAMC @F1@
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
1 MARR
1 CHIL @I3@
0 @U1@ SUBM
1 NAME Submitter
0 TRLR
```

The ingestion of this file results in the following MongoDB structure:

```json
some: { json: here }
```

## Conventions
 * Keys in the GEDCOM file (e.g. `FAMS`, `NAME`, ...) are retained as keys in MongoDB,
as far as possible. The instances where this is not the case, are:
    -  sublist  
  ```
  1 NAME Judith /du Plessis/'
  2 SURN du Plessis'
  2 GIVN Judith' 
  ```

 * An individual record (e.g. `@I2@`) is currently used as the document 
 `_id` in MongoDB.
 
 * An embedded database structure is sought, but a secondary family
   database has been retained until that structure is settled on. 
   It is possible to join between the `individuals` database and this
   `family` database.


## Example MongoDB Queries


* **Q** Get all husbands and their marriage dates
```json
db.coll.aggregate([
    {
        $lookup: {
            from: "family",
            localField: "_id",
            foreignField: "husb",
            as: "husband"
        }
    },
    {
        $match: {
            "husband": {$ne: []}
        }
    },
    {
        $unwind: "$husband"
    },
    {
        $project: {"husband.marr": 1}
    }, 
])
```

* **Q**: Which town had the most marriages
```json
db.coll.aggregate([
     {
        "$match": { "PLAC": {$ne: null}}
     },
     {  
        "$group": {
            _id: "$plac",
            count: {
                $sum: 1
            }
        }
    },
    {
        "$sort": {"_id":-1}
    }
])

```

* **Q**: Average number of children per family

```json
db.coll.aggregate([
    {
        "$match":{ "chil": {$ne: null} }
    },
    {
        "$group":
        {
            "_id": "res",
            "total":
            {
                "$sum": { "$size": "$chil" }
            },
            "nr_arrays":
            {
                "$sum": 1
            }
        }
    },
    {
        "$project":
        {
              "total": 1, "nr_arrays": 1, "average": {"$divide": ["$total", "$nr_arrays"]}
        }
    }
])

```

* **Q** Get all ancestors of of an individual `@I3@`
```json
db.coll.aggregate(
    [ 
        { "$graphLookup": { 
            "from": "coll", 
            "startWith": "$parents", 
            "connectFromField": "parents", 
            "connectToField": "_id", 
            "as": "ancestors"
        }}  , 
        { "$match": { "_id": "@I3@" } }, 
        { "$addFields": { 
            "ancestors": { 
                "$reverseArray": { 
                    "$map": { 
                        "input": "$ancestors", 
                        "as": "t", 
                        "in": { "_id": "$$t._id" }
                    } 
                } 
            }
        }},
        { "$project": {"ancestors": 1}}
    ]
)
```