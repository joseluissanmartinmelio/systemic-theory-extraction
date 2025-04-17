import pandas as pd
from pathlib import Path

# relative path

relative_dir = Path(__file__).resolve().parent.parent

data_dir = relative_dir / 'docs'

# function
def load_csvs_with_paper_name(directory, paper_name):
    all_csv_files = directory.glob("*.csv")
    dataframes = []
    for csv_file in all_csv_files:
        if paper_name in csv_file.stem:
            df = pd.read_csv(csv_file)
            # Process the "autores" column
            if "autores" in df.columns:
                df["autores"] = df["autores"].apply(
                    lambda x: f"¨{paper_name}" if isinstance(x, str) and "narrador" in x.lower() else x
                )
                # Remove "*" from the "autores" column
                df["autores"] = df["autores"].str.replace("*", "", regex=False)
            dataframes.append(df)
    if dataframes:
        return pd.concat(dataframes, ignore_index=True)
    else:
        return pd.DataFrame()

# variables

paper_name = "Lucardie P. (2000)"

# data

loaded_dataframes = load_csvs_with_paper_name(data_dir, paper_name)
print(loaded_dataframes)

# export to csv
loaded_dataframes.to_csv(data_dir / f"{paper_name}_complete.csv", index=False)
