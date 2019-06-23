import mitmproxy.addonmanager
import mitmproxy.http
import mitmproxy.proxy.protocol
import re
import pickle
import time
from mitmproxy import ctx
import SaveInfoToPickle

URL_START_STR = r"https://vodm0pihssv.vod.126.net/edu-video/nos/mp4"
URL_RE_PATTEN = r"https://vodm0pihssv.vod.126.net/edu-video/nos/mp4(.*).mp4*"

SAVE_TRIGER_URL = r"https://www.baidu.com"

URL_INFO_SAVE_FILE = "url_infos.pkl"
 
class UrlScraber:
    def __init__(self):
        self.save_status = False
        self.url_info_list = []
        self.re_url = re.compile(URL_RE_PATTEN, re.M)
        ctx.log.info("initial Url Scraber......")
 
    def request(self, flow: mitmproxy.http.HTTPFlow):
        """
        HTTP response headers were successfully read. At this point, the body
        is empty.
        """
        url = flow.request.url
        if(url.startswith(URL_START_STR)):
            url_patten = self.re_url.search(url)
            if url_patten:
                info = {
                    "time" : time.time(),
                    "file_url" : url
                    }
                self.url_info_list.append(info)
                self.save_status = True
                ctx.log.info("!!!!!!!!!!!!!!!!!!get matched url: " + url)
        elif url.startswith(SAVE_TRIGER_URL):
            if self.save_status:
                SaveInfoToPickle.save_info(URL_INFO_SAVE_FILE, self.url_info_list)
                print("url infos saved!!!!!!")
                self.save_status = False
     
addons = [
    UrlScraber()
]

