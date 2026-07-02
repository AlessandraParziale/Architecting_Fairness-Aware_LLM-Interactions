import pandas as pd

RANDOM_STATE = 42
K = 10

df = pd.read_csv("data/SCOPE_dataset.csv")

balanced_df = (
    df.groupby(["bias_type", "intent"], group_keys=False)
      .sample(n=K, random_state=RANDOM_STATE)
)

balanced_df = balanced_df.sample(
    frac=1,
    random_state=RANDOM_STATE
)

balanced_df.to_csv(
    "data/SCOPE_dataset_360.csv",
    index=False
)

print("Final dataset size:", len(balanced_df))

print("\nBias type distribution:")
print(balanced_df["bias_type"].value_counts())

print("\nIntent distribution:")
print(balanced_df["intent"].value_counts())

print("\nBias type x Intent distribution:")
print(
    balanced_df.groupby(
        ["bias_type", "intent"]
    ).size()
)