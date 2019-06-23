from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import subprocess
import SaveInfoToPickle

#运行前先启动mitmproxy代理：1、在anaconda的cmd中，先切换到文件所在的目录下； 2、启动mitmproxy命令: mitmdump -s UrlScraberInProxy.py
#UrlScraberInProxy.py为爬取视频url的python脚本

class Study163LessonBrowser(object):
    def __init__(self, chrome_cfg_path, chrome_exe_path, wait_time=20):
        chrome_start_cmd = "chrome.exe --remote-debugging-port=9222 --user-data-dir=%s --proxy-server=127.0.0.1:8080"%(chrome_cfg_path)
        self.browe_process = subprocess.Popen(chrome_start_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        time.sleep(3)

        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        self.browse = webdriver.Chrome(chrome_exe_path, chrome_options=chrome_options)
        self.wait = WebDriverWait(self.browse, wait_time)

        self.browse_info_list = []


    def browse_lesson(self, index):
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".m-chapterList .section")))
        lessons = self.browse.find_elements_by_css_selector(".m-chapterList .section")
        lesson = lessons[index]
        try:
            lesson_id = lesson.get_attribute("data-id")
            label = lesson.find_element_by_css_selector(".ksinfoicon-2")    #如果非视频文件，此处会抛出异常，从而跳过该课程浏览信息保存
            info = {
                "time" : time.time(),
                "lesson_id" : lesson_id
                }
            self.browse_info_list.append(info)
            lesson.click()
        except:
            print("ignore lesson %d"%(index))

    def browse_all_lessons(self, url, file_name=None):
        self.browse.get(url)
        try:
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".m-chapterList .section")))
            lessons = self.browse.find_elements_by_css_selector(".m-chapterList .section")
            total_len = len(lessons)
            for index in range(1, total_len):
                try:
                    self.browse_lesson(index)
                    time.sleep(6)
                except:
                    print("browsee lesson %d failed!!!"%(index))
        except:
            print("error ocurred when browse all lessons!!!")
        finally:
            if file_name:
                print("save browse infos")
                SaveInfoToPickle.save_info(file_name, self.browse_info_list)

            #访问通过特定的地址，用于通知代理脚本所有课程点击结束，保存相关信息
            self.browse.get(r"https://www.baidu.com")
            time.sleep(5)

            #完成后，释放资源
            self.browse.close()
            self.browe_process.terminate()

def main():
    chrome_cfg_path = r"D:\wsp\spider\chromeDbgCfg"
    chrome_exe_path = r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe"
    scraber = Study163LessonBrowser(chrome_cfg_path, chrome_exe_path)

    course_url = '''https://study.163.com/course/courseLearn.htm?courseId=1004569003#/learn/video?lessonId=1049050008&courseId=1004569003'''
    file_name = "browse_infos.pkl"
    scraber.browse_all_lessons(course_url, file_name)

if __name__ == "__main__":
    main()

