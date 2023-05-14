import click

import stow
import pypdf
from typing import List



def merge(files: List[stow.File], output_path: str):

    pdfMerger = pypdf.PdfMerger()

    for file in files:
        pdfMerger.append(file.abspath)

    pdfMerger.write(output_path)
    pdfMerger.close()



@click.command()
@click.option("--files", default=[], multiple=True)
@click.option("--output", required=True, type=str)
def main(files: List[str] = None, output: str = None):

    # Check each file
    files = [stow.artefact(path) for path in files]

    if not files:
        print('Files must be provided')

    merge(files, output_path=output)
