render_pct_change_table <- function(metrics, s=summary) {
  if (metrics!="*") s <- s[Metric %in% metrics]
  # get (1-alpha) CI from bootstrap
  # and merge with experiment result
  datatable(s,
            caption="Overall % Changes (Treatment - Control) for Each Metric",
            options=list(
              dom='t',
              columnDefs=list(
                list(targets=c(2, 3, 6, 7), visible=F),
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
  l <- min(quantile(s$lower, .025), 0)
  u <- max(quantile(s$upper, .975), 0)
  s$color <- factor(s$color)
  ggplot(s, aes(x=Metric, y=`Percent Change`, colour=color)) +
    geom_errorbar(aes(ymin=lower, 
                      ymax=upper), 
                  width = .1) +
    geom_point(size=2) +
    coord_flip(ylim=c(l, u)) + theme_bw() + theme(legend.position="bottom", 
                                                  legend.title=element_blank()) +
    xlab("") + ylab("% Change") + 
    labs(title='Percent Change Estimates',
         subtitle="(Treatment - Control), with 99% CIs") +
    geom_hline(yintercept = 0, linetype=2) + scale_y_continuous(labels = function(x) paste0(x*100, "%")) +
    scale_color_manual(values=c("0"='#008000', "1"='grey', "2"='#ff2e2e'), labels=c("0"="Positive Change", '1'="No Change", '2'="Negative Change"))
  
}

create_summary <- function(b=boot, r=result, alpha=.01) {
  of <- merge(
    boot[,.(lower=quantile(change, alpha/2, na.rm=T),
             upper=quantile(change, 1-(alpha/2), na.rm=T)),
          .(Metric)],
    r,
    by='Metric')
  # construct human readable ci and color code based on whether or not
  # the result is significant
  of$ci <- paste("(", round(of$lower, 4)*100, "%, ", round(of$upper, 4)*100, "%)", sep="")
  of$color <- ifelse(of$upper < 0, 2, as.numeric(of$lower + of$upper > of$lower & (of$lower - .001) < 0))
  of <- na.omit(of) # for now, ad_clicks missing from gcp
  setnames(of, old=c('ci'), new = c(paste(as.character((1-alpha)*100), "% Confidence Interval", sep='')))
  of$abs_change <- abs(of$`Percent Change`)
  of
}

plot_enrollment_by_day <- function() {
ggplot(exp_melted[variable=="n_clients"], aes(x=days_since_enrollment, y=value, color=experiment_branch)) +
  geom_line() + theme_bw()
}

plot_metrics_by_day <- function() {
  ggplot(exp_melted[variable!="n_clients"], aes(x=days_since_enrollment, y=value, color=experiment_branch)) +
    geom_line() +
    facet_wrap(. ~ variable, scales="free_y", ncol=7) +
    theme_bw()
}


