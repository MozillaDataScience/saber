ipak <- function(pkg){
  new.pkg <- pkg[!(pkg %in% installed.packages()[, "Package"])]
  if (length(new.pkg)) 
    install.packages(new.pkg, dependencies = TRUE)
  p <- sapply(pkg, require, character.only = TRUE)
}

render_pct_change_table <- function(metrics, s=summary) {
  if (metrics!="*") s <- s[Metric %in% metrics]
  # get (1-alpha) CI from bootstrap
  # and merge with experiment result
  datatable(s,
            caption="Overall % Changes (Treatment - Control) for Each Metric",
            options=list(
              dom='t',
              columnDefs=list(
                list(targets=c(3, 4, 6, 7), visible=F),
                list(className='dt-right', targets=5)
              ),
              order = list(list(abs(7), 'desc'))
            )
  ) %>%
    formatPercentage("Percent Change", 2) %>%
    formatStyle(
      "Percent Change", "color",
      color = styleEqual(c(0, 1, 2), c("green", "grey", "red")),
      fontWeight = styleEqual(c(0, 2), c("bold", "bold"))
    ) %>%
    formatStyle(c(1),
                fontWeight = "bold")
}

plot_pct_changes <- function(metrics, s=summary) {
  if (metrics!="*") s <- s[Metric %in% metrics]
  s$color <- factor(s$color)
  ggplot(s, aes(x=Metric, y=`Percent Change`, colour=color)) +
    geom_errorbar(aes(ymin=lower, 
                      ymax=upper), 
                  width = .1) +
    geom_point(size=2) +
    coord_flip(ylim=c(-.1, .1)) + theme_bw() + theme(legend.position="bottom", 
                                                  legend.title=element_blank()) +
    xlab("") + ylab("% Change") + 
    labs(title='Percent Change Estimates',
         subtitle="(Treatment - Control), with 99% CIs") +
    geom_hline(yintercept = 0, linetype=2) + scale_y_continuous(labels = function(x) paste0(x*100, "%")) +
    scale_color_manual(values=c("0"='#008000', "1"='grey', "2"='#ff2e2e'), labels=c("0"="Positive Change", '1'="No Change", '2'="Negative Change"))
  
}

plot_pct_changes_decile <- function(s) {
  s$bucket <- ifelse(s$bucket < 10, 90 + s$bucket, s$bucket)
  s$bucket <- ifelse(s$bucket == 10, 99.9, s$bucket)
  s$bucket <- ifelse(s$bucket == 11, 99.99, s$bucket)
  s$color <- factor(ifelse(s$`Percent Change` == 0, 1, s$color))
  sig_pct <- s[,.(pct=mean(ifelse(color!=1, 1, 0))), bucket]
  s$color <- factor(s$color)
  tlabel = "% showed changes"
  s <- merge(s, sig_pct, by="bucket")
  ggplot(s, aes(x=bucket, y=`Percent Change`, colour=color)) +
    geom_point(size=2, position=position_dodge(width=0.2), alpha=.5) +
    geom_errorbar(aes(ymin=lower, 
                      ymax=upper), 
                  width = .2, position = 'dodge', alpha=.2) +
     theme_bw() + theme(legend.position="bottom", 
                                                  legend.title=element_blank()) +
    xlab("") + ylab("% Change") + 
    labs(title='Percent Change Estimates',
         subtitle="(Treatment - Control), with 99% CIs") +
    geom_hline(yintercept = 0, linetype=2) +
    scale_y_continuous(labels = scales::percent) +
    scale_color_manual(values=c("0"='#008000', "1"='grey', "2"='#ff2e2e'), labels=c("0"="Positive Change", '1'="No Change", '2'="Negative Change"))

  
}

create_summary <- function(of, alpha=.01) {
  # construct human readable ci and col   or code based on whether or not
  # the result is significant
  of$ci <- paste("(", round(of$lower, 4)*100, "%, ", round(of$upper, 4)*100, "%)", sep="")
  of$color <- ifelse(of$upper < 0, 2, as.numeric(of$lower + of$upper > of$lower & (of$lower - .00001) < 0))
  of <- na.omit(of) # for now, ad_clicks missing from gcp
  setnames(of, old=c('ci'), new = c(paste(as.character((1-alpha)*100), "% Confidence Interval", sep='')))
  of$abs_change <- abs(of$`Percent Change`)
  of
}

create_summary_dist <- function(b=boot, r=result, alpha=.01) {
  of <- merge(
    b[,.(lower=quantile(change, alpha/2, na.rm=T),
             upper=quantile(change, 1-(alpha/2), na.rm=T)),
          .(Metric, bucket)],
    r,
    by=c('Metric', 'bucket'))
  # construct human readable ci and color code based on whether or not
  # the result is significant
  of$ci <- paste("(", round(of$lower, 4)*100, "%, ", round(of$upper, 4)*100, "%)", sep="")
  of$color <- ifelse(of$upper < 0, 2, as.numeric(of$lower + of$upper > of$lower & (of$lower - .0001) < 0))
  of <- na.omit(of) # for now, ad_clicks missing from gcp
  setnames(of, old=c('ci'), new = c(paste(as.character((1-alpha)*100), "% Confidence Interval", sep='')))
  of$abs_change <- abs(of$`Percent Change`)
  of
}

plot_enrollment_by_day <- function() {
ggplot(exp_melted[variable=="n_clients"], aes(x=submission_date, y=value, color=experiment_branch)) +
  geom_line() + theme_bw() + labs(x="Submission Date", y="N Clients", title="N Clients enrolled in study over time")
}

plot_metrics_by_day <- function() {
  ggplot(exp_melted[variable!="n_clients"], aes(x=submission_date, y=value, color=experiment_branch)) +
    geom_line() +
    facet_wrap(. ~ variable, scales="free_y", ncol=7) +
    theme_bw()
}


