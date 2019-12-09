import pandas as pd
import numpy as np
from utils import read_json



def lower_bound(x):
    return x.quantile(0.005)


def upper_bound(x):
    return x.quantile(0.995)

def cap_df(df, metric, cap):
    cutoff = df[metric].quantile(cap)
    df[metric] = df[metric].clip(0, cutoff)
    return df

def bootstrap(
    df,
    iterations,
    spec,
    reporting_freq=100,
    strata=[]
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

    treatment = spec['treatment_branch_name']
    control = spec['control_branch_name']

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
    spec,
    reporting_freq=100,
    strata=[]
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

    treatment = spec['treatment_branch_name']
    control = spec['control_branch_name']
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


def process_experiment(df, n_boots, spec):
    capped_decile = pd.DataFrame()
    capped_tail = pd.DataFrame()
    capped = pd.DataFrame()

    n_clients = len(df)
    with open('./experiments/{}/data/n_clients.txt'.format(spec['dir']), 'w') as f:
        f.write(str(n_clients))

    print("{} Clients were enrolled in this experiment".format(n_clients))
    # Here we bootstrap individual metrics across
    # the distrbution
    print("Bootstrapping Metrics...")
    for metric in spec['metrics']:
        d = df[["experiment_branch", metric]]
        print(metric)
        d["any_" + metric] = [1 if i > 0 else 0 for i in d[metric]]

        df_capped = cap_df(d.copy(), metric, 0.999)

        result_capped = bootstrap(df_capped, n_boots, spec)
        capped = pd.concat([capped, result_capped])
        x = d[d[metric] > 0]
        x_capped = df_capped[df_capped[metric] > 0][["experiment_branch", metric]]

        # bootstrap these metrics again across deciles
        deciles = np.arange(0.1, 1.1, 0.1)
        rd = bootstrap_quantiles(x, n_boots, deciles, spec)
        rcd = bootstrap_quantiles(x_capped, n_boots, deciles, spec)
        capped_decile = pd.concat([capped_decile, rcd])

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
        rt = bootstrap_quantiles(x, n_boots, deciles, spec)
        rct = bootstrap_quantiles(x_capped, n_boots, deciles, spec)
        capped_tail = pd.concat([capped_tail, rct])


    csv_path = "experiments/{}/data/".format(spec['dir'])
    capped_decile.to_csv(csv_path + "capped_decile.csv", index=False)
    capped_tail.to_csv(csv_path + "capped_tail.csv", index=False)
    capped.to_csv(csv_path + "capped.csv", index=False)




