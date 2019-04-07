[![Build Status](https://travis-ci.org/nand8a/gedcom-to-mongo.svg?branch=master)](https://travis-ci.org/nand8a/gedcom-to-mongo)


# gedcom-to-mongo

Ingest a file in GEDCOM format into MongoDB.

> [Summary](#summary)
> 
> [Execution](#execution)
>
> [Testing](#testing)
>
> [Conversion Conventions](#conversion-conventions)
> 
> [Example MongoDB Queries](#example-mongodb-queries)
>
> [Integrating with R](#integrating-with-r)

## Summary
Embed a lineage-linked _Genealogical Data Communication_ 
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

```
/* 1 */
{
    "_id" : "@I1@",
    "name" : {
        "name" : "John /Smith/"
    },
    "sex" : "M",
    "fams" : "@F1@"
}

/* 2 */
{
    "_id" : "@I2@",
    "name" : {
        "name" : "Elizabeth /Stansfield/"
    },
    "sex" : "F",
    "fams" : "@F1@"
}

/* 3 */
{
    "_id" : "@I3@",
    "name" : {
        "name" : "James /Smith/"
    },
    "sex" : "M",
    "famc" : "@F1@"
}
```


## Execution

  * Dependencies are contained in `requirements.txt`:
      
    ```bash
    $pip install -r requirements.txt
    ```
  
  * Ingesting a data file, say `data/wiki.ged`, may be done as follows:
  
    ```bash
    $python main.py -i data/wiki.ged
    ```
  * Usage information may be gathered from the main runner via:
  
    ```bash
    $python main.py -h
    ```
    
## Testing

  * Unittests may be run via: 
  ```
    python -m unittest tests
  ```
  * Two sample files are provided in `data/`
  
  

## Conversion Conventions
 * Keys in the GEDCOM file (e.g. `FAMS`, `NAME`, ...) are retained as keys in MongoDB,
as far as possible. The instances where this is not the case, is:
    - when an individuals record is edited, a change record is added. In 
    this instance, the `DATE` and `TIME` are concatenated to form `chan_date`, an ISO datetime:  
  ```
    1 CHAN
    2 DATE 14 Jun 2020
    3 TIME 18:24:09
    
    >> chan_date: '2020-06-14 18:24:09.000Z'
  ```
 * ISO dates are used wherever possible to allow querying over time 
 ranges.
 * An individual record (e.g. `@I2@`) is currently used as the document 
 `_id` in MongoDB.
 
 * An embedded database structure is sought, but a secondary family
   database has been retained until the data is fully embedded. These two 
   databases are the
     - `person`, and
     - `family` databases.
      
   It is possible to join between the them in MongoDB.
 * Transformation are always repeatable and embedded in the data flow. There are currently the 
 following transformations applied to the incoming data:
    * `embed_p1`: 
        * [`parents`] insert the parents of each individual in a list (there can be more than two parents)
        * [`married_count`] count the number of times an individual has been married
        * [`spouses`] create a list of spouses that an individual had
        * [`children_count`] provide a counter of the number of children an individual had
   
   Each attribute 


## Example MongoDB Queries


* **Q**: Get all husbands and their marriage dates
```bash
db.coll.aggregate([
    {
        "$lookup": {
            "from": "family",
            "localField": "_id",
            "foreignField": "husb",
            "as": "husband"
        }
    },
    {
        "$match": {
            "husband": {"$ne": []}
        }
    },
    {
        "$unwind": "$husband"
    },
    {
        "$project": {"husband.marr": 1}
    }, 
])
```

* **Q**: Which town had the most marriages
```bash
db.coll.aggregate([
     {
        "$match": { "plac": {$ne: null}}
     },
     {  
        "$group": {
            "_id": "$plac",
            "count": {
                "$sum": 1
            }
        }
    },
    {
        "$sort": {"_id":-1}
    }
])

```

* **Q**: Average number of children per family

```bash
db.coll.aggregate([
    {
        "$match":{ "chil": {"$ne": null} }
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

* **Q**: Get all ancestors of of an individual `@I3@`
```bash
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

## Integrating with R

 * R packages requirements include:
   * `mongolite`
   
 * todo: an R notebook will be provided (e.g. [here](queries_r.nb.html))
 * Connecting to a MongoDB instance with database `gedcom`, collections `person` and `family`,
 and located on a host with IP `10.22.14.2` and port `27017`
 
 ```bash
 library(mongolite)
    person_coll = mongo(collection = "person", db = "gedcom", url = "mongodb://10.22.14.2:27017")
    family_coll = mongo(collection = "family", db = "gedcom", url = "mongodb://10.22.14.2:27017")
```
   

