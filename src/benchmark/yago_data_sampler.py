import os
import random
import sys
from pathlib import Path
from dotenv import load_dotenv
from driver.neo4j_driver import Neo4jSession

load_dotenv()

IN_FILENAME = "yagoDateFacts.tsv"
OUT_FILENAME = "sampled_dates_dirty.tsv"
LIMIT: int = 50_000
COLUMNS: int = 5
TRESHOLD: float = 0.01

USAGE = """
python3 yago_data_sampler.py <INPUT_FOLDER_PATH>
Args :
    <INPUT_FOLDER_PATH> (required) :
        The path of the folder who contains `yagoDateFacts.tsv`.
"""

def main(input_folder: str, uri: str, user: str, password: str, database: str) -> None:
    input_file = Path(input_folder) / IN_FILENAME
    if not input_file.exists():
        print(f"Error : the following path doesn't exist `{input_file}`")
        return

    print("Connecting to Neo4j to retrieve the import folder path...")
    
    with Neo4jSession(uri, user, password, database) as session:
        home_folder = session.get_home_folder()
        if home_folder is None:
            print("Error: Could not retrieve Neo4j home folder. Check your connection or database config.")
            return
            
        import_folder = home_folder / "import"
        import_folder.mkdir(parents=True, exist_ok=True)
        output_file = import_folder / OUT_FILENAME

    print(f"Starting to intercept and clean {LIMIT} records...")

    with (
        open(input_file, encoding="utf-8") as f_in,
        open(output_file, "w", encoding="utf-8") as f_out,
    ):
        for i, line in enumerate(f_in):
            if i >= LIMIT:
                break

            columns = line.strip("\n").split("\t")
            cleaned_columns = []
            for col in columns:
                if "^^" in col:
                    col = col.split("^^")[0]
                col = col.strip('"')
                cleaned_columns.append(col)

            if len(cleaned_columns) >= COLUMNS:
                if random.random() < TRESHOLD:
                    cleaned_columns[4] = "3000-01-01"

                new_line = "\t".join(cleaned_columns) + "\n"
                f_out.write(new_line)

    print("Cleaning completed.")
    print(f"File successfully saved to: {output_file.resolve()}")

    print("Creating constraints in Neo4j...")
    constraint_query = "CREATE CONSTRAINT IF NOT EXISTS FOR (e:Entity) REQUIRE e.uri IS UNIQUE;"
    session.run_query(constraint_query)

    print("Loading data into Neo4j via Cypher")
    load_query = r"""
    LOAD CSV FROM 'file:///sampled_dates_dirty.tsv' AS row FIELDTERMINATOR '\t'
    WITH row[1] AS subject, row[2] AS predicate, row[3] AS object, row[4] AS date_value
    WHERE subject IS NOT NULL AND predicate IS NOT NULL

    MERGE (s:Entity {uri: subject})
    MERGE (o:Entity {uri: object})

    WITH s, o, predicate, date_value
    CALL apoc.create.relationship(s, predicate, {date_value: date_value}, o) YIELD rel
    RETURN count(*) AS count;
    """
    
    result = session.run_query(load_query)
    record = result.single()
    
    if record:
        print(f"Success! Loaded {record['count']} relationships into Neo4j.")
    else:
        print("Data load query executed successfully.")


if __name__ == "__main__":
    args: list[str] = sys.argv[1:]

    if ("--help" in args) or ("-help" in args) or len(args) < 1:
        print(USAGE)
    else:
        input_folder = args[0]
        
        uri = os.getenv("URI")
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PW")
        database = os.getenv("DB_NAME")

        if not all([uri, user, password, database]):
            print("Error: Missing Neo4j connection details. Please provide them in the .env file or via CLI.")
        else:
            main(input_folder, uri, user, password, database)