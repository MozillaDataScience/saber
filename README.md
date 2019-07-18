# SABER

This is an MVP of the SABER framework.

To test locally:

* Ensure you have GCP credentials somewhere locally and specify the path [here in `etl.R`](https://github.com/benmiroglio/saber/blob/master/test_1/etl.R#L14).
* `cd` into one of the test directories and open `experiments.json`. Set `reprocess_etl` to `true`.
* Make sure you have R/[RMarkdown](https://bookdown.org/yihui/rmarkdown/installation.html) installed (I recommend [Rstudio](https://www.rstudio.com/products/rstudio/download/) as well).
* Run `mkdir data && Rscript -e "rmarkdown::render('test.Rmd')" && open test.html` 

This is a prototype and more work needs to be done. I don't expect these steps to work without some kinks to start on a different machine.


The two successfully rendered test cases can be viewed [here](https://metrics.mozilla.com/~bmiroglio/saber_test/) (LDAP credentials required).
