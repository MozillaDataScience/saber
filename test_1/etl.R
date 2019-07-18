ipak <- function(pkg){
  new.pkg <- pkg[!(pkg %in% installed.packages()[, "Package"])]
  if (length(new.pkg)) 
    install.packages(new.pkg, dependencies = TRUE)
  p <- sapply(pkg, require, character.only = TRUE)
}

packages <- c("bigrquery", "ggplot2", "DBI", "data.table",
              "reshape2", "DT", "GetoptLong", "readr", "rjson")
ipak(packages)


spec <- fromJSON(file="experiment.json")
GA_CREDENTIALS_PATH <- "/home/bmiroglio/.gcp/cred.json"
REPROCESS <- spec$reprocess_etl
# setup code a la saptarshi
Sys.setenv("GOOGLE_APPLICATION_CREDENTIALS"=GA_CREDENTIALS_PATH)
bq <- function(fullTable=F){
  set_service_token("~/.gcp/cred.json")
  ocon <- dbConnect(
    bigrquery::bigquery(),
    project = "moz-fx-data-derived-datasets",
    dataset = 'telemetry'
  )
  w <- dbListTables(ocon)
  nrows = ifelse(fullTable, -1, 200)
  adhoc <- function(s,n=nrows, con=NULL){
    ## be careful with n=-1 !!
    ## which returns *all* the rows
    if(is.null(con)) con <- ocon
    data.table(dbGetQuery(con, s, n = n))
  }
  return(list(w=w,con=ocon, query=adhoc))
}

sql_by_branch <- qq(read_file("./sql/exp_by_branch.sql"))
sql_by_client <- qq(read_file("./sql/exp_by_client.sql"))

if (REPROCESS) {      
  g <- bq(fullTable=T)
  exp_branch <- g$q(sql_by_branch)
  exp_client <- g$q(sql_by_client)
  # get normalized volume by branch, date
  exp_branch <- exp_branch[,c("sap_norm",
                              "tagged_sap_norm",
                              "tagged_follow_on_norm",
                              "organic_norm",
                              "search_with_ads_norm",
                              "ad_clicks_norm",
                              "google_norm"):=list(
                                sap/n_clients,
                                tagged_sap/n_clients,
                                tagged_follow_on/n_clients,
                                organic/n_clients,
                                search_with_ads/n_clients,
                                ad_clicks/n_clients,
                                google/n_clients
                              )]
  exp_branch$experiment_branch <- factor(exp_branch$experiment_branch)
  exp_client$experiment_branch <- factor(exp_client$experiment_branch)
  write.csv(exp_branch, "./data/exp_branch.csv",, row.names = F)
  write.csv(exp_client, "./data/exp_client.csv", row.names = F)
} else {
  exp_branch <- fread("cat ./data/exp_branch.csv")
  exp_client <- fread("cat ./data/exp_client.csv")
  
}

if (REPROCESS) system("python2 boot.py")