import pandas as pd
import numpy as np


def lower_bound(x):
    return x.quantile(0.005)


def upper_bound(x):
    return x.quantile(0.995)


def bootstrap(
    df,
    iterations,
    reporting_freq=100,
    strata=[],
    treatment="3-col-7-row-octr",
    control="basic",
):
    def munge(s):
        agg = s.groupby(["experiment_branch"] + strata).mean()
        agg = (
            pd.melt(agg.reset_index(), id_vars=["experiment_branch"] + strata)
            .pivot_table(
                index=strata + ["variable"], columns="experiment_branch", values="value"
            )
            .reset_index()
        )
        agg["change"] = (agg[treatment] - agg[control]) / agg[control]
        return agg

    n = len(df)
    results = munge(df)
    bootstrapped_results = pd.DataFrame()
    for i in range(iterations):
        s = df.sample(n, replace=True)
        sagg = munge(s)
        sagg["iteration"] = i
        bootstrapped_results = pd.concat([sagg, bootstrapped_results])

    idx = ["variable"] + strata
    br = (
        bootstrapped_results.groupby(idx)
        .agg({"change": [lower_bound, upper_bound]})
        .reset_index()
    )

    br.columns = idx + ["lower", "upper"]
    return pd.merge(results, br, on=["variable"] + strata)


def bootstrap_quantiles(
    df,
    iterations,
    q,
    reporting_freq=100,
    strata=[],
    treatment="3-col-7-row-octr",
    control="basic",
):
    def munge(s):
        agg = s.groupby(["experiment_branch"] + strata).quantile(q)
        agg = (
            pd.melt(
                agg.reset_index(), id_vars=["experiment_branch"] + strata + ["level_1"]
            )
            .pivot_table(
                index=strata + ["level_1", "variable"],
                columns="experiment_branch",
                values="value",
            )
            .reset_index()
        )
        agg["change"] = (agg[treatment] - agg[control]) / agg[control]
        return agg

    n = len(df)
    results = munge(df)
    bootstrapped_results = pd.DataFrame()
    for i in range(iterations):
        s = df.sample(n, replace=True)
        sagg = munge(s)
        sagg["iteration"] = i
        bootstrapped_results = pd.concat([sagg, bootstrapped_results])

    idx = ["variable"] + strata + ["level_1"]
    br = (
        bootstrapped_results.groupby(idx)
        .agg({"change": [lower_bound, upper_bound]})
        .reset_index()
    )

    br.columns = idx + ["lower", "upper"]
    return pd.merge(results, br, on=["variable", "level_1"] + strata)


def trim_df(df, cut, metric):
    cutoffs = (
        df.groupby("experiment_branch")
        .quantile([cut])
        .reset_index()[["experiment_branch", metric]]
    )

    cutoffs.columns = ["experiment_branch", metric + "_cut"]
    joined = pd.merge(df, cutoffs, on="experiment_branch")

    df_trimmed = joined[joined[metric] < joined[metric + "_cut"]].drop(
        [metric + "_cut"], axis=1
    )

    return df_trimmed


def cap_df(df, metric, cap):
    cutoff = df[metric].quantile(cap)
    df[metric] = df[metric].clip(0, cutoff)
    return df


df = pd.read_csv("./data/exp_client.csv")
print("Bootstrapping Metrics...")
res_capped_decile1 = pd.DataFrame()
res_capped_tail1 = pd.DataFrame()
res_capped1 = pd.DataFrame()


# Here we bootstrap individual metrics across
# the distrbution, using only the three defined below
# for time's sake
NBOOTS = 1000
metrics = ["sap", "tagged_sap", "organic", "ad_clicks"]
for metric in metrics:
    d = df[["experiment_branch", metric]]
    print(metric)
    d["any_" + metric] = [1 if i > 0 else 0 for i in d[metric]]

    df_capped1 = cap_df(d.copy(), metric, 0.999)

    print("means")
    result_capped_1 = bootstrap(df_capped1, NBOOTS)

    res_capped1 = pd.concat([res_capped1, result_capped_1])

    x = d[d[metric] > 0]
    x_capped1 = df_capped1[df_capped1[metric] > 0][["experiment_branch", metric]]

    print("deciles")
    # bootstrap these metrics again across deciles
    deciles = np.arange(0.1, 1.1, 0.1)
    rd = bootstrap_quantiles(x, NBOOTS, q=deciles)
    rcd1 = bootstrap_quantiles(x_capped1, NBOOTS, q=deciles)
    res_capped_decile1 = pd.concat([res_capped_decile1, rcd1])

    print("quantiles")
    # Do the same thing, but only for the tail above 90th percentile, adding the
    # 99.9 and 99.99th as well
    deciles = [
        0.9,
        0.91,
        0.92,
        0.93,
        0.94,
        0.95,
        0.96,
        0.97,
        0.98,
        0.99,
        0.999,
        0.9999,
        1,
    ]
    rt = bootstrap_quantiles(x, NBOOTS, q=deciles)
    rct1 = bootstrap_quantiles(x_capped1, NBOOTS, q=deciles)
    res_capped_tail1 = pd.concat([res_capped_tail1, rct1])


csv_path = "./data/"
res_capped_decile1.to_csv(csv_path + "res_capped_decile.csv", index=False)
res_capped_tail1.to_csv(csv_path + "res_capped_tail.csv", index=False)
res_capped1.to_csv(csv_path + "res_capped.csv", index=False)
