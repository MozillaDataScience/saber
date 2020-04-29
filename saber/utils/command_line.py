import os
import os.path as op
import shutil
import subprocess
from argparse import ArgumentParser
import webbrowser

import _etl

description = 'SABER: Search A/B Experiment Report'


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
    rmd_file = template.format('{}', 'index.Rmd')
    r_file = template.format('{}', 'helper_funcs.R')
    img_file = template.format('{}', 'design.png')
    html_file = template.format(exp_path, 'index.html')
    saber_dir = op.abspath(op.join(op.dirname(__file__), '..'))

    # check to make sure you're not overwriting
    if op.exists(rmd_file.format(exp_path)) and not overwrite:
        raise OSError("File already exists!")

    # run the ETL
    print("Proceeding to etl...")
    _etl.run_etl(exp_path, overwrite)

    # copy over files
    shutil.copyfile(rmd_file.format(op.join(saber_dir, 'template')),
                    rmd_file.format(exp_path))
    shutil.copyfile(r_file.format(op.join(saber_dir, 'template')),
                    r_file.format(exp_path))
    if not op.exists(img_file.format(op.join(exp_path, 'template'))):
        shutil.copyfile(img_file.format(op.join(saber_dir, 'template')),
                        img_file.format(exp_path))

    # knit the preliminary report
    subprocess.run(["R", "-e",
                    (f"rmarkdown::render('{rmd_file.format(exp_path)}',"
                     f"output_file='{html_file}')")
                    ])
    if openbrowser:
        webbrowser.open_new_tab(('file://' + op.abspath(html_file)))
