with exp as (
    SELECT
        client_id,
        `moz-fx-data-shared-prod.udf.get_key`(event_map_values, 'branch') AS experiment_branch,
        MIN(submission_date) as enrollment_date,
        COUNT(submission_date) as num_enrollment_events
    FROM
      `moz-fx-data-shared-prod.telemetry.events`
    WHERE 
      submission_date BETWEEN @start_date AND @end_date
      AND event_string_value = @experiment_slug
      AND event_category = 'normandy'
      AND event_method = 'enroll'
    GROUP BY 1, 2
),

scd AS (
  SELECT *
  FROM `moz-fx-data-derived-datasets`.search.search_clients_daily
  WHERE 
      submission_date_s3 BETWEEN @start_date AND @end_date
)


SELECT  exp.*,
        scd.engine,
        scd.source,
        scd.submission_date_s3 as submission_date,
        COALESCE(scd.sap, 0) as sap,
        COALESCE(scd.ad_click, 0) as ad_click,
        COALESCE(scd.search_with_ads, 0) as search_with_ads,
        COALESCE(scd.tagged_sap, 0) as tagged_sap,
        COALESCE(scd.tagged_follow_on, 0) as tagged_follow_on,
        COALESCE(scd.organic, 0) as organic
FROM exp
LEFT JOIN scd
USING (client_id)
WHERE 
  enrollment_date <= @enrollment_end_date

