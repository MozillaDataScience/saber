import pandas as pd  


def bootstrap(df, iterations, reporting_freq=10, strata=[],
              treatment='variant', control='control'):
    def munge(s):
        agg = s.groupby(["experiment_branch"] + strata).mean()
        agg = (
          pd.melt(agg.reset_index(), id_vars=["experiment_branch"] + strata)
          .pivot_table(
                    index=strata + ['variable'],
                    columns='experiment_branch',
                    values='value').reset_index()
          )
        agg['change'] = (agg[treatment] - agg[control]) / agg[control]
        return agg

    n = len(df)
    results = munge(df)
    bootstrapped_results = pd.DataFrame()
    for i in range(iterations):
        if i % 10 == 0:
            print(i),
        s = df.sample(n, replace=True)
        sagg = munge(s)
        sagg['iteration'] = i
        bootstrapped_results = pd.concat([sagg, bootstrapped_results])
    return results, bootstrapped_results
  

df = pd.read_csv("./data/exp_client.csv")

cutoffs = (
    df
    .groupby("experiment_branch")
    .quantile([.995])
    .reset_index()
    [["experiment_branch", "sap", "organic"]]
)

cutoffs.columns = ["experiment_branch", "sap_cut", 'organic_cut']
joined = pd.merge(df, cutoffs, on="experiment_branch")

df_trimmed = (
    joined[(joined.sap < joined.sap_cut) & 
           (joined.organic < joined.organic_cut)]
    .drop(["organic_cut", "sap_cut"], axis=1)
)


print("Bootstrapping...")
result, bs = bootstrap(df_trimmed, 500)


result.to_csv("./data/result.csv", index=False)
bs.to_csv("./data/boot.csv", index=False)
