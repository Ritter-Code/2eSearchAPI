import math
import numpy as np
import pandas as pd

def df_to_records(df):
    result = []

    for row in df.to_dict(orient="records"):
        clean_row = {}
        for k, v in row.items():
            if isinstance(v, float) and math.isnan(v):
                clean_row[k] = None
            elif v is pd.NA: 
                clean_row[k] = None
            elif isinstance(v, np.integer):
                clean_row[k] = int(v)
            elif isinstance(v, np.bool_):
                clean_row[k] = bool(v)
            else:
                clean_row[k] = v
        
        result.append(clean_row)
    
    return result