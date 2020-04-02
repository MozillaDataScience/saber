import os
import os.path as op
from optparse import OptionParser
import etl


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

    for dirname in ['sql', 'data', 'analysis']:
        dir_path = op.join(folder_path, dirname)
        if not op.exists(dir_path):
            os.mkdir(dir_path)
    etl.run_etl(exp_path)