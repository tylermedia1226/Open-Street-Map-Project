
# coding: utf-8

# In[ ]:

#Counting top level tags in the full San Diego OSM file
import xml.etree.cElementTree as ET
import pprint

filename = 'san-diego_california.osm'

def count_tags(filename):
    tag_dict = {}
    for event, elem in ET.iterparse(filename):
        if elem.tag not in tag_dict.keys():
            tag_dict[elem.tag] = 1
        else:
            tag_dict[elem.tag] += 1
    return tag_dict
    
x = count_tags(filename)

pprint.pprint(x)


# In[ ]:


#Count all tag 'k' values that fall into the lower, lower_colon and problem character categries.
import xml.etree.cElementTree as ET
import pprint
import re

filename = 'san-diego_california.osm'

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

def key_type(element, keys):
    if element.tag == "tag":
        valueOfAttribute = element.attrib['k']
        if re.search(lower, valueOfAttribute):
            keys["lower"] += 1
        elif re.search(lower_colon, valueOfAttribute):
            keys["lower_colon"] += 1
        elif re.search(problemchars, valueOfAttribute):
            keys["problemchars"] += 1
        else:
            keys["other"] += 1
        pass
        
    return keys



def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys

y = process_map(filename)


pprint.pprint(y)


# In[ ]:

#Creating a smaller sample of OSM data to audit and clean

import xml.etree.ElementTree as ET 

OSM_FILE = 'san-diego_california.osm' 
SAMPLE_FILE = "sample_SD_2.osm"

k = 2 # Parameter: take every k-th top level element

def get_element(osm_file, tags=('node', 'way', 'relation')):

    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


with open(SAMPLE_FILE, 'wb') as output:
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write('<osm>\n  ')

    # Write every kth top level element
    for i, element in enumerate(get_element(OSM_FILE)):
        if i % k == 0:
            output.write(ET.tostring(element, encoding='utf-8'))

    output.write('</osm>')


# In[ ]:

#Secondary attributes for Node element
def extract_secondary_attribs(osmfile, tagtype):
    osm_file = open(osmfile, "r")
    secondary_attribs = set() 
    for i, element in enumerate(get_element(osm_file)):
        if element.tag == tagtype:                         
            for tag in element.iter("tag"):
                for tkey, tvalue in tag.attrib.iteritems():
                    secondary_attribs.add((tkey,tvalue))
    return secondary_attribs

node_secondary_attribs = extract_secondary_attribs("sample_SD_2.osm", "node")

#found this good (aka readable) print functions in the Udacity forums
def print_secondary_attribs(stuff):
    for ind in stuff:
        if ind[0] == 'k':
            print 'Attributes - Key: ', ind[0], ' Value: ', ind[1]

    for ind in stuff:
        if ind[0] == 'v':
            print 'Attributes - Key: ', ind[0], ' Value: ', ind[1]
                
x = print_secondary_attribs(node_secondary_attribs)


# In[ ]:

#Secondary attributes for Way element
def extract_secondary_attribs(osmfile, tagtype):
    osm_file = open(osmfile, "r")
    secondary_attribs = set()  
    for i, element in enumerate(get_element(osm_file)):
        if element.tag == tagtype:                         
            for tag in element.iter("tag"):
                for tkey, tvalue in tag.attrib.iteritems():
                    secondary_attribs.add((tkey,tvalue))
    return secondary_attribs

way_secondary_attribs = extract_secondary_attribs("sample_SD_2.osm", "way")


def print_secondary_attribs(stuff):
    for ind in stuff:
        if ind[0] == 'k':
            print 'Attributes - Key: ', ind[0], ' Value: ', ind[1]

    for ind in stuff:
        if ind[0] == 'v':
            print 'Attributes - Key: ', ind[0], ' Value: ', ind[1]
                
y = print_secondary_attribs(way_secondary_attribs)


# In[ ]:

'''Function creates dictionary for the node tags with a set 'k' attributes and a set 'v' 
values for the associated 'k' attribute.
''''
def tm_unique_k_and_v(osmfile, tagtype):
    osm_file = open(osmfile, "r")
    unique_k_and_v = defaultdict(set)
    for i, element in enumerate(get_element(osm_file)):
        if element.tag == tagtype:                         
            for tag in element.iter("tag"):        
                unique_k_and_v[tag.attrib['k']].add(tag.attrib['v'])    
    return unique_k_and_v

print "Unique 'k' and 'v' values for node element"
tm_unique_k_and_v("sample_SD_2.osm", "node")


# In[ ]:

'''Function creates dictionary for the way tags with a set 'k' attributes and a set 'v' 
values for the associated 'k' attribute.
''''
def tm_unique_k_and_v(osmfile, tagtype):
    osm_file = open(osmfile, "r")
    unique_k_and_v = defaultdict(set)
    for i, element in enumerate(get_element(osm_file)):
        if element.tag == tagtype:                         
            for tag in element.iter("tag"):        
                unique_k_and_v[tag.attrib['k']].add(tag.attrib['v'])    
    return unique_k_and_v

print "Unique 'k' and 'v' values for way element"
tm_unique_k_and_v("sample_SD_2.osm", "way")


# In[ ]:

#Auditing phone number types
def all_phone(osmfile):
    osm_file = open(osmfile, "r")
    unique_phone = set()
    for event, element in ET.iterparse(osmfile):
        if element.tag == 'way':
             for tag in element.iter("tag"):
                if tag.attrib['k'] == "phone":
                    unique_phone.add(tag.attrib['v'])
    print len(unique_phone)  
    print "--------------------"
    return unique_phone

all_phone('san-diego_california.osm')


# In[ ]:

#clean phone numbers
def clean_phone_nums(phone_number):
    num = re.sub('[^0-9]','', phone_number)
    if num[0] == '1':
        cleaned_number = num[1:4] + " " + num[4:7] + " " + num[7:11]
    else:
        cleaned_number = num[0:3] + " " + num[3:6] + " " + num[6:10]
    return cleaned_number


# In[ ]:

#Auditing Zipcodes
def post_codes(osmfile):
    osm_file = open(osmfile, "r")
    post_cd = set()
    for event, element in ET.iterparse(osmfile):
        if element.tag == 'node' or element.tag == 'way':
             for tag in element.iter("tag"):
                if tag.attrib['k'] == "addr:postcode":
                    post_cd.add(tag.attrib['v'])
    return post_cd

s = post_codes('san-diego_california.osm') 
print len(s)
print "----------------"
pprint.pprint(s)


# In[ ]:

#Cleaning Zipcodes
def clean_zipcode(zip_code):
    if re.search(r'^\d{5}', zip_code):
        new_zip = re.search(r'^\d{5}', zip_code).group()
    elif re.search(r'\d{5}$', zip_code):
        new_zip = re.search(r'\d{5}$', zip_code).group()
    else:
        new_zip = '92131'
    return new_zip


# In[ ]:

#Auditing Cuisine Types
def all_cuisines(osmfile):
    osm_file = open(osmfile, "r")
    unique_cuisines = set()
    for event, element in ET.iterparse(osmfile):
        if element.tag == "node" or element.tag == "way":
            for tag in element.iter("tag"):
                if tag.attrib['k'] == "cuisine":
                    unique_cuisines.add(tag.attrib['v']) 
    return unique_cuisines


t = all_cuisines('san-diego_california.osm') 
print "Cuisine types"
print len(t)
print "----------------"
pprint.pprint(t)


# In[ ]:

#Auditing Denomination Types
def all_denominations(osmfile):
    osm_file = open(osmfile, "r")
    denominations = set()
    for event, element in ET.iterparse(osmfile):
        if element.tag == "node" or element.tag == "way":
            for tag in element.iter("tag"):
                if tag.attrib['k'] == "denomination":
                    denominations.add(tag.attrib['v'])
    return denominations

y = all_denominations('san-diego_california.osm')
print "Denomination types"
print len(y)
print "----------------"
pprint.pprint(y)


# In[ ]:

#Cleaning Cuisines and Denominations
#clean cuisine
def clean_cuisine(cuisine):
    new_cuisine = re.search(r'\b\w+', cuisine)
    cuisine = new_cuisine.group()
    return cuisine.lower()

#clean denomination
def clean_denomination(denomination):
    return denomination.lower()


# In[ ]:

#Auditing Street Types (as taken from OSM Case Study)
osm_file = open("san-diego_california.osm", "r")

street_type_re = re.compile(r'\S+\.?$', re.IGNORECASE)
street_types = defaultdict(int)

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        street_types[street_type] += 1

def print_sorted_dict(d):
    keys = d.keys()
    keys = sorted(keys, key=lambda s: s.lower())
    for k in keys:
        v = d[k]
        print "%s: %d" % (k, v) 

def is_street_name(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "addr:street")

def audit():
    for event, elem in ET.iterparse(osm_file):
        if is_street_name(elem):
            audit_street_type(street_types, elem.attrib['v'])    
    pprint.pprint(dict(street_types))   

if __name__ == '__main__':
    audit()


# In[ ]:

#Updating Street Types
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

