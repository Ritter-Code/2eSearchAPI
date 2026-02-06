import duckdb
from pathlib import Path

ledger_dir = Path("2eDataManipulation/Content/metadata/ledger")

## Used to import the stored ledger parquets, sort them by most recent entry, and decide if the file is committed, or still needs processed
def retrieve_processed_list():
    ledger_parq = list(ledger_dir.glob("*.parquet"))
    if not ledger_parq:
        return {}

    con = duckdb.connect(database=":memory:")

    latest_change = con.execute(f"""
                                    SELECT entity_id, entity_type, entity_hash, state
                                    FROM read_parquet("{ledger_dir.as_posix()}/*.parquet")
                                    QUALIFY ROW_NUMBER() OVER (
                                        PARTITION BY entity_id, entity_type
                                        ORDER BY event_time DESC
                                    ) = 1
                                """).fetchall()
    
    commited = {
        (entity_id, entity_type) : entity_hash
        for (entity_id, entity_type, entity_hash, state) in latest_change
        if state == "COMMITTED"
    }

    return commited