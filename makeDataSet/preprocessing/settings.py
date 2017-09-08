# -*- coding: utf-8 -*-

import os
import pandas as pd
pd.set_option("display.max_colwidth", 100)
pd.set_option("display.max_rows", 10000)

postgres_host = "localhost"
postgres_db = "news"
postgres_url = "postgres://%s/%s"%(postgres_host, postgres_db)

START = "<S>"
EOS = "<EOS>"
