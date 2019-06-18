from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from pyquery import PyQuery as pq
import subprocess
import time
import SaveInfoToPickle

class Study163LessonInfoScraber(object):
    def __init__(self, chrome_cfg_path, chrome_exe_path, wait_time=20):
        chrome_start_cmd = r"chrome.exe --remote-debugging-port=9222 --user-data-dir=" + chrome_cfg_path
        self.browe_process = subprocess.Popen(chrome_start_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        time.sleep(3)
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        self.browse = webdriver.Chrome(chrome_exe_path, chrome_options=chrome_options)
        self.wait = WebDriverWait(self.browse, wait_time)

    def init_chapte_lesson_infos(self):
        self.chapter_number = ""
        self.chapter_name = ""
        self.chapter_info_list = []
        self.lesson_info_list = []

    def add_chapter_to_list(self):
        if len(self.lesson_info_list) > 0:
            lesson_in_chapter = self.lesson_info_list[:]
            chapter_info = {
                "chapter_name" : "第%s章 "%(self.chapter_number) + self.chapter_name,
                "lesson_list" : lesson_in_chapter
                }
            self.chapter_info_list.append(chapter_info)

    def get_lesson_infos_in_course(self, course_url):
        self.browse.get(course_url)
        try:
            self.init_chapte_lesson_infos()
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".m-chapterList div")))
            doc = pq(self.browse.page_source)
            item_list = doc(".m-chapterList div")
            for item in item_list.items():
                chapter_item = item(".chapter")
                lesson_item = item(".section")
                if chapter_item:
                    self.add_chapter_to_list()

                    chapter_number = chapter_item(".chaptericon").text()
                    chapter_name = chapter_item(".chaptername").text()
                    self.lesson_info_list.clear()
                elif lesson_item:
                    lesson_id = lesson_item.attr("data-id")
                    lesson_keshi = lesson_item(".ks").text()
                    lesson_name = lesson_item(".ksname").text()
                    lesson_type = lesson_item(".ksinfoicon").attr("title")

                    lesson_info = {
                        "lesson_id" : lesson_id,
                        "lesson_name" : lesson_keshi + " " + lesson_name,
                        "lesson_type" : lesson_type
                        }
                    self.lesson_info_list.append(lesson_info)
        
            #把最后一个章节的课程信息添加到列表
            self.add_chapter_to_list()
        except TimeoutException:
            self.get_lesson_infos_in_course()

    def scrab_lesson_infos(self, course_url, file_name):
        try:
            self.get_lesson_infos_in_course(course_url)
            SaveInfoToPickle.save_info(file_name, self.chapter_info_list)
            self.browse.close()
            self.browe_process.terminate()
        except:
            print("爬取课程信息过程发生错误！")

def main():
    chrome_cfg_path = r"D:\wsp\spider\chromeDbgCfg"
    chrome_exe_path = r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe"
    scraber = Study163LessonInfoScraber(chrome_cfg_path, chrome_exe_path)

    course_url = '''https://study.163.com/course/courseLearn.htm?courseId=1004569003#/learn/video?lessonId=1049050008&courseId=1004569003'''
    file_name = "lesson_infos.pkl"
    scraber.scrab_lesson_infos(course_url, file_name)

if __name__ == "__main__":
    main()