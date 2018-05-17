import xml.etree.ElementTree as ET
import os

tree = ET.parse('template.gmx')
root = tree.getroot()


a = os.system('bash image_size.sh -w 2_0.png')
print("w is ",a)

'''
for e in root.iter('year'):
    new_year = int(e.text)* 23423
    e.text = str(new_year)
    e.set("cahcahcha", "34")

tree.write('out.xml')
'''
