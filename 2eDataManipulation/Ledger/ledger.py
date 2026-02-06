import uuid
from datetime import datetime, timezone

## Create a ledger event with needed information for status check and id verification and add the the event registry
def add_ledger_event(i_ledger, i_batch_id, i_entity_id, i_entity_type, i_entity_hash, i_state):
    event_time = datetime.now(timezone.utc)
    
    event_entry = {
        "ledger_id" : str(uuid.uuid4()),
        "entity_id" : i_entity_id,
        "entity_type" : i_entity_type,
        "entity_hash" : i_entity_hash,
        "batch_id" : i_batch_id,
        "state" : i_state,
        "event_time" : event_time
    }

    i_ledger.append(event_entry)
