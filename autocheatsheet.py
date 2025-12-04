# -*- coding: utf-8 -*-
"""
全自动脚本：
登录 -> 进入页面 -> (可选)点击菜单 -> 勾选 checkbox -> 点击编辑 -> 抓 nodename -> 导出 CSV
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv


# ================== 需要你自己填的配置 ==================

LOGIN_URL = "https://YOUR_LOGIN_URL_HERE"      # 登录页
LIST_URL = "https://YOUR_LIST_URL_HERE"        # 编辑列表的页面

USERNAME = "YOUR_USERNAME"
PASSWORD = "YOUR_PASSWORD"

AFTER_LOGIN_KEYWORD_IN_URL = "index"          # 登录后 URL 中出现的关键字

OUTPUT_CSV = "names.csv"

# 是否需要点击左侧菜单（如果没有就 False）
ENABLE_CLICK_MENU_NODE = False
MENU_NODE_ACE = "21"

# checkbox & 编辑按钮的 selector（明天在公司确定）
CHECKBOX_SELECTOR = "input[type='checkbox']"  # TODO: 进入内网后改成更精确的
EDIT_BUTTON_XPATH = "//button[contains(text(),'编辑')] | //a[contains(text(),'编辑')]"

# =====================================================


def create_driver(headless=False):
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    return driver


def login(driver):
    """登录"""
    driver.get(LOGIN_URL)
    wait = WebDriverWait(driver, 15)

    form = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#loginForm, form.aui-form")
        )
    )

    username_input = form.find_element(By.CSS_SELECTOR, "input[type='text']")
    password_input = form.find_element(By.CSS_SELECTOR, "input[type='password']")

    username_input.send_keys(USERNAME)
    password_input.send_keys(PASSWORD)

    login_btn = form.find_element(
        By.CSS_SELECTOR,
        "button[type='submit'], input[type='submit'], button.aui-btn"
    )
    driver.execute_script("arguments[0].click();", login_btn)

    WebDriverWait(driver, 15).until(
        EC.url_contains(AFTER_LOGIN_KEYWORD_IN_URL)
    )


def go_to_list_page(driver):
    """进入包含 checkbox + 编辑的列表页面"""
    driver.get(LIST_URL)


def collect_names(driver):
    """
    不需要滚动的版本：
    找到 div.mCSB_container[id^='mCSB_']，
    然后抓其中 ul > li[nodename]
    """
    wait = WebDriverWait(driver, 15)

    container = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.mCSB_container[id^='mCSB_']")
        )
    )

    lis = container.find_elements(By.CSS_SELECTOR, "ul > li[nodename]")

    records = []
    for li in lis:
        name = li.get_attribute("nodename")
        acee = li.get_attribute("acee")
        if name:
            records.append({"name": name, "acee": acee})

    print(f"共抓到 {len(records)} 条记录：")
    return records


def save_to_csv(records, filename):
    fieldnames = ["name", "acee"]
    with open(filename, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    print(f"数据已保存到 {filename}")


def main():
    driver = create_driver(headless=False)
    try:
        login(driver)
        go_to_list_page(driver)

        records = collect_names(driver)
        save_to_csv(records, OUTPUT_CSV)

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
