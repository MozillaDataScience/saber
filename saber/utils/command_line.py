import os
import os.path as op
import shutil
import subprocess
from argparse import ArgumentParser
import webbrowser
import json

import _etl

description = 'SABER: Swift A/B Experiment Report'


def run():
    """Run command."""
    parser = ArgumentParser(prog='run',
                            description=description)
    parser.add_argument('-p', dest='folder_path',
                        help='The folder path', default=None)
    parser.add_argument('-f', dest='overwrite', action='store_true',
                        help='Force an overwrite')
    parser.add_argument('-o', dest='openbrowser', action='store_true',
                        help='Open report in web browser')

    args = parser.parse_args()
    exp_path = op.abspath(args.folder_path)
    overwrite = args.overwrite
    openbrowser = args.openbrowser
    if not args.folder_path:
        raise IndexError('Missing folder argument.')

    # create template files
    template = op.join('{}', '{}')
    rmd_folder = template.format('{}', 'src')
    r_file = template.format('{}', 'helper_funcs.R')
    img_file = template.format('{}', 'design.png')
    html_file = template.format(exp_path, 'index.html')
    report_file = template.format(exp_path, 'report.json')
    saber_dir = op.abspath(op.join(op.dirname(__file__), '..'))

    # check to make sure you're not overwriting
    if op.exists(rmd_folder.format(exp_path)) and not overwrite:
        raise OSError("Folder already exists!")

    # run the ETL
    print("Proceeding to etl...")
    # _etl.run_etl(exp_path, overwrite)

    # copy over files
    shutil.copytree(rmd_folder.format(op.join(saber_dir, 'template')),
                    rmd_folder.format(exp_path))
    shutil.copyfile(r_file.format(op.join(saber_dir, 'template')),
                    r_file.format(exp_path))
    if not op.exists(img_file.format(exp_path)):
        shutil.copyfile(img_file.format(op.join(saber_dir, 'template')),
                        img_file.format(exp_path))

    # create yaml files
    report = json.load(open(report_file))
    with open(op.join(exp_path, 'src', '_config.yml'), 'w') as FILE:
        FILE.write(f"""title: '{report['title']}'
author: '{report['author']} <<{report['email']}>>'
date: '{report['publish_date']}'""")

    # build the preliminary report
    subprocess.run(["jupyter-book", "build", rmd_folder.format(exp_path)])
    # if openbrowser:
    #     webbrowser.open_new_tab(('file://' + op.abspath(html_file)))
