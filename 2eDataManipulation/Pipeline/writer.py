import pyarrow as pa
import pandas as pd
import pyarrow.parquet as pq
from pathlib import Path

## Write the current selected batch of tables to a parquet based on the content type, schema, and batch id
def batch_to_file(relational_dir, table_rows, relational_name, batch_id):
    table = pa.Table.from_pandas(pd.DataFrame(table_rows))
    relational_dir.mkdir(parents = True, exist_ok = True)
        
    with pq.ParquetWriter(f"{relational_dir}/{batch_id}--{relational_name}.parquet", table.schema, use_dictionary = True) as writer:
        writer.write_table(table)

## Write the current ledger file into a parquet with the batch id
def write_ledger_file(i_ledger, i_metadata_dir, i_batch_id):
    table = pa.Table.from_pandas(pd.DataFrame(i_ledger))
    event_dir = i_metadata_dir/"ledger"
    event_dir.mkdir(parents = True, exist_ok = True)

    with pq.ParquetWriter(f"{event_dir}/Batch--{i_batch_id}.parquet", table.schema, use_dictionary = True) as writer:
         writer.write_table(table)

## Manage the write process for the master table, feeding the batch writer type/schema specific files to process
## Report when each type is complete
def write_master_table(i_master_table, i_master_parq_dir, i_batch_id):
    # Process each content type recorded in the master table
    for types in i_master_table:
            # Record the path for the relational tables to pass to batch writer
            sub_table_dir = i_master_parq_dir/f"{types}"
            sub_table_dir.mkdir(parents = True, exist_ok = True)
            
            # Process each relational table into a parquet using the batch writer
            for sub_tables in i_master_table[types]:
                rows = i_master_table[types][sub_tables]
                if not rows:
                    continue
                relational_table_dir = sub_table_dir/f"{sub_tables}"        
                batch_to_file(relational_table_dir, i_master_table[types][sub_tables], sub_tables, i_batch_id)

            # Report when a type is completed.
            print(f"Entry type <{types}> completed")