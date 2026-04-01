from pathlib import Path
from .connection import conn

def register_views():
    type_list = ["spell", "ancestry"]

    for type in type_list:
        file_dir = Path(__file__).resolve().parent.parent.parent / "Content" / type

        for parquet_file in file_dir.glob("**/*.parquet"):
            sub_table_name = parquet_file.parent.name
            view_name = f"{type}_{sub_table_name}"
            conn.execute(f"CREATE VIEW IF NOT EXISTS {view_name} AS SELECT * FROM read_parquet('{parquet_file.as_posix()}')")

    print(conn.execute("SHOW TABLES").fetchdf())