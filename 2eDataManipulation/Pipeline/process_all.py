import glob
import os
import pandas as pd
from pathlib import Path
from Schema.schema_registry import TYPE_REGISTRY
from Extractor.extractor_registry import EXTRACTOR_REGISTRY
from Pipeline.process_item import process_item_file
from Pipeline.writer import write_master_table, write_ledger_file
from datetime import datetime, timezone
from Ledger.ledger import add_ledger_event
from Ledger.pull_ledger import retrieve_processed_list

## Core method for the entire data ingestion and processing program. Houses all logic calls
def process_all(input_dir):

    # Retrieve a referenceable list of the extractors, keyed to each file's "type" field
    extractor_reg = {
        extractor_name: extractor
        for extractor_name, extractor in EXTRACTOR_REGISTRY.items()
    }

    # Creates/loads a series of lists to manage the itteration filter to prevent duplicate processed files
    ledger_events = []
    processed_entities = []
    committed_ledger = retrieve_processed_list()

    #Generate the current batch ID to record in the ledger
    batch_id = datetime.now(timezone.utc)

    # Create a mutable table to handle each of the content types/schema prepared in the schema registry (TYPE_REGISTRY)
    master_table = {
        type_name: {
            table_name: []
            for table_name in relations
        }
        for type_name, relations in TYPE_REGISTRY.items()
    }

    # Making a Path and creating any directories if they have not been created yet for storing all processed content
    master_parq_dir = Path("2eDataManipulation/Content")
    master_parq_dir.mkdir(parents = True, exist_ok = True)
   
    # Stores the ledger information
    metadata_dir = master_parq_dir/"metadata"
    metadata_dir.mkdir(parents = True, exist_ok = True)
    
    # Create Variable to keep track of how many entries are updated.
    updated = 0

    # Pull all of the file paths to use for the traversing and processing
    # Pull the number of files to use as a counting reference
    json_files = glob.glob(os.path.join(input_dir, "**/*.json"), recursive = True)
    file_count = len(json_files)

    # Process each file that has been called
    # Attempt to process the entire file using process_item_file, report errors, count/report the count, and continue
    for i, file_path in enumerate(json_files, 1):
        try:
            new_record = process_item_file(
                i_file_path = file_path, 
                i_extractor_registry = extractor_reg,
                i_master_table = master_table,
                i_ledger = ledger_events, 
                i_processed_entities = processed_entities, 
                i_batch_id = batch_id,
                i_committed_ledger = committed_ledger
            )

            # If a file is successfully processed and process_item_file returns true, record a file has been updated
            if new_record:
                updated += 1

        # If the file fails to process, report it has failed and continue
        except Exception as e:
            print(f"{file_path} failed with :: {e}")

        # Every 500 files process, report the current count and total files in process
        if (i%500) == 0:     
            print(f"Processed Files: {i} of {file_count}")

    # If any files have been update, begin writing the files to parquets
    # For each file, either record it has successfully been committed to content or record that it has failed to be written
    # Write the updated ledger file to a parquet
    if updated > 0:
        print(f"Beginning saving {updated} new files")

        try:
            write_master_table(
                i_master_table = master_table, 
                i_master_parq_dir = master_parq_dir,
                i_batch_id = batch_id 
            )
        
        except Exception:
            for entity in processed_entities:
                add_ledger_event(
                    i_ledger = ledger_events, 
                    i_batch_id = batch_id, 
                    i_entity_id = entity["entity_id"], 
                    i_entity_type = entity["entity_type"], 
                    i_entity_hash = entity["entity_hash"], 
                    i_state = "FAILED"
                )
            raise
        
        else: 
            for entity in processed_entities:
                add_ledger_event(
                    i_ledger = ledger_events, 
                    i_batch_id = batch_id, 
                    i_entity_id = entity["entity_id"], 
                    i_entity_type = entity["entity_type"], 
                    i_entity_hash = entity["entity_hash"], 
                    i_state = "COMMITTED"
                )

        write_ledger_file(
            i_ledger = ledger_events, 
            i_metadata_dir = metadata_dir, 
            i_batch_id = batch_id
        )    
                
    else: 
        print("No new entries to process")

        