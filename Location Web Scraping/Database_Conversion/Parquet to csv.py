import pandas as pd

#converting db to csv format
df = pd.read_parquet("list%20of%20company%20websites.snappy.parquet")
df.to_csv("List_of_companies_urls.csv")