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
import functions

LOGFORMAT = logging.Formatter("%(asctime)-15s [%(name)s] %(message)s")

def process(conn, query, target, logger):
    query = query%target
    df = pd.io.sql.read_sql(query, conn)
    #import IPython;IPython.embed() ##############################
    
    logger.info("raw shape: %s"%str(df.shape))
    logger.info("columns: %s"%str(df.columns))

    df = df[df['title'].apply(lambda x: len(x)) != 0]
    df = df[df['content'].apply(lambda x: len(x)) != 0]

    logger.info("shape after removing record having empty title or content: %s"%str(df.shape))

    df = df[["title", "content"]]

    # general process
    df = df.assign(title_=lambda df: df["title"].apply(functions.processGeneralTitle),
                   content_=lambda df: df["content"].apply(functions.processGeneralContent)
    ).drop(["title", "content"], axis=1
    ).rename(columns={"title_": "title", "content_": "content"})

    # process per target # if want to drop, return blank from apply function
    df = df.assign(title_=lambda df: df["title"].apply(functions.__dict__["process"+target.capitalize()+"Title"]),
                   content_=lambda df: df["content"].apply(functions.__dict__["process"+target.capitalize()+"Content"])
    ).drop(["title", "content"], axis=1
    ).rename(columns={"title_": "title", "content_": "content"})

    return df
    
def main(args):
    
    query = "select * from %s order by random() limit 100000;" ##################################
    global target_list
    target_list = target_list[:1] ##################################
    query = "select * from %s;"

    with operation.conn_scope(postgres_url) as conn:
        for target in target_list:
            if args.overwrite and os.path.exists(args.outpath, target+".pkl"):
                continue

            sh = logging.FileHandler(os.path.join(args.logpath, target+".log"), "a")
            sh.setFormatter(LOGFORMAT)
            main_logger = logging.getLogger("main")
            main_logger.addHandler(sh)
            process_logger = logging.getLogger("process")
            process_logger.addHandler(sh)
            df = process(conn, query, target, process_logger)
            
            main_logger.info("save title and target")
            with open(os.path.join(args.outpath, target+".pkl"), "wb") as f_save:
                pickle.dump(df, f_save)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--outpath", type=str, help="")
    parser.add_argument("--logpath", type=str, help="")
    parser.add_argument("--overwrite", action="store_true", help="")
    args = parser.parse_args()
    
    main(args)
