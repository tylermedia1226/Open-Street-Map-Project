
# coding: utf-8

# In[ ]:

import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET

import cerberus

import schema

OSM_PATH = "san-diego_california.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way element
    
    if element.tag == 'node':
        for node in NODE_FIELDS:
            node_attribs[node] = element.attrib[node]
        for child in element:
            data = {}
            if child.tag == 'tag':
#My cleaning functions for node elements
                if child.attrib['k'] == 'phone' or child.attrib['k'] == 'contact:phone':
                    data['value'] = clean_phone_nums(child.attrib['v'])
                elif child.attrib['k'] == 'cuisine':
                    data['value'] = clean_cuisine(child.attrib['v'])
                elif child.attrib['k'] == "addr:postcode":
                    data['value'] = clean_zipcode(child.attrib['v'])
                elif child.attrib['k'] == "denomination":
                    data['value'] = clean_denomination(child.attrib['v'])
                elif child.attrib['k'] == "addr:street":
                    data['value'] = update_street_type(child.attrib['v'], mapping)
                
                else:
                    data['value'] = child.attrib['v']
                if PROBLEMCHARS.search(child.attrib['k']):
                    continue
                elif LOWER_COLON.search(child.attrib['k']):
                    split = child.attrib['k'].split(':',1)
                    data['key'] = split[1]
                    data['type'] = split[0]
                else:
                    data['key'] = child.attrib['k']
                    data['type'] = 'regular'
                
                data['id'] = element.attrib['id']
                
                
                tags.append(data)
        
        return {'node': node_attribs, 'node_tags': tags}
    
    elif element.tag == 'way':
        for way in WAY_FIELDS:
            way_attribs[way] = element.attrib[way]
        position = 0
        for child in element:
            data = {}
            ways = {}
            if child.tag == 'tag':
#My cleaning functions for way elements                
                if child.attrib['k'] == 'phone':
                    data['value'] = clean_phone_nums(child.attrib['v'])
                elif child.attrib['k'] == 'cuisine':
                    data['value'] = clean_cuisine(child.attrib['v'])
                elif child.attrib['k'] == "addr:postcode" or child.attrib['k'] == 'post_code':
                    data['value'] = clean_zipcode(child.attrib['v'])
                elif child.attrib['k'] == "denomination":
                    data['value'] = clean_denomination(child.attrib['v'])
                elif child.attrib['k'] == "addr:street":
                    data['value'] = update_street_type(child.attrib['v'],mapping)
                
                else: 
                    data['value'] = child.attrib['v']
                if PROBLEMCHARS.search(child.attrib['k']):
                    continue
                elif LOWER_COLON.search(child.attrib['k']):
                    split = child.attrib['k'].split(':',1)
                    data['key'] = split[1]
                    data['type'] = split[0]
                else:
                    data['key'] = child.attrib['k']
                    data['type'] = 'regular'
                
                data['id'] = element.attrib['id']
                
                tags.append(data)
            
            if child.tag == 'nd':
                data_ways = {}
                data_ways['id'] = element.attrib['id']
                data_ways['node_id'] = child.attrib['ref']
                data_ways['position'] = position 
                position += 1
                way_nodes.append(data_ways)
                
            
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))

#My cleaning functions
def clean_phone_nums(phone_number):
    num = re.sub('[^0-9]','', phone_number)
    if num[0] == '1':
        cleaned_number = num[1:4] + " " + num[4:7] + " " + num[7:11]
    else:
        cleaned_number = num[0:3] + " " + num[3:6] + " " + num[6:10]
    return cleaned_number

def clean_zipcode(zip_code):
    if re.search(r'^\d{5}', zip_code):
        new_zip = re.search(r'^\d{5}', zip_code).group()
    elif re.search(r'\d{5}$', zip_code):
        new_zip = re.search(r'\d{5}$', zip_code).group()
    else:
        new_zip = '92131'
    return new_zip

def clean_cuisine(cuisine):
    new_cuisine = re.search(r'\b\w+', cuisine)
    cuisine = new_cuisine.group()
    return cuisine.lower()

def clean_denomination(denomination):
    return denomination.lower()

street_type_re = re.compile(r'\S+\.?$', re.IGNORECASE)

mapping = { "St": "Street",
            "St.": "Street",
            "street": "Street",
            "Ave": "Avenue",
            "Ave.": "Avenue",
            "Av": "Avenue",
            "Rd": "Road",
            "Rd.": "Road",
            "Bl": "Boulevard",
            "Blvd": "Boulevard",
            "Ct": "Court",
            "Ctr": "Court",
            "Dr": "Drive",
            "Ln": "Lane",
            "Loreta": "Loretta",
            "Pk": "Parkway",
            "Pkwy": "Parkway"
            }

def update_street_type(street_name, mapping):
    m = street_type_re.search(street_name)
    if m.group() in mapping.keys():
        street_name = re.sub(m.group(), mapping[m.group()], street_name)
    return street_name


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file,          codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file,          codecs.open(WAYS_PATH, 'w') as ways_file,          codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file,          codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=True)

