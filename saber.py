import os
import os.path as op
from optparse import OptionParser
import etl
import shutil
import subprocess


version = 'v2.0'
description = 'Search A/B Experiment Report'


def run():
    """Run command."""
    from mne.commands.utils import get_optparser

    parser = get_optparser(__file__)

    parser = OptionParser(prog='saber', version=version,
                          description=description)
    parser.add_option('-f', '--folder', dest='folder_path',
                      help='The folder path')


    options, args = parser.parse_args()
    exp_path = options.folder_path

    # run the ETL
    etl.run_etl(exp_path)

    # copy over the template report
    rmd_file = op.join(exp_path, 'index.Rmd')
    html_file = op.join(exp_path, 'index.Rmd')
    shutil.copyfile('template.Rmd', rmd_file)

    # knit the preliminary report
    subprocess.run(["R", "-e",
                    (f"rmarkdown::render('{rmd_file}',"
                     f"output_file='{op.join(exp_path, index.html)}')")
    ])

)
