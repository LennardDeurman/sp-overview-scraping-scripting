import urllib2
import uuid
import math
import os
import json
import time 

CONTENTS_DIR = "contents"
DETAILS_DIR = "details"
CURRENT_DIR = "current"
ADAPTER_NAME = "commerzbank"
URL = "{0}/EmcWebApi/api/ProductSearch/Search?PageSize={1}&PageNum={2}"
PAGE_SIZE = 100

NL = "NL"
FR = "FR"
PT = "PT"
BE = "BE"

BASE_URLS = {
    NL: "https://www.beurs.commerzbank.com",
    FR: "https://www.bourse.commerzbank.com",
    PT: "https://www.warrants.commerzbank.pt",
    BE: "https://www.beurs.commerzbank.be"
}



def load_contents(url):
    response = urllib2.urlopen(url)
    contents = response.read()
    return contents

def get_overview_url(base_url, page_size, page_num):
    return URL.format(base_url, page_size, page_num)

def save_file(path, contents):
    with open(path, 'w') as file:
        file.write(contents)

def save_overview(path, page, contents):
    save_file("{0}/{1}".format(path, "Page{0}.txt".format(page)), contents)

def fetch_content(language_code, path):
    base_url = BASE_URLS[language_code]
    base_content = load_contents(get_overview_url(base_url, PAGE_SIZE, 1))
    dictionary = json.loads(base_content)
    total_count = dictionary["TotalCount"]
    pages = int(math.ceil(int(total_count) / PAGE_SIZE))
    print("There are {0} pages".format(pages))
    save_overview(path, 1, base_content)
    time.sleep(4)
    for page in range(1, pages):
        contents = load_contents(get_overview_url(base_url, PAGE_SIZE, page + 1))
        time.sleep(4)
        save_overview(path, page + 1, contents)

def init_program():
    temp_directory_name = str(uuid.uuid4())
    full_dir = "{0}/{1}".format(CONTENTS_DIR, ADAPTER_NAME)
    if not os.path.exists(CONTENTS_DIR):
        os.mkdir(CONTENTS_DIR)
    if not os.path.exists(full_dir):
        os.mkdir(full_dir)
    path = "{0}/{1}".format(full_dir, temp_directory_name)
    nl_path = "{0}/{1}".format(path, NL)
    fr_path = "{0}/{1}".format(path, FR)
    be_path = "{0}/{1}".format(path, BE)
    pt_path = "{0}/{1}".format(path, PT)
    os.mkdir(path)
    os.mkdir(nl_path)
    os.mkdir(fr_path)
    os.mkdir(be_path)
    os.mkdir(pt_path)
    fetch_content(NL, nl_path)
    fetch_content(FR, fr_path)
    fetch_content(BE, be_path)
    fetch_content(PT, pt_path)
    new_path = "{0}/{1}".format(full_dir, CURRENT_DIR)
    os.remove(new_path)
    os.rename(path, new_path)
    
def load_details(path):
    nl_path = "{0}/{1}".format(path, NL)
    fr_path = "{0}/{1}".format(path, FR)
    be_path = "{0}/{1}".format(path, BE)
    pt_path = "{0}/{1}".format(path, PT)
    #load_details_by_lan(nl_path, BASE_URLS[NL])
    #load_details_by_lan(fr_path, BASE_URLS[FR])
    load_details_by_lan(be_path, BASE_URLS[PT])
    load_details_by_lan(pt_path, BASE_URLS[BE])

def read_from_file(full_filename, base_url, path):
    try:
        print("Reading file {0}".format(full_filename))
        f = open(full_filename, "r")
        text = f.read()    
        contents = json.loads(text)
        ids = [x["Id"] for x in contents["Products"]] 
        print("Found {0} ids".format(len(ids)))
        for id in ids:
            print("Loading for id: {0}".format(id))
            html = load_contents("{0}/webforms/Products/ProductDetailsData.aspx?p={1}&pc=3&dm=TabPanel&c=0".format(base_url, id))
            save_file("{0}/{1}/{2}.html".format(path, DETAILS_DIR, id), html)
            time.sleep(1)
    except:
        pass

def load_details_by_lan(path, base_url):
    full_filenames = map(lambda x: "{0}/{1}".format(path, x), os.listdir(path))
    details_path = "{0}/{1}".format(path, DETAILS_DIR)
    if not os.path.exists(details_path):
        os.mkdir(details_path)
    for full_filename in full_filenames:
        read_from_file(full_filename, base_url, path)

load_details(r"C:\Users\Lenna\DribbaBV\contents\8af8ae3e-c26e-428a-bc3e-e8c866904b84");