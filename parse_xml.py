import xml.etree.ElementTree as ET
tree = ET.parse('template.gmx')
root = tree.getroot()
for t in root:
    print (t)
