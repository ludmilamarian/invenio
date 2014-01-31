import os
from invenio.websubmit_icon_creator import build_icon
for x in os.listdir('.'):
    if x.find('icon') < 0:
        build_icon('/home/michael/aerial', x, 'JPG', "%s_icon.JPG" %x[:-4], 'JPG', False, 100, '300' )



#./bibsched
