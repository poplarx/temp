__author__ = 'poplarx'

import gzip
import requests
import json
from libs.fds_tools import *
from diff_format.diff1_profile import diff1_object,diff1_profile


def extract_gzstr_2_str(gz_data):
    import cStringIO as StringIO
    import gzip

    fileobj = StringIO.StringIO(gz_data)
    gzf = gzip.GzipFile(mode="rb",fileobj=fileobj)
    str_data = gzf.read()
    gzf.close()

    return str_data

#request from origin url
route_id = 1596949
url = "http://ir-d2.mi-ae.com.cn/routes/%d/show/gps.diff1.gz" % route_id
r1 = requests.get(url)

#request from the new url got from the origin one
url_new = r1.content
r = requests.get(url_new)

#extract diff data from gz file
str_data = extract_gzstr_2_str(r.content)

#parse the diff file
diff_obj = diff1_object.Diff1Object()
diff_obj.parse_from_string(str_data)

#generate path in format that json_post needs
path = []
for p in diff_obj._points:
    path_row = {}
    path_row['lat'] = p['latitude']
    path_row['long'] = p['longitude']
    path_row['value'] = p['distance'] / p['record_time']
    path.append(path_row)

file_obj = open("../post_body/path_json_v1.json",'r')
json_post = json.loads(file_obj.read())
json_post['path'] = path


#remove the temp pictures generated
print 'test', 'pathmap/heatline :  compact=gz'
remove_test_file('pathmap/heatline/test')

#call API and generate heatline images.
base_url = 'http://jietu.iriding.cc/pathmap/heatline/test/urls?size=320*320,640*640&compact=%s&site=xiaomi'
url_post = base_url % 'gz'
post_body = compact_json_2_gz(json_post)
files = {'file': ('path.json.gz',post_body)}

r_new = requests.post(url_post, files=files)

#print the image urls
print r_new.text
