# xlrd usage, see: http://scienceoss.com/read-excel-files-from-python/
import xlrd

# Open the XLS file as a "workbook" and select the first sheet as our source.
# We'll get our tag names from the sheet's first row contents.
wb = xlrd.open_workbook("essai.xlsx")
sh = wb.sheet_by_index(0)
tags = [n.replace(" ", "").lower() for n in sh.row_values(0)]

# This is going to come out as a string, which will write to a file in the end.
result = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<myItems>\n"

# Now, we'll just create a string that looks like an XML node for each row
# in the sheet. Of course, a lot of things will depend on the prescribed XML
# format but since we have no idea what it is, we'll just do this:
for row in range(1, sh.nrows):
    result += "  <item>\n"
    for i in range(len(tags)):
        tag = tags[i].encode("utf-8")
        val = sh.row_values(row)[i].encode("utf-8")
        result += "    <%s>%s</%s>\n" % (tag, val, tag)
        print result
    result += "  </item>\n"

# Close our pseudo-XML string.
result += "</myItems>"

# Write the result string to a file using the standard I/O.
f = open("myfile.xml", "w")
f.write(result)
f.close()