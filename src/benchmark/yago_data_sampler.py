import random

input_file = "yagoDateFacts.tsv"
output_file = "sampled_dates_dirty.tsv"
limit = 50000

print(f"Starting to intercept and clean {limit} records...")

with (
    open(input_file, encoding="utf-8") as f_in,
    open(output_file, "w", encoding="utf-8") as f_out,
):
    for i, line in enumerate(f_in):
        if i >= limit:
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

        if len(cleaned_columns) >= 5:
            # Inject "dirty" data: 1% chance to change date to 3000-01-01
            if random.random() < 0.01:
                cleaned_columns[4] = "3000-01-01"

            new_line = "\t".join(cleaned_columns) + "\n"
            f_out.write(new_line)

print("Cleaning completed")
