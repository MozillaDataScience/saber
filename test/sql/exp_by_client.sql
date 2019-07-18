WITH exp AS
(
  SELECT scd.*,
         exp.experiment_branch,
         exp.enrollment_date
  FROM (
    SELECT client_id,
           experiment_branch,
           submission_date_s3,
           MIN(submission_date_s3) over(partition by client_id) as enrollment_date,
           COUNT(DISTINCT experiment_branch) over(partition by client_id) as n_branches
    FROM telemetry.experiments
    WHERE
        experiment_id = '@{spec$experiment_slug}'
        AND submission_date_s3 BETWEEN '@{spec$start}' AND '@{spec$end}'
  ) exp
  LEFT JOIN (
    SELECT *
    FROM `moz-fx-data-derived-datasets`.search.search_clients_daily_v6
    WHERE
        submission_date_s3 BETWEEN '@{spec$start}' AND '@{spec$end}'
  ) scd
  ON (exp.client_id = scd.client_id AND exp.submission_date_s3 = scd.submission_date_s3)
  WHERE 
      exp.enrollment_date BETWEEN '@{spec$start}' AND '@{spec$enrollment_end}'
      AND exp.n_branches = 1
),
exp_agg as (
  SELECT client_id,
         experiment_branch,
         DATE_DIFF(submission_date_s3, enrollment_date, DAY) as days_since_enrollment,
         engine,
         SUM(COALESCE(sap, 0)) as sap,
         SUM(COALESCE(tagged_sap, 0)) as tagged_sap,
         SUM(COALESCE(tagged_follow_on, 0)) as tagged_follow_on,
         SUM(COALESCE(organic, 0)) as organic,
         SUM(COALESCE(search_with_ads, 0)) as search_with_ads,
         SUM(COALESCE(ad_click, 0)) as ad_clicks
   FROM exp
   GROUP BY 1, 2, 3, 4
),

client_agg as (
  SELECT experiment_branch,
         client_id,
         --standard search metrics
         SUM(sap) as sap,
         SUM(tagged_sap) as tagged_sap,
         SUM(tagged_follow_on) as tagged_follow_on,
         SUM(organic) as organic,
         SUM(search_with_ads) as search_with_ads,
         SUM(ad_clicks) as ad_clicks,
         --add special engine fields here
         SUM(
          COALESCE(
            CASE
              WHEN engine like 'google%' THEN sap
              ELSE 0 END
          )
         ) as google,
         --average search metrics per client per day
         AVG(sap) as sap_avg,
         AVG(tagged_sap) as tagged_sap_avg,
         AVG(tagged_follow_on) as tagged_follow_on_avg,
         AVG(organic) as organic_avg,
         AVG(search_with_ads) as search_with_ads_avg,
         AVG(ad_clicks) as ad_clicks_avg,
         AVG(
          COALESCE(
            CASE
              WHEN engine like 'google%' THEN sap
              ELSE 0 END
          )
         ) as google_avg
   FROM exp_agg
   GROUP BY 1, 2
)

SELECT *
FROM client_agg
