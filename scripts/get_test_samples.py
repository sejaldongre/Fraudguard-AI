import pandas as pd
import json


df = pd.read_csv("data/raw/creditcard.csv")


# Get first fraud transaction
fraud = (
    df[df["Class"] == 1]
    .drop(columns=["Class"])
    .iloc[0]
    .to_dict()
)


print("FRAUD TRANSACTION:")
print(
    json.dumps(
        fraud,
        indent=4
    )
)
