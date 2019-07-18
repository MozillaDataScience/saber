WITH exp AS
(
  SELECT scd.*,
         exp.experiment_branch
  FROM (
    SELECT client_id,
           experiment_branch,
           submission_date_s3,
           MIN(submission_date_s3) over(partition by client_id) as enrollment_date
    FROM telemetry.experiments
    WHERE
        experiment_id = '@{EXPERIMENT_SLUG}'
        AND submission_date_s3 BETWEEN '@{START_DATE}' AND '@{END_DATE}'
  ) exp
  LEFT JOIN (
    SELECT *
    FROM `moz-fx-data-derived-datasets`.search.search_clients_daily_v7
    WHERE
        submission_date_s3 BETWEEN '@{START_DATE}' AND '@{END_DATE}'
  ) scd
  ON (exp.client_id = scd.client_id AND exp.submission_date_s3 = scd.submission_date_s3)
  WHERE 
      exp.enrollment_date <= '@{ENROLLMENT_END}'
)