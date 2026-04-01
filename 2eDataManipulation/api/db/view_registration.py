from pathlib import Path
from .connection import conn

def register_views():
    type_list = ["spell", "ancestry"]

    for type in type_list:
        file_dir = Path(__file__).resolve().parent.parent.parent / "Content" / type

        for sub_table_dir in file_dir.iterdir():
            if sub_table_dir.is_dir():
                view_name = f"{type}_{sub_table_dir.name}"
                glob_path = (sub_table_dir / "*.parquet").as_posix()
                conn.execute(f"CREATE VIEW IF NOT EXISTS {view_name} AS SELECT * FROM read_parquet('{glob_path}')")

    print(conn.execute("SHOW TABLES").fetchdf())