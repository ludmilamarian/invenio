#from invenio.flaskshell import *
import os
from invenio.legacy.bibrecord import create_records
#from invenio.legacy.bibupload import bibupload
from invenio.legacy.bibrecord import record_xml_output
imageFolder = '/home/michael/aerial'
outputPath = '/home/michael/Test pylire/image-set-ready-air.xml'
xml=''
for path, dirs, fs in os.walk(imageFolder):
    for f in fs:
        if 'muon17' not in f and 'icon' not in f:
            print f
            filename = path+os.sep+f
            xml = xml+"<record>  <datafield tag=\"963\" ind1=\" \" ind2=\" \"><subfield code=\"a\">PUBLIC</subfield></datafield><datafield tag=\"980\" ind1=\" \" ind2=\" \"><subfield code=\"a\">Pictures</subfield></datafield><datafield tag=\"FFT\" ind1=\" \" ind2=\" \"><subfield code=\"a\">"+filename+"</subfield><subfield code=\"x\">"+"%s_icon.JPG" %filename[:-4]+"</subfield></datafield></record>"
    f = open(outputPath, 'w')
    f.write(xml)
    f.close()
    #records = create_records(xml)

# for record in records:
# new_marcxml = record_xml_output(records)
# f = open('/home/michael/Test pylire/image-set-ready.xml', 'w')
# f.write(new_marcxml)
# f.close()
# for record in records:
#     print record
#     bibupload(record[0],opt_mode='insert')
