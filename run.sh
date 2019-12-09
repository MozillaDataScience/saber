#!/bin/bash
echo Reading $1
cp template.Rmd $1/report.Rmd
mkdir $1/data
python derive_experiment.py $1
python aggregate_experiment.py $1
cd $1
Rscript -e "rmarkdown::render('report.Rmd')" && open report.html