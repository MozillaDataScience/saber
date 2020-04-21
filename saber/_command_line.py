import os
import os.path as op
from argparse import ArgumentParser
import etl
import shutil
import subprocess


description = 'Search A/B Experiment Report'


def run():
    """Run command."""
    parser = ArgumentParser(prog='run',
                            description=description)
    parser.add_argument('-p', dest='folder_path',
                        help='The folder path', default=None)
    parser.add_argument('-f', dest='overwrite', action='store_true',
                        help='Force an overwrite')

    args = parser.parse_args()
    exp_path = args.folder_path
    if not args.folder_path:
        raise IndexError('Missing folder argument.')

    # create template files
    template = op.join('{}', '{}')
    rmd_file = template.format('{}', 'index.Rmd')
    img_file = template.format('{}', 'design.png')
    html_file = template.format(exp_path, 'index.html')
    saber_dir = op.dirname(op.abspath(__file__))

    # check to make sure you're not overwriting
    if op.exists(rmd_file.format(exp_path)) and not args.overwrite:
        raise OSError("File already exists!")

    # run the ETL
    print("Proceeding to etl...")
    # etl.run_etl(exp_path)

    # copy over files
    shutil.copyfile(rmd_file.format(op.join(saber_dir, 'template')),
                    rmd_file.format(exp_path))
    if not op.exists(img_file):
        shutil.copyfile(img_file.format(op.join(saber_dir, 'template')),
                        img_file.format(exp_path))

    # knit the preliminary report
    subprocess.run(["R", "-e",
                    (f"rmarkdown::render('{rmd_file.format(exp_path)}',"
                     f"output_file='{html_file}')")
    ])
