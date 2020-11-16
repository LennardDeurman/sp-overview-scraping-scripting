import urllib2
import uuid
import time
import mysql.connector
from pyquery import PyQuery as pq




class HTTPLoader:

    COOKIE = "Cookie"
    FILE_NAME = "{0}.html"

    def __init__(self, url, cookie = "", file_name = None):
        self.url = url
        self.cookie = cookie
        self.contents = None
        self.uuid = str(uuid.uuid4())
        self.file_name = file_name if file_name is not None else self.uuid

    def load_contents(self):
        opener = urllib2.build_opener()
        opener.addheaders.append((HTTPLoader.COOKIE, self.cookie))
        f = opener.open(self.url)
        self.contents = f.read()
        return self.contents

    def save_file(self):
        if (self.contents):    
            with open(HTTPLoader.FILE_NAME.format(self.file_name), 'w') as file:
                file.write(self.contents)
    
class INGHTTPLoader (HTTPLoader):

    ING_COOKIE = "cookiepref=true; AcceptedDisclaimer=939393; SelectedProfile=Professional; SelectedJurisdiction=The Netherlands"

    def __init__(self, url, file_name = None):
        HTTPLoader.__init__(self, url, INGHTTPLoader.ING_COOKIE, file_name)

class BNPHTTPLoader (HTTPLoader):

    BNP_COOKIE = "LegalTermsAccepted=True; LegalTermsAcceptedDate='2019-03-29T17:46:07.2975786+01:00';"

    def __init__(self, url, file_name = None):
        HTTPLoader.__init__(self, url, BNPHTTPLoader.BNP_COOKIE, file_name)

class KempenHTTPLoader (HTTPLoader):

    KEMPEN_COOKIE = "ecm=user_id=0&isMembershipUser=0&site_id=&username=&new_site=/&unique_id=0&site_preview=0&langvalue=0&DefaultLanguage=1043&NavLanguage=1043&LastValidLanguageID=1043&DefaultCurrency=840&SiteCurrency=840&ContType=&UserCulture=1033&dm=www.kempenmarkets.nl&SiteLanguage=1043; SelectedCulture=nl-nl; acceptDisclaimer_nl_v5=04/21/2019 01:05:06;"

    def __init__(self, url, file_name = None):
        HTTPLoader.__init__(self, url, KempenHTTPLoader.KEMPEN_COOKIE, file_name)


def get_kempen_detail_links():
    loader = KempenHTTPLoader("https://www.kempenmarkets.nl/gestructureerde-producten/", "kempen-overview")
    loader.load_contents()
    loader.save_file()
    dom = pq(loader.contents)
    kempen_links = map(lambda x: "https://www.kempenmarkets.nl{0}".format(pq(x).attr["href"]), dom("#table-placements tr td:nth-child(2) a"))
    return kempen_links

def get_bnp_detail_links():
    bnp_details_urls = []
    bnp_overview_urls = [
        {
            "url": "https://www.bnpparibasmarkets.nl/producten/?cat=Memory%20Coupon%20Notes",
            "name": "bnp-overview-memory-coupon-notes"
        },
        {
            "url": "https://www.bnpparibasmarkets.nl/producten/?cat=Klik+%26+Klaar+Notes",
            "name": "bnp-overview-klik-klaar-notes"
        },
        {
            "url": "https://www.bnpparibasmarkets.nl/producten/?cat=Rendement+Certificaten",
            "name": "bnp-overview-rendement-certificaten"
        },
        {
            "url": "https://www.bnpparibasmarkets.nl/producten/?cat=Garantie+Notes",
            "name": "bnp-overview-garantie-notes"
        },
        {
            "url": "https://www.bnpparibasmarkets.nl/producten/?cat=Certificates",
            "name": "bnp-overview-certificates"
        }
    ]

    urls = []
    while (len(bnp_overview_urls) > 0):
        item = bnp_overview_urls[0]
        url = item["url"]
        time.sleep(1)
        loader = BNPHTTPLoader(url, item["name"])
        loader.load_contents()
        loader.save_file()
        dom = pq(loader.contents)
        bnp_details_links = map(lambda x: "https://www.bnpparibasmarkets.nl{0}".format(pq(x).attr["href"]), dom(".table-container table tr td:nth-child(2) a"))
        bnp_details_urls += bnp_details_links
        bnp_next_links = map(lambda x: "https://www.bnpparibasmarkets.nl{0}".format(pq(x).attr["href"]), dom(".trailer a.button--ghost:not(.is-active):not(.button--icon-only)"))
        for i in range(0, len(bnp_next_links)):
            next_url = bnp_next_links[i]
            if not next_url in urls:
                urls.append(next_url)
                name = "{0}-{1}".format(item["name"], str(i + 2))
                bnp_overview_urls.append({
                    "url": next_url,
                    "name": name
                })
        bnp_overview_urls.pop(0)
    return bnp_details_urls


mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="Swaps@005",
    database="tradingdb"
)
cursor = mydb.cursor(dictionary=True)
cursor.execute("SELECT isin, isin_url FROM seperated_isins LEFT JOIN domains ON seperated_isins.domain_id = domains.domain_id")
results = cursor.fetchall()
all_urls = []
for res in results:
    all_urls.append(res["isin_url"].format(res["isin"]))

all_urls += get_bnp_detail_links() + get_kempen_detail_links()
cursor.close()
mydb.close()

print(len(all_urls))
print(all_urls)

