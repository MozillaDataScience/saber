import numpy as np
import os.path as op
import json
from datetime import date
from collections import OrderedDict
import pandas as pd

from mozanalysis.metrics import Metric
import mozanalysis.metrics.desktop as desktop
import mozanalysis.frequentist_stats.bootstrap as mafsb
from mozanalysis.experiment import Experiment, TimeLimits
from mozanalysis.bq import BigQueryContext


def run_etl(exp_path):
    exp_path = op.abspath(exp_path)
    experiment = json.load(open(op.join(exp_path, "experiment.json")))
    report = json.load(open(op.join(exp_path, "report.json")))

    EXP_NAME = experiment["experiment_name"]
    DATE = date.today()
    FILENAME_ANALYSIS_DATA = op.join(exp_path, 'data',
                                    f'{experiment["last_date_full_data"]}_'
                                    f'{report["experiment_slug"]}.csv')
    FILENAME_SQL = op.join(exp_path, 'sql',
                           f'{experiment["last_date_full_data"]}_'
                           f'{report["experiment_slug"]}.sql')

    deciles = np.arange(1, 10) * 0.1
    ci_quantiles = (0.005, 0.025, 0.5, 0.975, 0.995)
    quantiles = np.unique(np.hstack((deciles, ci_quantiles)))
    quantiles.sort()

    bq_context = BigQueryContext(dataset_id=experiment["dataset_id"])

    exp = Experiment(
        experiment_slug=report["experiment_slug"],
        start_date=experiment["start_date"],
        num_dates_enrollment=experiment["num_dates_enrollment"]
    )

    metric_list = [
        Metric(name=key, data_source=getattr(desktop, data_source),
            select_expr=value['select_expr']
                if isinstance(value['select_expr'], str)
                else ' '.join(value['select_expr']))
        for data_source, data_source_metrics in experiment['metrics'].items()
        for key, value in data_source_metrics.items()
    ]

    single_window_res = exp.get_single_window_data(
        bq_context=bq_context,
        metric_list=metric_list,
        last_date_full_data=experiment["last_date_full_data"],
        analysis_start_days=experiment["analysis_start_days"],
        analysis_length_days=experiment["analysis_length_days"]
    )
    # create an archive of the sql generating analysis
    time_limits = TimeLimits.for_single_analysis_window(
        first_enrollment_date=experiment['start_date'],
        last_date_full_data=experiment['last_date_full_data'],
        analysis_start_days=experiment['analysis_start_days'],
        analysis_length_dates=experiment['analysis_length_days'],
        num_dates_enrollment=experiment['num_dates_enrollment'])
    query = exp._build_query(metric_list=metric_list, time_limits=time_limits,
                            enrollments_query_type='normandy')
    open(FILENAME_SQL, 'w').write(query)

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
                num_samples = experiment['n_resamples']
            )
        )
        res_metrics.extend(res_metric)

    res_metrics = pd.DataFrame(res_metrics)
    res_metrics.to_csv(FILENAME_ANALYSIS_DATA, index=False)
