SELECT 
  client_id,
  experiment_branch,
  --standard search metrics
  SUM(sap) as sap,
  SUM(tagged_sap) as tagged_sap,
  SUM(tagged_follow_on) as tagged_follow_on,
  SUM(organic) as organic,
  SUM(search_with_ads) as search_with_ads,
  SUM(ad_clicks) as ad_clicks,
  --add special engine fields here
  SUM(google) as google,
  --average search metrics per client per day
  --these have already been COALESCED to account for nulls
  AVG(sap) as sap_avg,
  AVG(tagged_sap) as tagged_sap_avg,
  AVG(tagged_follow_on) as tagged_follow_on_avg,
  AVG(organic) as organic_avg,
  AVG(search_with_ads) as search_with_ads_avg,
  AVG(ad_clicks) as ad_clicks_avg,
  AVG(google) as google_avg
FROM (
  SELECT 
   client_id,
   experiment_branch,
   submission_date,
   ANY_VALUE(enrollment_date) as enrollment_date,
   --standard search metrics
   SUM(sap) as sap,
   SUM(tagged_sap) as tagged_sap,
   SUM(tagged_follow_on) as tagged_follow_on,
   SUM(organic) as organic,
   SUM(search_with_ads) as search_with_ads,
   SUM(ad_click) as ad_clicks,
   --add special engine fields here
   SUM(
      CASE
        WHEN STARTS_WITH(engine, "google") THEN sap
        ELSE 0
      END
    ) as google
   FROM 
    `{}`
   GROUP BY 1, 2, 3
)
GROUP BY 1, 2