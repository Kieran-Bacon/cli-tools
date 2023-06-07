import click

import stow
import pypdf
import fitz
import logging
from typing import List

from PIL import Image

log = logging.getLogger(__name__)

@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug: bool):

    if debug:
        logging.basicConfig(level=logging.DEBUG)
        log.info('Debugging enabled')

@cli.command()
@click.argument('files', nargs=-1)
@click.argument('output_path', nargs=1)
def merge(files: List[str], output_path: str):

    pdfMerger = pypdf.PdfMerger()

    for file in files:
        pdfMerger.append(file)

    pdfMerger.write(output_path)
    pdfMerger.close()

@cli.command()
@click.argument('file_path')
@click.option('--out-path')
@click.option('--replace/--no-replace', default=False)
@click.option('--format')
def imageify(file_path: str, out_path: str = None, replace: bool = False, format: str = None):

    if format is None:
        format = 'jpg'

    doc = fitz.open(file_path)

    pageIndex = 0
    images = []
    maxWidth, height = 0, 0

    while True:

        try:
            page = doc.load_page(pageIndex)  # number of page
            pix = page.get_pixmap()
            image = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)

            maxWidth = max(maxWidth, image.width)
            height += image.height

            images.append(image)
            pageIndex += 1

        except:
            break

    # Concatinate the images

    dst = Image.new('RGB', (maxWidth, height))

    pasted_height = 0
    for image in images:
        dst.paste(image, (0, pasted_height))
        pasted_height += image.height

    replacepath = stow.join(stow.dirname(file_path), stow.name(file_path) + f'.{format}')
    if replace:
        dst.save(replacepath)
        stow.rm(file_path)

    else:
        if out_path is None:
            out_path = replacepath
        print(f'saving file to {out_path}')
        dst.save(out_path)

    doc.close()
