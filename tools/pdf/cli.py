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
@click.argument('target', help='The file to have pages inserted into')
@click.argument('source', help='The source file to have pages pulled from to insert')
@click.argument('destination', help='The final output location')
@click.argument('page_selection', help='Select the pages that are being extracted from source')
@click.argument('location_select', help='Select the locations for those pages, must be one to one with page_select')
def insert(target, source, destination, page_selection, location_selection):

    if not stow.exists(target) or not stow.exists(source) or stow.exists(destination):
        print('Files specified are not allowed')
        exit()

    page_selection_indexes = [int(x) for x in page_selection.split(',')]
    location_selection_indexes = [int(x) for x in location_selection.split(',')]

    if len(page_selection_indexes) != location_selection_indexes:
        print(f'You page selection and location selection must be the same length :: {len(page_selection_indexes)}, {len(location_selection_indexes)}')
        exit()






    pass

@cli.command()
@click.argument('files', nargs=-1)
@click.argument('output_path', nargs=1)
def merge(files: List[str], output_path: str):

    if not files:
        print('No files provided')
        exit()

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
