import click

import stow
import pypdf
import fitz
import logging
from typing import List
import piexif
import arrow
import itertools
from typing import Optional

from PIL import Image

log = logging.getLogger(__name__)

@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug: bool):

    if debug:
        logging.basicConfig(level=logging.DEBUG)
        log.info('Debugging enabled')

@cli.command()
@click.argument('pdf_file')
def split(pdf_file: str):

    with open(pdf_file, 'rb') as handle:
        reader = pypdf.PdfReader(handle)

        page_num = 0
        while True:

            try:
                reader_page = reader.get_page(page_num)
                page_num += 1
            except Exception as e:
                break

            page_writer = pypdf.PdfWriter()
            page_writer.add_page(reader_page)

            destination = stow.abspath(stow.join(stow.dirname(pdf_file), stow.name(pdf_file) + f'-p{page_num}.pdf'))
            print('writing', destination)

            with open(destination, 'wb') as output_handle:
                page_writer.write(output_handle)


@cli.command()
@click.argument('files', nargs=-1)
@click.argument('output_path', nargs=1)
def merge(files: List[str], output_path: str):

    if not files:
        print('No files provided')

    pdfMerger = pypdf.PdfMerger()

    for file in files:
        print('merging', file)
        pdfMerger.append(file)

    print('writing to', output_path)
    pdfMerger.write(output_path)
    pdfMerger.close()

@cli.command()
@click.argument('file_path')
@click.option('--page-select')
@click.option('--out-path')
@click.option('--replace/--no-replace', default=False)
@click.option('--format')
@click.option('--date-taken')
def imageify(
    file_path: str,
    page_select: Optional[str] = None,
    out_path: Optional[str] = None,
    replace: bool = False,
    format: Optional[str] = None,
    date_taken: Optional[str] = None,
    ):
    """ Convert a PDF document into an image

    Args:
        file_path (str): The relative path to the file
        out_path (str, optional): The relative path to the output. Defaults to None.
        replace (bool, optional): Toggle to remove the original file. Defaults to False.
        format (str, optional): The format of the image to create. Defaults to None.
        date_created (str, optional): The ISO format of the time the image was created. Defaults to None.
    """

    if page_select is not None:
        pages = []
        for identifier in page_select.split(','):
            if '-' in identifier:
                start, end = identifier.split('-')
                pages.extend(range(int(start), int(end)))
            else:
                pages.append(int(identifier))

    else:
        pages = itertools.count(0, 1)


    if format is None:
        format = 'jpg'

    # Open and parse the pages of the document
    doc = fitz.open(file_path)

    images = []
    maxWidth, height = 0, 0

    for pageIndex in pages:

        try:
            page = doc.load_page(pageIndex)  # number of page
            pix = page.get_pixmap()
            image = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)

            maxWidth = max(maxWidth, image.width)
            height += image.height

            images.append(image)

        except:
            break

    doc.close()

    # Concatinate the images
    dst = Image.new('RGB', (maxWidth, height))

    pasted_height = 0
    for image in images:
        dst.paste(image, (0, pasted_height))
        pasted_height += image.height

    # Create the image metadata
    originalDatetime = arrow.get() if date_taken is None else arrow.get(date_taken)
    digitizedDatetime = arrow.get()

    exif_dict={
        'Exif':{
            piexif.ExifIFD.DateTimeOriginal: originalDatetime.strftime("%Y:%m:%d %H:%M:%S"),
            piexif.ExifIFD.DateTimeDigitized: digitizedDatetime.strftime("%Y:%m:%d %H:%M:%S"),
        }
    }


    # Write the image to disk
    if out_path is None:
        out_path = stow.join(stow.dirname(file_path), stow.name(file_path) + f'.{format}')

    print(f'saving file to {out_path}')
    dst.save(out_path, exif=piexif.dump(exif_dict))

    if replace:
        print(f'Removing original input file: {file_path}')
        stow.rm(file_path)
