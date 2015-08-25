# 
# Script to check package file listing against expected BOM inventory
#
import xlrd
import os.path
import sys
rootdir = "../../out"
inventory_file = "files.txt"
#----------------------------------------------------------------------
# read Excel BOM file list as 'expected' BOM
def read_excel(path):
    """
    Open and read an Excel file
    """
    sheets = ["corelibs", "arduino-tools", "toolchains"]
    bom = []
    book = xlrd.open_workbook(path)
 
    # read sheets
    for sheet in sheets:
        bom_sheet = book.sheet_by_name(sheet) 
        # read first column
        col = bom_sheet.col_values(0)
        col.pop(0) # exclude header row
        bom += col
 
    return bom
#----------------------------------------------------------------------
# read zip file inventory as 'actual' BOM
def list_files():
    bom = []
    f = open(inventory_file, 'r')
    for line in f:
        bom.append(line.strip())

    return bom
#----------------------------------------------------------------------

if __name__ == "__main__":
    path = "BOM.xlsx"
    expected = read_excel(path)
    actual = list_files()
    actual.sort()
    expected.sort()
    missing = list(set(expected) - set(actual))
    extra = list(set(actual) - set(expected))

    print "Expected files: %d\nActual files:   %d" % (len(expected), len(actual))
    print '----------------- MISSING ---------------------'
    for i in missing:
        print i
    print '-------------- EXTRA/ORPHANED -----------------'
    for i in extra:
        print i
    print '-----------------------------------------------'
    print "Missing: %d\nExtra:   %s" % (len(missing), len(extra))
    if len(missing) > 0:
        print "**** BOM Check - FAIL ****"
        sys.exit(1)

    print "**** BOM Check - PASS ****"
