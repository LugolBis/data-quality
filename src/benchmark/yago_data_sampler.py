import random
import sys
from pathlib import Path

IN_FILENAME = "yagoDateFacts.tsv"
OUT_FILENAME = "sampled_dates_dirty.tsv"
LIMIT: int = 50_000
COLUMNS: int = 5
TRESHOLD: float = 0.01
REQUIRED_ARGS: int = 1
USAGE = """
python3 yago_data_sampler.py <INPUT_FOLDER_PATH> <OUTPUT_FOLDER_PATH>

Args :
    <INPUT_FOLDER_PATH> (required) :
        The path of the folder who contains `yagoDateFacts.tsv`.
    <OUTPUT_FOLDER_PATH> (optional) :
        The path to the folder to save the transformed file `sampled_dates_dirty.tsv`.
"""


def main(input_folder: str, output_folder: str | None = None) -> None:
    input_file = Path(input_folder) / IN_FILENAME
    if not input_file.exists():
        print(f"Error : the following path doesn't exist `{input_file}`")
        return

    if output_folder is None:
        output_folder = input_folder
    output_file = Path(output_folder) / OUT_FILENAME

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
                # Strip type identifiers (e.g., values before ^^)
                if "^^" in col:
                    col = col.split("^^")[0]
                # Remove surrounding quotes
                col = col.strip('"')
                cleaned_columns.append(col)

            if len(cleaned_columns) >= COLUMNS:
                # Inject "dirty" data: 1% chance to change date to 3000-01-01
                if random.random() < TRESHOLD:
                    cleaned_columns[4] = "3000-01-01"

                new_line = "\t".join(cleaned_columns) + "\n"
                f_out.write(new_line)

    print("Cleaning completed")


if __name__ == "__main__":
    args: list[str] = sys.argv[1:]

    if ("--help" in args) or ("-help" in args) or len(args) < REQUIRED_ARGS:
        print(USAGE)
    else:
        output_folder = args[1] if len(args) > REQUIRED_ARGS else None
        main(args[0], output_folder)
