import json
import os
import os.path as op
from collections import OrderedDict
from datetime import date

import numpy as np
import pandas as pd
import mozanalysis.frequentist_stats.bootstrap as mafsb
import mozanalysis.metrics.desktop as desktop
from mozanalysis.bq import BigQueryContext
from mozanalysis.experiment import Experiment, TimeLimits
from mozanalysis.metrics import Metric

from utils.validate_schema import validate_schema


OSERROR_MSG = "File exists and overwrite was set to False."


def aggregate_data(exp_path):
    report = validate_schema(op.join(op.abspath(exp_path), "report.json"))
    exp = Experiment(
        experiment_slug=report["experiment_slug"],
        start_date=report["start_date"],
        num_dates_enrollment=report["num_dates_enrollment"]
    )

    bq_context = BigQueryContext(dataset_id=report["dataset_id"])
    metric_list = _make_metric_list(report)

    single_window_res = exp.get_single_window_data(
        bq_context=bq_context,
        metric_list=metric_list,
        last_date_full_data=report["last_date_full_data"],
        analysis_start_days=report["analysis_start_days"],
        analysis_length_days=report["analysis_length_days"]
    )
    # TODO: Figure out another way to deal with missing values per client
    single_window_res.dropna(inplace=True)

    return single_window_res


def bootstrap_data(exp_path, single_window_res, num_samples,
                   ref_branch_label='control',
                   threshold_quantile=0.999,
                   ci_quantiles=(0.005, 0.025, 0.975, 0.995)):

    report = validate_schema(op.join(op.abspath(exp_path), "report.json"))
    metric_list = _make_metric_list(report)
    metric_names = [metric.name for metric in metric_list]

    res_metrics = list()
    for metric in metric_names:
        if any(single_window_res['branch'] == ref_branch_label):
            res_metric = _res_to_df_nest(
                metric,
                mafsb.compare_branches(
                    single_window_res,
                    col_label=metric,
                    ref_branch_label=ref_branch_label,
                    stat_fn=_decilize,
                    threshold_quantile=threshold_quantile,
                    individual_summary_quantiles=list(ci_quantiles),
                    comparative_summary_quantiles=list(ci_quantiles),
                    num_samples=num_samples
                )
            )
        elif len(np.unique(single_window_res['branch'])) == 1:
            res_metric = mafsb.bootstrap_one_branch(single_window_res[metric],
                                                    stat_fn=_decilize,
                                                    num_samples=num_samples,
                                                    summary_quantiles=list(ci_quantiles)
                                                    )
        else:
            raise ValueError("There are multiple branches present in this ",
                             "study, but `ref_branch_label` is either "
                             "missing or incorrect.")
        res_metrics.append(res_metric)
    res_metrics = pd.concat(res_metrics)

    return res_metrics


def dry_run_query(exp_path):
    report = validate_schema(op.join(exp_path, "report.json"))
    metric_list = _make_metric_list(report)

    exp = Experiment(
        experiment_slug=report["experiment_slug"],
        start_date=report["start_date"],
        num_dates_enrollment=report["num_dates_enrollment"]
    )
    # create an archive of the sql generating analysis
    time_limits = TimeLimits.for_single_analysis_window(
        first_enrollment_date=report['start_date'],
        last_date_full_data=report['last_date_full_data'],
        analysis_start_days=report['analysis_start_days'],
        analysis_length_dates=report['analysis_length_days'],
        num_dates_enrollment=report['num_dates_enrollment'])
    query = exp.build_query(metric_list=metric_list, time_limits=time_limits,
                            enrollments_query_type='normandy')

    return query


def run_etl(exp_path, overwrite=False):
    # Initialization
    exp_path = op.abspath(exp_path)
    report = validate_schema(op.join(exp_path, "report.json"))
    _build_directory(exp_path)

    single_window_res = aggregate_data(exp_path)

    res_metrics = bootstrap_data(exp_path, single_window_res,
                                 num_samples=report["n_resamples"])

    # Make a copy of the query that was executed
    query = dry_run_query(exp_path)

    # Write things to disk
    FILENAME_SQL = op.join(exp_path, 'sql',
                           f'{report["last_date_full_data"]}_'
                           f'{report["experiment_slug"]}.sql')
    FILENAME_ANALYSIS_DATA = op.join(exp_path, 'data',
                                     f'{report["last_date_full_data"]}_'
                                     f'{report["experiment_slug"]}.csv')
    if not op.exists(FILENAME_ANALYSIS_DATA) or overwrite:
        res_metrics.to_csv(FILENAME_ANALYSIS_DATA, index=False)
        open(FILENAME_SQL, 'w').write(query)
    else:
        raise OSError(OSERROR_MSG)

    return res_metrics


def _build_directory(folder_path):
    for dirname in ['sql', 'data', 'analysis']:
        dir_path = op.abspath(op.join(folder_path, dirname))
        if not op.exists(dir_path):
            os.mkdir(dir_path)

    return(folder_path)


def _decilize(arr):
    deciles = np.arange(1, 10) * 0.1
    arr_quantiles = np.quantile(arr, deciles)

    arr_dict = {f"{int(label*100)}%": arr_quantile for label, arr_quantile
                in zip(deciles, arr_quantiles)}
    # include the mean of resample distribution
    arr_dict['expected_mean'] = np.mean(arr)

    return arr_dict

def _make_metric_list(report):
    metric_list = list()
    for metric in report['metrics']:
        try:
            metric_list.append(getattr(desktop, metric))
        except AttributeError:
            print(f'`{metric}` is not a pre-defined Metric. Will skip')
    if 'user_defined_metrics' in report:
        for data_source, data_source_metrics \
                in report['user_defined_metrics'].items():
            for key, select_expr in data_source_metrics.items():
                new_metric = Metric(name=key,
                                    data_source=getattr(desktop,
                                                        data_source),
                                    select_expr=select_expr)
                metric_list.append(new_metric)

    return metric_list


# these helper functions addressed the issue that the results
# from analysis functions are pandas.Series
# see https://github.com/mozilla/mozanalysis/issues/71

# mean is mapped to exp for individual and comparative
# TODO: standardize to exp across mozanalysis
def _res_to_df_nest(metric, res):
    res_analysis = list()

    def tidy_data(stats, branch, analysis):
        stats = stats.reset_index()
        stats.rename(columns={'index': 'statistic'}, inplace=True)
        stats['metric'] = metric
        stats['analysis'] = analysis
        stats['branch'] = branch
        return stats
    if res.get('individual'):
        analysis = 'individual'
        for branch, stats in res[analysis].items():
            stats = tidy_data(stats, branch, analysis)
            res_analysis.append(stats)
    if res.get('comparative'):
        analysis = 'comparative'
        for branch, stats in res[analysis].items():
            for uplift in ['rel_uplift', 'abs_uplift']:
                stats_uplift = tidy_data(stats[uplift], branch, uplift)
                stats_uplift.rename(columns={'exp': 'mean'}, inplace=True)
                res_analysis.append(stats_uplift)
    res_analysis = pd.concat(res_analysis)

    return res_analysis

