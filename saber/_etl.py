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


def _build_directory(folder_path):
    for dirname in ['sql', 'data', 'analysis']:
        dir_path = op.abspath(op.join(folder_path, dirname))
        if not op.exists(dir_path):
            os.mkdir(dir_path)

    return(folder_path)


def dry_run_query(exp_path, metric_list):
    report = validate_schema(op.join(exp_path, "report.json"))

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


def initialize_experiment(exp_path):
    exp_path = op.abspath(exp_path)
    report = validate_schema(op.join(exp_path, "report.json"))

    exp = Experiment(
        experiment_slug=report["experiment_slug"],
        start_date=report["start_date"],
        num_dates_enrollment=report["num_dates_enrollment"]
    )

    return exp, report


def make_metric_list(report):
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


def run_etl(exp_path, overwrite=False):
    exp, report = initialize_experiment(exp_path)
    _build_directory(exp_path)

    FILENAME_ANALYSIS_DATA = op.join(exp_path, 'data',
                                    f'{report["last_date_full_data"]}_'
                                    f'{report["experiment_slug"]}.csv')
    deciles = np.arange(1, 10) * 0.1
    ci_quantiles = (0.005, 0.025, 0.5, 0.975, 0.995)
    quantiles = np.unique(np.hstack((deciles, ci_quantiles)))
    quantiles.sort()

    bq_context = BigQueryContext(dataset_id=report["dataset_id"])

    metric_list = make_metric_list(report)

    single_window_res = exp.get_single_window_data(
        bq_context=bq_context,
        metric_list=metric_list,
        last_date_full_data=report["last_date_full_data"],
        analysis_start_days=report["analysis_start_days"],
        analysis_length_days=report["analysis_length_days"]
    )

    query = dry_run_query(exp_path, metric_list)
    FILENAME_SQL = op.join(exp_path, 'sql',
                           f'{report["last_date_full_data"]}_'
                           f'{report["experiment_slug"]}.sql')
    oserror_msg = "File exists and overwrite was set to False."
    if not op.exists(FILENAME_SQL) or overwrite:
        open(FILENAME_SQL, 'w').write(query)
    else:
        raise OSError(oserror_msg)

    metric_names = [metric.name for metric in metric_list]

    single_window_res.dropna(inplace=True)

    # these helper functions addressed the issue that the results
    # from analysis functions are pandas.Series
    # see https://github.com/mozilla/mozanalysis/issues/71
    def multiindexed_series_to_dict(s):
        return {
            l: s[l].to_dict() for l in s.index.levels[0]
        }

    # mean is mapped to exp for individual and comparative
    # TODO: standardize to exp across mozanalysis
    def ma_sres_to_dict_nest(metric, res):
        res_analysis = list()
        if res.get('individual'):
            for branch, stats in res['individual'].items():
                ind = stats.to_dict()
                ind['exp'] = ind.pop('mean')
                ind['analysis'] = 'individual'
                ind['metric'] = metric
                ind['branch'] = branch
                res_analysis.append(ind)
        if res.get('comparative'):
            for branch, stats in res['comparative'].items():
                stats = multiindexed_series_to_dict(stats)
                for analysis, stats in stats.items():
                    if analysis in ('max_abs_diff', 'prob_win'):
                        continue
                    comp = dict()
                    comp['analysis'] = analysis
                    comp['metric'] = metric
                    comp['branch'] = branch
                    comp.update(stats)
                    res_analysis.append(comp)
        return res_analysis

    res_metrics = list()
    for metric in metric_names:
        res_metric = ma_sres_to_dict_nest(
            metric,
            mafsb.compare_branches(
                single_window_res,
                metric, threshold_quantile=0.999,
                individual_summary_quantiles=list(quantiles),
                comparative_summary_quantiles=list(quantiles),
                num_samples = report['n_resamples']
            )
        )
        res_metrics.extend(res_metric)

    res_metrics = pd.DataFrame(res_metrics)
    if not op.exists(FILENAME_ANALYSIS_DATA) or overwrite:
        res_metrics.to_csv(FILENAME_ANALYSIS_DATA, index=False)
    else:
        raise OSError(oserror_msg)


    return res_metrics
