# -+- coding: utf-8 -*-

import os
import sys
import argparse
import pandas as pd
import pickle
import logging
sys.path.append(os.getcwd())
from postgre_db import operation

from settings import *
import functionsProcessCommon as functions

LOGFORMAT = logging.Formatter("%(asctime)-15s [%(name)s] %(message)s")

def process(conn, query, target, logger):
    query = query%target
    df = pd.io.sql.read_sql(query, conn)
    
    logger.info("raw shape: %s"%str(df.shape))
    logger.info("columns: (%s)"%", ".join(df.columns))

    df = df[df["title"].apply(lambda x: len(x)) != 0]
    df = df[df["content"].apply(lambda x: len(x)) != 0]

    logger.info("shape after removing record having empty title or content: %s"%str(df.shape))

    # general process
    df = df.assign(title_=lambda df: df["title"].apply(functions.processGeneralTitle),
                   content_=lambda df: df["content"].apply(functions.processGeneralContent))

    # process per target 
    df = df.assign(title__=lambda df: df["title_"].apply(functions.__dict__["process"+target.capitalize()+"Title"]),
                   content__=lambda df: df["content_"].apply(functions.__dict__["process"+target.capitalize()+"Content"]))

    df = df.reset_index(drop=True)

    return df
    
def main(args):
    
    print("=== target: %s ===" % args.target)
    
    query = "select * from %s;"

    with operation.conn_scope(postgres_url) as conn:            
        sh = logging.FileHandler(args.logpath)
        sh.setFormatter(LOGFORMAT)
        main_logger = logging.getLogger(os.path.basename(__file__) + ": main")
        main_logger.addHandler(sh) 
        main_logger.setLevel(logging.INFO)
        process_logger = logging.getLogger(os.path.basename(__file__) + ": process")
        process_logger.addHandler(sh)
        process_logger.setLevel(logging.INFO)
        df = process(conn, query, args.target, process_logger)
    
        main_logger.info("done! save title and target")
        with open(args.outpath, "wb") as f_save:
            pickle.dump(df, f_save)
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--outpath", type=str, help="")
    parser.add_argument("--logpath", type=str, help="")
    parser.add_argument("--target", type=str, help="")
    parser.add_argument("--overwrite", action="store_true", help="")
    args = parser.parse_args()
    
    main(args)
