import sys
import pickle

def savePickle(outpath, result):
    try:
        pickle.dump(result, open(outpath, "wb"))
    except OSError:
        bytes_out = pickle.dumps(result)
        n_bytes = sys.getsizeof(bytes_out)
        max_bytes = 2**31 - 1
        with open(outpath, "wb") as f_out:
            for idx in range(0, n_bytes, max_bytes):
                f_out.write(bytes_out[idx: idx+max_bytes])
