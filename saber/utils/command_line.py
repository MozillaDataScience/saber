import os
import os.path as op
import shutil
from distutils.dir_util import copy_tree
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
    saber_dir = op.abspath(op.join(op.dirname(__file__), '..'))
    src_folder = op.join(saber_dir, 'template', 'src')
    exp_src_folder = op.join(exp_path, 'src')
    img_file = op.join(exp_path, 'design.png')

    html_file = op.join(exp_path, 'src', '_build', 'html', 'index.html')
    report_file = op.join(exp_path, 'report.json')

    # check to make sure you're not overwriting
    if op.exists(op.join(exp_path, 'src')) and not overwrite:
        raise OSError("Folder already exists!")

    # run the ETL
    print("Proceeding to etl...")
    _etl.run_etl(exp_path, overwrite)

    # copy over files
    copy_tree(src_folder, exp_src_folder)
    if op.exists(img_file):
        shutil.move(img_file,
                    op.join(exp_src_folder, 'images', op.basename(img_file)))

    # create yaml files
    report = json.load(open(report_file))
    with open(op.join(exp_path, 'src', '_config.yml'), 'w') as FILE:
        FILE.write(f"""\
title: '{report['title']}'
author: '{report['author']} <<{report['email']}>>'
date: '{report['publish_date']}'
logo: images/logo.png
""")

    # build the preliminary report
    subprocess.run(["jupyter-book", "build", exp_src_folder])
    if openbrowser:
        webbrowser.open_new_tab(('file://' + op.abspath(html_file)))
