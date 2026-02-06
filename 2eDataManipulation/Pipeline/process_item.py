import orjson
import hashlib
from Ledger.ledger import add_ledger_event

## Core data extraction and schema enforcement layer process
## Records file in progress and begins the extraction
## Selects data extraction method and schema based on the "type" field
## Extracts the data for all necessary content fields and ledger metadata 
## Records which files have been processed and reports which are staged for writing and which have failed
## Returns a check to confirm if a file was processed successfully
def process_item_file(i_file_path, i_extractor_registry, i_master_table, i_ledger, i_processed_entities, i_batch_id , i_committed_ledger):
    # Open and check the file for duplicate processing and file relevancy. If the file does not have an '_id' or 'type', is not the expected 
    # data type (dict), or matches an already processed id/type/hash combination, skip it 
    with open(i_file_path, "rb") as file:
        raw_bytes = file.read()
        read_file = orjson.loads(raw_bytes)
        
        # Data type check
        if not isinstance(read_file, dict):
            return False

        # File relevancy check
        if '_id' not in read_file or 'type' not in read_file:
            return False  

        # Duplicate processing check   
        entity_hash = hashlib.sha256(raw_bytes).hexdigest()
        id_check = read_file['_id']
        type_check = read_file['type']
        last_hash = i_committed_ledger.get((id_check, type_check))
        if last_hash == entity_hash:
            return False
        
        # Record the file is being processed
        add_ledger_event(
            i_ledger = i_ledger, 
            i_batch_id = i_batch_id, 
            i_entity_id = id_check, 
            i_entity_type = type_check, 
            i_entity_hash = entity_hash, 
            i_state = "IN_PROGRESS"
        )

        # Select type-based extractor according to content type and extract the information
        Extractor = i_extractor_registry[type_check]
        extracted_data = Extractor(read_file).extract_all()

        # Process the extracted information into schema stable tables 
        try:
                
            for sub_table, table_row in extracted_data.items():
                # If no content was extracted for this field, move on
                if table_row is None:
                    continue
                
                # Add the content to the appropriate table/subtable in the master table by content aware processing
                # If there is no table in master table, report a type error and continue
                target_table = i_master_table[type_check][sub_table]

                if isinstance(table_row, dict):
                    target_table.append(table_row)

                elif isinstance(table_row, list):
                    target_table.extend(table_row)

                else:
                    raise TypeError(f"Unexpected type: {type(table_row)} for table {target_table}")

            # Record which files have been processed to reference during writing    
            i_processed_entities.append({
                "entity_id" : id_check,
                "entity_type" : type_check,
                "entity_hash" : entity_hash
            })

            # Add a record to the ledger stating the file is ready for writing
            add_ledger_event(
                i_ledger=i_ledger,
                i_batch_id=i_batch_id,
                i_entity_id=id_check,
                i_entity_type=type_check,
                i_entity_hash=entity_hash,
                i_state="STAGED"
            )

            # Return true if a file is successfully processed
            return True

        # If a file fails to process, record it in the ledger and return false
        except Exception:
            add_ledger_event(
                i_ledger = i_ledger, 
                i_batch_id = i_batch_id, 
                i_entity_id = id_check, 
                i_entity_type = type_check, 
                i_entity_hash = entity_hash, 
                i_state = "FAILED"
            )

            return False
                