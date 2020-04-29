# Install and/or Import Packages for the R Session
helper_funcs.ipak <- function(pkg){
  new.pkg <- pkg[!(pkg %in% installed.packages()[, "Package"])]
  if (length(new.pkg))
    install.packages(new.pkg, dependencies = TRUE)
  p <- sapply(pkg, require, character.only = TRUE)
}

# Takes a tidy dataframe and splits it on branch.
# This creates a streamline way to iterate plots and tables.
helper_funcs.create_summary_list <- function(df, alpha_level=.01) {
  ci <- c((alpha_level/2), (1-(alpha_level/2)))
  ci_cols <- sapply(ci, toString)
  
  rel_uplift <- df %>% filter(analysis == 'rel_uplift')
  
  # figure out why there are nans in the results
  rel_uplift[is.na(rel_uplift)] = 0
  
  rel_uplift['sig'] = sign(rel_uplift[ci_cols[1]] * rel_uplift[ci_cols[2]])
  rel_uplift <- rel_uplift %>% mutate(sig = if_else(sig == 0, -1, sig))
  rel_uplift$sig <- factor(rel_uplift$sig)
  
  rel_uplift <- rel_uplift %>% rename(lower_ci = ci_cols[1],
                                      upper_ci = ci_cols[2])
  
  branches <- pull(rel_uplift['branch']) %>% unique()
  
  # create ci column
  ci_bound <- as.character((1 - alpha_level) * 100)
  rel_uplift$ci_formatted <- paste0(ci_bound, "% CI [ ",
                                    round(pull(rel_uplift, lower_ci), 4)*100,
                                    "%, ",
                                    round(pull(rel_uplift, upper_ci), 4)*100, "% ]")
  rel_uplift$mean_formatted <- paste0(round(pull(rel_uplift, mean), 4)*100, "%")
  
  summary_list <- split(rel_uplift, f=rel_uplift$branch)
  
  return(summary_list)
}

# Takes a df and makes a summary plot
helper_funcs.create_plot <- function(metric_summary) {
  metric_summary <- metric_summary %>% filter(statistic == 'expected_mean')
  ggplot(metric_summary, aes(x=metric, y=mean, colour=sig)) +
    geom_errorbar(aes(ymin=lower_ci,
                      ymax=upper_ci),
                  width = .1) +
    geom_point(size=2) +
    coord_flip(ylim=c(-.1, .1)) + theme_bw() + theme(legend.position="bottom",
                                                     legend.title=element_blank()) +
    xlab("") + ylab("% Change") +
    labs(title='Percent Change Estimates',
         subtitle=paste0("(", first(metric_summary$branch), " - Control), with 99% CIs")) +
    geom_hline(yintercept = 0, linetype=2) + scale_y_continuous(labels = function(x) paste0(x*100, "%")) +
    # #ff2e2e is red
    scale_color_manual(values=c("1"='#008000', "-1"='grey'), labels=c('1'="Reliable Change", '-1'="No Reliable Change"))
  
}

# Takes a df and makes a facet of decile plots
helper_funcs.plot_pct_changes_decile <- function(metric_summary) {
  
  metric_summary <- metric_summary %>% filter(statistic != 'expected_mean')
  
  branch <- first(metric_summary$branch)
  ggplot(metric_summary, aes(x=mean, y=statistic)) +
    geom_point(size=2, alpha=.5) +
    geom_errorbarh(aes(xmin=lower_ci,
                       xmax=upper_ci),
                   width = .1) +
    facet_wrap(~metric) +
    theme_bw() + theme(legend.position="bottom", legend.title=element_blank()) +
    xlab("% Change") + ylab("Decile") +
    labs(title='Percent Change Estimates by Decile',
         subtitle=paste0("(", branch, " - Control)")) +
    geom_vline(xintercept = 0, linetype=2) +
    scale_x_continuous(labels = scales::percent) + xlim(-.1, .1)
}

# Takes a df and makes a DT table
helper_funcs.create_table <- function(metric_summary)  {
  # since summary is split by branch, this could be any element from the column
  branch_name <- first(metric_summary$branch)
  metric_summary <- metric_summary %>% filter(statistic == 'expected_mean') %>% select(metric,  
                                                                                       mean_formatted, ci_formatted,
                                                                                       sig, branch)
  # generate the table
  datatable(metric_summary,
            fillContainer=TRUE,
            colnames= c('Metric of Interest' = 'metric',
                        'Percentage Change' = 'mean_formatted',
                        'Confidence Interval' = 'ci_formatted',
                        'Significance' = 'sig'),
            caption=paste0("Overall Percentage Changes for Each Each Metric\n(`",
                           branch_name, "` - `control`)"),
            options=list(
              autoWidth = TRUE,
              dom="t",
              columnDefs=list(
                list(className='dt-left', targets=2),
                list(visible=F, targets=c(4,5))
              ),
              order = list(list(abs(5), 'desc'))
            ),
  ) %>%
    formatPercentage("Metric of Interest", 2) %>%
    formatStyle(
      "Significance",
      color = styleEqual(c(-1, 0, 1), c("grey", "blue", "blue")),
      fontWeight = styleEqual(c(-1, 1), c("regular", "bold"))
    ) %>%
    formatStyle(c(1),
                fontWeight = "bold"
    ) %>% return()
}
