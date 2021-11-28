"""
Запускает браузер chrome.
В автоматическом режиме происходит авторизация на сайте.

Каждую минуту обновляется страница (https://betscsgo.in/),
результат (HTML код страницы) пишется в базу данных datahtml.db.

При наличии заданий в файле task.txt открывается страница (https://betscsgo.in/match/342329/)
с результатом матча. Результат (HTML код страницы) пишется в базу данных result_page.db.

auto_clear_db -> Автоочистка данный в базе datahtml.db для экономии места на диске.

Так как базаданных sqlite это всего лишь файлики то необходимо расположить их в одной директории для
того что бы другой скрипт мог безпрепятственно подключиться к этим данным.
"""
from datetime import datetime
import os, time
from Globals import LOGIN, PASSWORD, SITE, SHARE_DIR
from itertools import count
from Model import HtmlData, ResultPage
from selenium.webdriver.common.keys import Keys
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
from tools import log

import undetected_chromedriver.v2 as uc

options = uc.ChromeOptions()

# setting profile
options.user_data_dir = "/tmp/chro"

# another way to set profile is the below (which takes precedence if both variants are used
options.add_argument('--user-data-dir=/tmp/chro')
options.add_argument('--headless')

# just some options passing in to skip annoying popups
options.add_argument('--no-first-run --no-service-autorun --password-store=basic')
driver = uc.Chrome(options=options)
driver.maximize_window()

log_content = log("MAIN")
URL = SITE

log_content.info("Start script")


def scene(driver):
    driver.execute_script('document.querySelector("a.userbar-login").click()')
    time.sleep(5)
    login = driver.find_element_by_css_selector("input.textField[name=username]")
    password = driver.find_element_by_css_selector("input.textField[name=password]")
    btn = driver.find_element_by_css_selector("#login_btn_signin input.btn_green_white_innerfade")
    login.send_keys(LOGIN)
    password.send_keys(PASSWORD)
    btn.click()
    time.sleep(5)


def work(driver, url):
    log_content.debug("Get %s", url)
    driver.get(url)
    time.sleep(8)
    html = str(driver.page_source)

    log_content.debug("Response %s. Length: %d", url, len(html))
    log_content.debug("Write to db")

    HtmlData.insert_remove({
        "m_time": datetime.now().timestamp(),
        "html": html
    })

    log_content.debug("End Job")


def work_for_result_page(driver, m_id):
    url = "https://betscsgo.in/match/{}".format(m_id)
    log_content.debug("Get %s", url)
    driver.get(url)
    time.sleep(7)
    html = str(driver.page_source)

    log_content.debug("Response %s. Length: %d", url, len(html))
    log_content.debug("Write to db")

    ResultPage.insert({
        "m_time": datetime.now().timestamp(),
        "data": html,
        "m_id": m_id
    }).execute()

    log_content.debug("End Job")


def check_task():
    cache = set()

    def _check_task():
        path = os.path.join(SHARE_DIR, "task.txt")
        with open(path, "r", encoding="utf-8") as f:
            _data = f.read().strip()
        current_ids = set(int(x) for x in _data.split("\n") if x)
        new_ids = current_ids.difference(cache)
        for el in new_ids:
            cache.add(el)
        log_content.info("New m_id: %s", str(new_ids))
        return new_ids

    return _check_task


def prepare(driver):
    # driver = webdriver.Chrome()
    driver.execute_script("window.open('https://betscsgo.in/','_blank');")
    time.sleep(10)
    driver.switch_to.window(driver.window_handles[0])
    driver.close()
    driver.switch_to.window(driver.window_handles[0])


def main():
    # driver = init_driver_firefox()
    # driver = init_driver()

    with driver:
        driver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        res = driver.get('https://betscsgo.in')  # known url using cloudflare's "under attack mode"
        time.sleep(2)
        log_content.info(res)
        log_content.debug("starting chrome")
        log_content.debug("open page {}".format(URL))
        driver.get(URL)
        log_content.info("Waiting 15 sec")

        driver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        time.sleep(15)

        scene(driver)

        driver.get(URL)
        log_content.debug("Checked length page:  {}".format(len(driver.page_source)))

        _check_task = check_task()

        # =========== work position =============
        for _ in count():
            work(driver, URL)

            result = _check_task()
            if result:
                for m_id in result:
                    work_for_result_page(driver, m_id)

            time.sleep(25)


if __name__ == '__main__':
    main()
    # check_task = check_task()
    # result = check_task()
    # print(result)

