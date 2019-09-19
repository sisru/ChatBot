from requests import get
from bs4 import BeautifulSoup, Comment
import pymongo

conn = pymongo.MongoClient('127.0.0.1', 27017)

db = conn.get_database('chatbot')
collection = db.get_collection('univ')

target_url1 = 'http://m.tu.ac.kr/tu/html/02_uni/uni_list.jsp#none'

request = get(target_url1)
raw_html = request.text
soup_obj = BeautifulSoup(raw_html, 'html.parser')

# 주석처리 된 코드 제거
for element in soup_obj(text=lambda text: isinstance(text, Comment)):
    element.extract()

# ul태그 중 클래스 이름이 'menulist_3st' 인 태그 로드
major_ul_list = soup_obj.select('ul.depth1')

# 과에 맞게 과 링크 저장
# {'메카트로닉스공학부' : 'http://m.tu.ac.kr/mechas/index.jsp', '자동차공학부' : 'http://m.tu.ac.kr/automobile/index.jsp'}
daehak_list = []

for major_ul in major_ul_list:
    # li 하위에 있는 a태그 로드
    daehak_li_list = major_ul.select('li>a>p')
    daehak_name = daehak_li_list[0].text
    print(daehak_name)

    daehak_list.append(daehak_name)

    major_a_list = major_ul.select('li>ul>li>ul>li>a')

    major_list = []
    for major in major_a_list :
        major_name = major.text
        major_list.append(major_name)
        major_url = major.get('href').replace("index", "html/01_about/about_04")

        prof_list = []
        if major_url == "#":
            continue

        prof_req = get(major_url)
        prof_html = prof_req.text
        prof_soup = BeautifulSoup(prof_html, 'html.parser')
        count = 0
        for tag in prof_soup.select('#tu_content > div > ul > li'):
            str_tag = str(tag)
            if str_tag.find('prof_name')>=0:
                prof_name = tag.text.strip()
                prof_name = prof_name.replace(".", "")
                prof_list.append(prof_name)
                count += 1

            elif str_tag.find('소속') >= 0:
                prof_major = tag.text
                prof_major = prof_major.replace("소속", "")
                prof_major = prof_major.replace(":", "").strip()
                count += 1

            elif str_tag.find('연구실') >= 0 :
                prof_lab = tag.text
                prof_lab = prof_lab.replace("연구실", "")
                prof_lab = prof_lab.replace(":", "").strip()
                count += 1

            elif str_tag.find('연락처') >= 0 :
                prof_tel = tag.text
                prof_tel = prof_tel.replace("연락처", "")
                prof_tel = prof_tel.replace(":", "").strip()
                count += 1

            if count == 4 :
                query = {"div": '완료', prof_name: {"prof_major" : prof_major, 'prof_tel': prof_tel, "prof_lab" : prof_lab}, "next_node" : "완료" }
                print(query)
                collection.insert_one(query)
                count = 0

        collection.insert_one({"div": '교수', major_name : prof_list ,"next_node" : "완료"})
    collection.insert_one({"div": '학과', daehak_name: major_list, "next_node": "교수"})
collection.insert_one({"div": "대학", "list": daehak_list, "next_node": "학과"})