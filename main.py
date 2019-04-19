import logging
import app_logger
import dbinterface as dbi
import ingest
import settings
import embedding_person as tr

import argparse

log = app_logger.init(log_level=logging.INFO)

DATA_FOLDER='/home/jacques/industria/nand/nand-gedcom-to-mongo/data'
MONGO_PORT = 27017


if __name__ == '__main__':
    parser = argparse.ArgumentParser('main')
    parser.add_argument('-i', '--ingest', required=False, help="provide a fully qualified gedcom file")
    # parser.add_argument('-d', '--db', required=True, help="provide an output database name")
    parser.add_argument('--host', default="10.22.14.2", help="provide an ip address for db")
    parser.add_argument('-p', '--port', default=27017, help="provide integer port for db")
    parser.add_argument('-t', '--transformer', help='apply transformation')
    # parser.add_argument('-c', '--coll', required=True, help="collection name")

    args = parser.parse_args()

    conn = None
    # open connection
    try:
        log.info('loading source data db')
        src_connector = dbi.MongoConnector().connect(args.host, args.port)
        # coll = src_conn.collection(args.db, args.coll)
        log.info('DB connection initialised : {}'.format(src_connector))
    except Exception as e:
        log.exception('failed to open connection to {}'.format(args.db))
        raise

    # # check if the collection exists
    # if args.coll not in src_conn.mc[args.db].collection_names():
    #     log.warning('collection {} does not exist in {}'.format(args.coll, args.db))

    if args.ingest:
        log.info('ingesting data: processing {} and storing to {}'.format(args.ingest, settings.sink_db))
        ingestor = ingest.FileIngestor(args.ingest)
        ingestor.ingest()
        log.info('REPORT: {}'.format(ingestor.meta_data))
    elif args.transformer:
        log.info('applying transformation pipelines')
        family_coll = dbi.MongoDb(dbi.MongoConnector(), db=settings.sink_db, coll=settings.sink_tbl['family'])
        person_coll = dbi.MongoDb(dbi.MongoConnector(), db=settings.sink_db, coll=settings.sink_tbl['person'])
        tr.processor(family_coll, person_coll)



