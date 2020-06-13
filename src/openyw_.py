"""Convert yWriter project to odt or csv. 

Input file format: yWriter
Output file format: odt (with visible or invisible chapter and scene tags) or csv.

Version @release

Copyright (c) 2020, peter88213
For further information see https://github.com/peter88213/PyWriter
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import sys
import os

from configparser import ConfigParser

from pywriter.globals import *
from pywriter.odt.odt_proof import OdtProof
from pywriter.odt.odt_manuscript import OdtManuscript
from pywriter.odt.odt_scenedesc import OdtSceneDesc
from pywriter.odt.odt_chapterdesc import OdtChapterDesc
from pywriter.odt.odt_partdesc import OdtPartDesc
from pywriter.yw.yw_file import YwFile
from pywriter.converter.yw_cnv import YwCnv
from pywriter.csv.csv_scenelist import CsvSceneList
from pywriter.csv.csv_plotlist import CsvPlotList
from pywriter.odt.odt_file import OdtFile
from pywriter.csv.csv_charlist import CsvCharList
from pywriter.csv.csv_loclist import CsvLocList
from pywriter.csv.csv_itemlist import CsvItemList

import uno

from uno_wrapper.uno_tools import *

INI_FILE = 'openyw.ini'


def run(sourcePath, suffix):

    fileName, FileExtension = os.path.splitext(sourcePath)

    if suffix == '':
        targetDoc = OdtFile(fileName + '.odt')

    elif suffix == PROOF_SUFFIX:
        targetDoc = OdtProof(fileName + suffix + '.odt')

    elif suffix == MANUSCRIPT_SUFFIX:
        targetDoc = OdtManuscript(fileName + suffix + '.odt')

    elif suffix == SCENEDESC_SUFFIX:
        targetDoc = OdtSceneDesc(fileName + suffix + '.odt')

    elif suffix == CHAPTERDESC_SUFFIX:
        targetDoc = OdtChapterDesc(fileName + suffix + '.odt')

    elif suffix == PARTDESC_SUFFIX:
        targetDoc = OdtPartDesc(fileName + suffix + '.odt')

    elif suffix == SCENELIST_SUFFIX:
        targetDoc = CsvSceneList(fileName + suffix + '.csv')

    elif suffix == PLOTLIST_SUFFIX:
        targetDoc = CsvPlotList(fileName + suffix + '.csv')

    elif suffix == CHARLIST_SUFFIX:
        targetDoc = CsvCharList(fileName + suffix + '.csv')

    elif suffix == LOCLIST_SUFFIX:
        targetDoc = CsvLocList(fileName + suffix + '.csv')

    elif suffix == ITEMLIST_SUFFIX:
        targetDoc = CsvItemList(fileName + suffix + '.csv')

    else:
        return('ERROR: Target file type not supported')

    ywFile = YwFile(sourcePath)
    converter = YwCnv()
    message = converter.yw_to_document(ywFile, targetDoc)

    return message


def open_yw7(suffix, newExt):

    # Set last opened yWriter project as default (if existing).

    scriptLocation = os.path.dirname(__file__)
    inifile = (scriptLocation + '/' + INI_FILE).replace('file:///',
                                                        '').replace('%20', ' ')
    defaultFile = None
    config = ConfigParser()

    try:
        config.read(inifile)
        ywLastOpen = config.get('FILES', 'yw_last_open')

        if os.path.isfile(ywLastOpen):
            defaultFile = 'file:///' + ywLastOpen.replace(' ', '%20')

    except:
        pass

    # Ask for yWriter 6 or 7 project to open:

    ywFile = FilePicker(path=defaultFile)

    if ywFile is None:
        return

    sourcePath = ywFile.replace('file:///', '').replace('%20', ' ')
    ywExt = os.path.splitext(sourcePath)[1]

    if not ywExt in ['.yw6', '.yw7']:
        msgbox('Please choose a yWriter 6/7 project.')
        return

    # Store selected yWriter project as "last opened".

    newFile = ywFile.replace(ywExt, suffix + newExt)
    dirName, filename = os.path.split(newFile)
    lockFile = (dirName + '/.~lock.' + filename +
                '#').replace('file:///', '').replace('%20', ' ')

    if not config.has_section('FILES'):
        config.add_section('FILES')

    config.set('FILES', 'yw_last_open', ywFile.replace(
        'file:///', '').replace('%20', ' '))

    with open(inifile, 'w') as f:
        config.write(f)

    # Check if import file is already open in LibreOffice:

    if os.path.isfile(lockFile):
        msgbox('Please close "' + filename + '" first.')
        return

    # Open yWriter project and convert data.

    workdir = os.path.dirname(sourcePath)
    os.chdir(workdir)
    result = run(sourcePath, suffix)

    if result.startswith('ERROR'):
        msgbox(result)

    else:
        desktop = XSCRIPTCONTEXT.getDesktop()
        doc = desktop.loadComponentFromURL(newFile, "_blank", 0, ())


def import_yw(*args):
    '''Import scenes from yWriter 6/7 to a Writer document
    without chapter and scene markers. 
    '''
    open_yw7('', '.odt')


def proof_yw(*args):
    '''Import scenes from yWriter 6/7 to a Writer document
    with visible chapter and scene markers. 
    '''
    open_yw7(PROOF_SUFFIX, '.odt')


def get_manuscript(*args):
    '''Import scenes from yWriter 6/7 to a Writer document
    with invisible chapter and scene markers. 
    '''
    open_yw7(MANUSCRIPT_SUFFIX, '.odt')


def get_partdesc(*args):
    '''Import pard descriptions from yWriter 6/7 to a Writer document
    with invisible chapter and scene markers. 
    '''
    open_yw7(PARTDESC_SUFFIX, '.odt')


def get_chapterdesc(*args):
    '''Import chapter descriptions from yWriter 6/7 to a Writer document
    with invisible chapter and scene markers. 
    '''
    open_yw7(CHAPTERDESC_SUFFIX, '.odt')


def get_scenedesc(*args):
    '''Import scene descriptions from yWriter 6/7 to a Writer document
    with invisible chapter and scene markers. 
    '''
    open_yw7(SCENEDESC_SUFFIX, '.odt')


def get_scenelist(*args):
    '''Import a scene list from yWriter 6/7 to a Writer document.
    '''
    open_yw7(SCENELIST_SUFFIX, '.csv')


def get_plotlist(*args):
    '''Import a plot list from yWriter 6/7 to a Writer document.
    '''
    open_yw7(PLOTLIST_SUFFIX, '.csv')


def get_charlist(*args):
    '''Import a plot list from yWriter 6/7 to a Writer document.
    '''
    open_yw7(CHARLIST_SUFFIX, '.csv')


def get_loclist(*args):
    '''Import a plot list from yWriter 6/7 to a Writer document.
    '''
    open_yw7(LOCLIST_SUFFIX, '.csv')


def get_itemlist(*args):
    '''Import an item list from yWriter 6/7 to a Writer document.
    '''
    open_yw7(ITEMLIST_SUFFIX, '.csv')


if __name__ == '__main__':
    try:
        sourcePath = sys.argv[1]
    except:
        sourcePath = ''

    fileName, FileExtension = os.path.splitext(sourcePath)

    if FileExtension in ['.yw5', '.yw6', '.yw7']:
        try:
            suffix = sys.argv[2]
        except:
            suffix = ''

        print(run(sourcePath, suffix))

    else:
        print('ERROR: File is not an yWriter project.')
