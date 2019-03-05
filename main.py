import logging
import app_logger
import dbinterface as dbi
import ingest
#from bson.objectid import ObjectId

import argparse

log = app_logger.init(log_level=logging.DEBUG)

DATA_FOLDER='/home/jacques/industria/nand/nand-gedcom-to-mongo/data'
MONGO_PORT = 27017


if __name__ == '__main__':
    parser = argparse.ArgumentParser('main')
    parser.add_argument('-i', '--ingest', required=False, help="provide a fully qualified gedcom file")
    parser.add_argument('-d', '--db', required=True, help="provide an output database name")
    parser.add_argument('--ip', default="10.22.14.2", help="provide an ip address for db")
    parser.add_argument('-p', '--port', default=27017, help="provide integer port for db")
    parser.add_argument('-c', '--coll', required=True, help="collection name")

    args = parser.parse_args()

    conn = None
    # open connection
    try:
        log.info('loading source data db')
        src_conn = dbi.Db(ip_addr=args.ip, port=args.port)
    except Exception as e:
        log.exception('failed to open connection to {}.{}'.format(args.db, args.coll))
        raise

    # check if the collection exists
    if args.coll not in src_conn.mc[args.db].collection_names():
        log.warning('collection {} does not exist in {}'.format(args.coll, args.db))

    if args.ingest:
        log.info('ingesting data: processing {} and storing to {}.{}'.format(args.ingest, args.db, args.coll))
        ingest.file_parser(ingest.FILENAME)
    else:
        raise NotImplementedError()



