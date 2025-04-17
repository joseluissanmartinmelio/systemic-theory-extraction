import pandas as pd
from pathlib import Path

# relative directory

relative_dir = Path(__file__).resolve().parent.parent
print(relative_dir)

# data

papers = pd.read_csv(relative_dir / 'data' / 'raw' / 'journal_party_politics_scopus.csv')
print(columns := papers.columns)

# five most cited papers per year
top_cited_per_year = papers.groupby('Year').apply(
    lambda group: group.nlargest(3, 'Cited by')
).reset_index(drop=True)

print(top_cited_per_year)

# export to csv
top_cited_per_year.to_csv(relative_dir / 'data' / 'processed' / 'journal_party_politics_scopus_most_cited.csv', index=False)