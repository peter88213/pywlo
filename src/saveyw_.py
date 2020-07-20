"""Convert html or csv to yWriter format. 

Input file format: html (with visible or invisible chapter and scene tags).

Version @release

Copyright (c) 2020 Peter Triesberger
For further information see https://github.com/peter88213/yw-cnv
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import sys
import os

from urllib.parse import unquote

from pywriter.html.html_proof import HtmlProof
from pywriter.html.html_manuscript import HtmlManuscript
from pywriter.html.html_scenedesc import HtmlSceneDesc
from pywriter.html.html_chapterdesc import HtmlChapterDesc
from pywriter.html.html_partdesc import HtmlPartDesc
from pywriter.html.html_characters import HtmlCharacters
from pywriter.html.html_locations import HtmlLocations
from pywriter.html.html_items import HtmlItems
from pywriter.csv.csv_scenelist import CsvSceneList
from pywriter.csv.csv_plotlist import CsvPlotList
from pywriter.csv.csv_charlist import CsvCharList
from pywriter.csv.csv_loclist import CsvLocList
from pywriter.csv.csv_itemlist import CsvItemList
from pywriter.html.html_import import HtmlImport
from pywriter.html.html_outline import HtmlOutline
from pywriter.yw.yw_file import YwFile
from pywriter.yw.yw_new_file import YwNewFile
from pywriter.html.html_fop import read_html_file

import uno
import unohelper

from uno_wrapper.uno_tools import *
from uno_wrapper.yw_cnv_uno import YwCnvUno

TAILS = [HtmlProof.SUFFIX + HtmlProof.EXTENSION,
         HtmlManuscript.SUFFIX + HtmlManuscript.EXTENSION,
         HtmlSceneDesc.SUFFIX + HtmlSceneDesc.EXTENSION,
         HtmlChapterDesc.SUFFIX + HtmlChapterDesc.EXTENSION,
         HtmlPartDesc.SUFFIX + HtmlPartDesc.EXTENSION,
         HtmlCharacters.SUFFIX + HtmlCharacters.EXTENSION,
         HtmlLocations.SUFFIX + HtmlLocations.EXTENSION,
         HtmlItems.SUFFIX + HtmlItems.EXTENSION,
         CsvSceneList.SUFFIX + CsvSceneList.EXTENSION,
         CsvPlotList.SUFFIX + CsvPlotList.EXTENSION,
         CsvCharList.SUFFIX + CsvCharList.EXTENSION,
         CsvLocList.SUFFIX + CsvLocList.EXTENSION,
         CsvItemList.SUFFIX + CsvItemList.EXTENSION,
         '.html']

YW_EXTENSIONS = ['.yw7', '.yw6', '.yw5']


def delete_tempfile(filePath):
    """If an Office file exists, delete the temporary file."""

    if filePath.endswith('.html'):

        if os.path.isfile(filePath.replace('.html', '.odt')):
            try:
                os.remove(filePath)
            except:
                pass

    elif filePath.endswith('.csv'):

        if os.path.isfile(filePath.replace('.csv', '.ods')):
            try:
                os.remove(filePath)
            except:
                pass


def run(sourcePath):
    sourcePath = unquote(sourcePath.replace('file:///', ''))

    ywPath = None

    for tail in TAILS:
        # Determine the document type

        if sourcePath.endswith(tail):

            for ywExtension in YW_EXTENSIONS:
                # Determine the yWriter project file path

                testPath = sourcePath.replace(tail, ywExtension)

                if os.path.isfile(testPath):
                    ywPath = testPath
                    break

            break

    if ywPath:

        if tail == '.html':
            return 'ERROR: yWriter project already exists.'

        elif tail == HtmlProof.SUFFIX + HtmlProof.EXTENSION:
            sourceDoc = HtmlProof(sourcePath)

        elif tail == HtmlManuscript.SUFFIX + HtmlManuscript.EXTENSION:
            sourceDoc = HtmlManuscript(sourcePath)

        elif tail == HtmlSceneDesc.SUFFIX + HtmlSceneDesc.EXTENSION:
            sourceDoc = HtmlSceneDesc(sourcePath)

        elif tail == HtmlChapterDesc.SUFFIX + HtmlChapterDesc.EXTENSION:
            sourceDoc = HtmlChapterDesc(sourcePath)

        elif tail == HtmlPartDesc.SUFFIX + HtmlPartDesc.EXTENSION:
            sourceDoc = HtmlPartDesc(sourcePath)

        elif tail == HtmlCharacters.SUFFIX + HtmlCharacters.EXTENSION:
            sourceDoc = HtmlCharacters(sourcePath)

        elif tail == HtmlLocations.SUFFIX + HtmlLocations.EXTENSION:
            sourceDoc = HtmlLocations(sourcePath)

        elif tail == HtmlItems.SUFFIX + HtmlItems.EXTENSION:
            sourceDoc = HtmlItems(sourcePath)

        elif tail == CsvSceneList.SUFFIX + CsvSceneList.EXTENSION:
            sourceDoc = CsvSceneList(sourcePath)

        elif tail == CsvPlotList.SUFFIX + CsvPlotList.EXTENSION:
            sourceDoc = CsvPlotList(sourcePath)

        elif tail == CsvCharList.SUFFIX + CsvCharList.EXTENSION:
            sourceDoc = CsvCharList(sourcePath)

        elif tail == CsvLocList.SUFFIX + CsvLocList.EXTENSION:
            sourceDoc = CsvLocList(sourcePath)

        elif tail == CsvItemList.SUFFIX + CsvItemList.EXTENSION:
            sourceDoc = CsvItemList(sourcePath)

        else:
            return 'ERROR: File format not supported.'

        ywFile = YwFile(ywPath)
        converter = YwCnvUno()
        message = converter.document_to_yw(sourceDoc, ywFile)

    elif sourcePath.endswith('.html'):
        result = read_html_file(sourcePath)

        if 'SUCCESS' in result[0]:

            if "<h3" in result[1].lower():
                sourceDoc = HtmlOutline(sourcePath)

            else:
                sourceDoc = HtmlImport(sourcePath)

        ywPath = sourcePath.replace('.html', '.yw7')
        ywFile = YwNewFile(ywPath)
        converter = YwCnvUno()
        message = converter.document_to_yw(sourceDoc, ywFile)

    else:
        message = 'ERROR: No yWriter project found.'

    if not message.startswith('ERROR'):
        delete_tempfile(sourcePath)

    return message


def export_yw(*args):
    '''Export the document to a yWriter 6/7 project.
    '''

    # Get document's filename

    document = XSCRIPTCONTEXT.getDocument().CurrentController.Frame
    # document   = ThisComponent.CurrentController.Frame

    ctx = XSCRIPTCONTEXT.getComponentContext()
    smgr = ctx.getServiceManager()
    dispatcher = smgr.createInstanceWithContext(
        "com.sun.star.frame.DispatchHelper", ctx)
    # dispatcher = createUnoService("com.sun.star.frame.DispatchHelper")

    documentPath = XSCRIPTCONTEXT.getDocument().getURL()
    # documentPath = ThisComponent.getURL()

    from com.sun.star.beans import PropertyValue
    args1 = []
    args1.append(PropertyValue())
    args1.append(PropertyValue())
    # dim args1(1) as new com.sun.star.beans.PropertyValue

    if documentPath.endswith('.odt') or documentPath.endswith('.html'):
        odtPath = documentPath.replace('.html', '.odt')
        htmlPath = documentPath.replace('.odt', '.html')

        # Save document in HTML format

        args1[0].Name = 'URL'
        # args1(0).Name = "URL"
        args1[0].Value = htmlPath
        # args1(0).Value = htmlPath
        args1[1].Name = 'FilterName'
        # args1(1).Name = "FilterName"
        args1[1].Value = 'HTML (StarWriter)'
        # args1(1).Value = "HTML (StarWriter)"
        dispatcher.executeDispatch(document, ".uno:SaveAs", "", 0, args1)
        # dispatcher.executeDispatch(document, ".uno:SaveAs", "", 0, args1())

        # Save document in OpenDocument format

        args1[0].Value = odtPath
        # args1(0).Value = odtPath
        args1[1].Value = 'writer8'
        # args1(1).Value = "writer8"
        dispatcher.executeDispatch(document, ".uno:SaveAs", "", 0, args1)
        # dispatcher.executeDispatch(document, ".uno:SaveAs", "", 0, args1())

        result = run(htmlPath)

    elif documentPath.endswith('.ods') or documentPath.endswith('.csv'):
        odsPath = documentPath.replace('.csv', '.ods')
        csvPath = documentPath.replace('.ods', '.csv')

        # Save document in csv format

        args1[0].Name = 'URL'
        # args1(0).Name = "URL"
        args1[0].Value = csvPath
        # args1(0).Value = csvPath
        args1[1].Name = 'FilterName'
        # args1(1).Name = "FilterName"
        args1[1].Value = 'Text - txt - csv (StarCalc)'
        # args1(1).Value = "Text - txt - csv (StarCalc)"
        dispatcher.executeDispatch(document, ".uno:SaveAs", "", 0, args1)
        # dispatcher.executeDispatch(document, ".uno:SaveAs", "", 0, args1())

        # Save document in OpenDocument format

        args1.append(PropertyValue())

        args1[0].Value = odsPath
        # args1(0).Value = odsPath
        args1[1].Value = 'calc8'
        # args1(1).Value = "calc8"
        args1[2].Name = "FilterOptions"
        # args1(2).Name = "FilterOptions"
        args1[2].Value = "124,34,76,1,,0,false,true,true"
        # args1(2).Value = "124,34,76,1,,0,false,true,true"
        dispatcher.executeDispatch(document, ".uno:SaveAs", "", 0, args1)
        # dispatcher.executeDispatch(document, ".uno:SaveAs", "", 0, args1())

        result = run(csvPath)

    else:
        result = "ERROR: File type not supported."

    if result.startswith('ERROR'):
        msgType = 'errorbox'

    else:
        msgType = 'infobox'

    msgbox(result, 'Export to yWriter', type_msg=msgType)


if __name__ == '__main__':
    try:
        sourcePath = sys.argv[1]
    except:
        sourcePath = ''
    print(run(sourcePath))
