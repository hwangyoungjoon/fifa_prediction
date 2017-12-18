from bs4 import BeautifulSoup
import requests as res
from urllib.parse import urlparse, parse_qs, urljoin
from selenium import webdriver
import re
import threading

def get_player_year_link(): # 플레이어 관련된 피파버전 링크 불러옴
    chromedriver = "./chromedriver"
    driver = webdriver.Chrome(chromedriver)
    basic_url = "https://www.fifaindex.com/players/"
    driver.get(basic_url)
    driver.find_element_by_xpath('/html/body/div[3]/div[2]/div[2]/ol/li[2]/a').click()
    driver.implicitly_wait(2)
    html = driver.page_source
    driver.quit()
    soup = BeautifulSoup(html, "lxml", from_encoding="utf-8")
    content = soup.select("ol.breadcrumb > li > ul")[0]
    fifa_year_links = [{"title": a_tag.text, "link": urljoin(basic_url, a_tag["href"])}
                       for a_tag in content.find_all("a")]
    # 피파타이틀과 url을 가져옴.

    return fifa_year_links

def merge_two_dicts(x, y): #리스트 내에 있는 두개의 dict 합치기

    for c,t in zip(x,y):
        c.update(t)
    return x


def year_page_cralwer(fifa_year_link): #피파 선수 url과 데이터 가져오기
    target_player = []  # url을 담을 리스트
    year_only_link = fifa_year_link["link"]
    page_num = 1
    is_unlast = True
    basic_url = "https://www.fifaindex.com/players/"  #604
    while is_unlast:
        link = year_only_link + str(page_num) + "/"
        get_page = res.get(link)
        page = BeautifulSoup(get_page.content, "lxml")
        player_url = page.select("tbody > tr > td:nth-of-type(4)")# 선수 개인 url
        club = page.find_all("", {"class": "team small"}) # 소속팀 관련 데이터
        nation = page.find_all("", {"class": "nation small"}) # 소속국가 관련 데이터

        player = [{"player_name": player.find("a").get_text(), "url": urljoin(basic_url, player.find("a")["href"])} for
                  player in player_url] #선수와 url 가져오기
        team = [{"team": list(i)[1]["title"], "nation": list(i)[0]["title"]} for i in list(zip(nation, club))] #나라와 클럽명 가져오기
        player_team = merge_two_dicts(player, team) # 리스트 내에 있는 사전 하나씩 붙이기

        if player_team not in target_player:
            target_player += player_team
        if page_num==604:
            break
        # else:
        #     is_unlast=False
        #     print(target_player)


        page_num += 1
    return target_player


def get_player_data(player_url): #선수 개인 속성 데이터 긁어오기
    req = res.get(player_url)
    page = BeautifulSoup(req.content, "lxml")
    stat = page.find_all("p")

    pattern = "(\D)*(\d)*" #정규표현식
    player = {}
    for skill in stat[2:-1]:  #필요없는 데이터 걸러내기
        if "Player Work Rate Medium" in skill.get_text():
            continue
        elif "Skill Moves" in skill.get_text():
            continue
        elif "Birth Date" in skill.get_text():
            continue
        elif "Kit Number" in skill.get_text():
            continue
        elif "Contract Length" in skill.get_text():
            continue
        elif "Weak Foot" in skill.get_text():
            continue
        elif "Joined Club" in skill.get_text():
            continue
            #     print(" ".join(re.search(pattern,b.get_text()).group().split(" ")[:-1]))
        player[" ".join(re.search(pattern, skill.get_text()).group().split(" ")[:-1])] = \
        re.search(pattern, skill.get_text()).group().split(" ")[-1]


    return player


a=get_player_year_link()
b=year_page_cralwer(a[0])