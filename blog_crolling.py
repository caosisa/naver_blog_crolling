# 네이버 블로그 이미지 크롤러
# 라이브러리들
import urllib.request
import urllib.parse
import os
import re
import getpass
import requests
from bs4 import BeautifulSoup


# 함수 설정
# 주어진 URL에서 게시글의 이미지 링크를 가져오는 함수
def linkget(url):
    if url.find("m.blog.naver.com") == -1:
        url = url.replace("blog.naver.com", "m.blog.naver.com")
    try:
        response = requests.get(url)
    except:
        return
    soup = BeautifulSoup(response.content, 'html.parser')
    try:
        category = soup.find("a", class_="link sp_after")['href'].split("&")[-2].replace("categoryNo=", "")
        blogId = soup.find("meta", property="og:url")["content"].split('/')[-2]
        if category == None:
            raise
    except:
        try:
            url2 = url.replace("#postlist_block", "").split("?")
            category = url2[-1]
            if category.find("blogId") == -1:
                blogId = url2[-2].split("/")[-1]
                category = category.replace("categoryNo=", "")
            else:
                category = category.split("&")
                for ii in category:
                    if ii.find("blogId") != -1:
                        blogId = ii.replace("blogId=", "")
                for iii in category:
                    if iii.find("parent") == -1 and iii.find("ategory") != -1:
                        category = iii.replace("categoryNo=", "")
                if str(type(category)) == "<class 'list'>":
                    return "photoNotFound"
        except:
            return "photoNotFound"
    linklist = []
    end = False
    overlapped = 0
    for i in range(1, 9999):
        category_url = "https://blog.naver.com/PostTitleListAsync.naver?blogId=" + blogId + "&viewdate=&currentPage=" + str(
            i) + "&CategoryNo=" + category + "&countPerPage=30"
        categoryresponse = requests.get(category_url)
        categorytext = categoryresponse.text
        try:
            categorysoup = categorytext.split('"tagQueryString":"')[1].replace('"}', '')
        except:
            return "postnotfound1"
        logNo = categorysoup.split("&logNo=")
        logNo.remove("")
        for i2 in logNo:
            try:
                link = "https://m.blog.naver.com/" + blogId + "/" + i2
                if link in linklist:
                    overlapped = overlapped + 1
                    if overlapped >= 5:
                        end = True
                        break
                    continue
                linklist.append(link)
            except:
                break
        if end == True:
            return linklist


# 주어진 URL에서 해당 카테고리의 모든 게시글 이미지를 가져오는 함수
def linkget_allcategory(url):
    try:
        url2 = url.replace("#postlist_block", "").split("?")
        category = url2[-1]
        if category.find("blogId") == -1:
            blogId = url2[-2].split("/")[-1]
            category = category.replace("categoryNo=", "")
        else:
            category = category.split("&")
            for ii in category:
                if ii.find("blogId") != -1:
                    blogId = ii.replace("blogId=", "")
            for iii in category:
                if iii.find("parentCategoryNo") != -1:
                    category = iii.replace("parentCategoryNo=", "")
            if str(type(category)) == "<class 'list'>":
                return "postnotfound2"
    except:
        return "photoNotFound"
    linklist = []
    end = False
    overlapped = 0
    for i in range(1, 9999):
        category_url = "https://blog.naver.com/PostTitleListAsync.naver?blogId=" + blogId + "&viewdate=&currentPage=" + str(
            i) + "&parentCategoryNo=" + category + "&countPerPage=30"
        categoryresponse = requests.get(category_url)
        categorytext = categoryresponse.text
        if categorytext.find('"tagQueryString":"') == -1:
            return "postnotfound2"
        categorysoup = categorytext.split('"tagQueryString":"')[1].replace('"}', '')
        logNo = categorysoup.split("&logNo=")
        logNo.remove("")
        for i2 in logNo:
            try:
                link = "https://m.blog.naver.com/" + blogId + "/" + i2
                if link in linklist:
                    overlapped = overlapped + 1
                    if overlapped >= 5:
                        end = True
                        break
                    continue
                linklist.append(link)
            except:
                break
        if end == True:
            return linklist


# 텍스트에서 특수 문자를 제거하는 함수
def clean_text(inputString):
    text_rmv = re.sub('[\\\/:*?"<>|]', ' ', inputString)
    text_rmv = text_rmv.strip()
    text_rmv = text_rmv.rstrip(".")
    return text_rmv


# 사용자에게 블로그 게시글 주소를 입력받아 이미지를 다운로드하도록 하는 함수
def showDialog():
    text = input("네이버 블로그 게시글 주소를 입력하세요\n")
    global onlyone
    onlyone = True
    textlist = text.split(" ")
    for i in textlist:
        download(i)


# 사용자에게 블로그 게시글 주소 또는 카테고리 주소를 입력받아 해당 카테고리의 이미지를 다운로드하도록 하는 함수
def showDialog2():
    text = input('네이버 블로그 게시글 주소 또는 카테고리 주소를 입력하세요\n')

    global onlyone
    onlyone = False
    global isAllCategory
    isAllCategory = False
    category_download(text)

def get_default_save_path():
    username = getpass.getuser()
    default_save_path = f"C:/Users/{username}/Downloads"
    return default_save_path
# 주어진 URL에서 이미지를 다운로드하는 함수
def download(url):
    if url.find("m.blog.naver.com") == -1:
        url = url.replace("blog.naver.com", "m.blog.naver.com")
    try:
        response = requests.get(url)
    except:
        print("Error : 주소가 올바르지 않습니다\n")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    try:
        title = soup.find('meta', property="og:title")['content']
    except:
        print("Error : 네이버 블로그 게시글 주소가 아닙니다\n")
        return
    file_box = soup.find('div', id='_photo_view_property')
    try:
        file = file_box['attachimagepathandidinfo'].strip("[""]").replace('"path"', '').replace('"id"', '').split('"')
    except:
        print("Error : 사진 파일을 찾을 수 없습니다\n")
        return

    username = getpass.getuser()
    save_path = os.path.join(default_save_path, clean_text(title) + "/")
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    publish_date_element1 = soup.find('p', class_='blog_date')
    publish_date_element2 = soup.find('span', class_='date')

    if publish_date_element1:
        publish_date = publish_date_element1.text.strip()
    elif publish_date_element2:
        publish_date = publish_date_element2.text.strip()
    else:
        publish_date = "작성일 가져오기 실패"

    content = soup.find('div', class_='se-main-container').get_text(separator='\n', strip=True)
    with open(os.path.join(save_path, '본문.txt'), 'w', encoding='utf-8') as f:
        f.write(publish_date+"\n\n")
        f.write(content)

    listDir = os.listdir(save_path)
    listSize = {}
    for i in listDir:
        listSize[i] = os.path.getsize(save_path + i)
    for i in range(0, 9999):
        a = i * 2 + 1
        try:
            link = "https://blogfiles.pstatic.net" + file[a]
            try:
                response = requests.head(link, allow_redirects=True)
            except:
                return
            fileSize = response.headers.get("Content-Length", -1)

            if fileNameOption == "1":
                fileName = str(i + 1) + "." + clean_text(urllib.parse.unquote(link.split('/')[-1]).split('.')[-1])
            elif fileNameOption == "2":
                fileName = str(i + 1) + "_" + clean_text(urllib.parse.unquote(link.split('/')[-1]))
            elif fileNameOption == "3":
                fileName = clean_text(urllib.parse.unquote(link.split('/')[-1]))

            try:
                if listSize[fileName] == int(fileSize):
                    continue
            except:
                pass
        except:
            global onlyone
            if onlyone == True:
                print(title + " 완료\n")
            else:
                global repeated
                global linklist
                completed = title + " 완료 " + str(repeated) + "/" + str(len(linklist))
                print(completed)

            break
        urllib.request.urlretrieve(link, save_path + fileName)


# 주어진 URL에서 해당 카테고리의 모든 게시글 이미지를 다운로드하는 함수
def category_download(url):
    global linklist
    global isAllCategory
    if isAllCategory == False:
        linklist = linkget(url)
    else:
        linklist = linkget_allcategory(url)
    if linklist == None:
        print("Error : 주소가 올바르지 않습니다\n")
        return
    elif linklist == "photoNotFound":
        print("Error : 올바른 네이버 블로그 주소가 아닙니다\n")
        return
    elif linklist == "postnotfound1":
        print("Error : 글을 찾을 수 없습니다 (큰 카테고리의 글이 모두 작은 카테고리에 포함되어 있으면 큰 카테고리를 개별 카테고리 다운로드하는 것은 불가능합니다)")
        return
    elif linklist == "postnotfound2":
        print("Error : 글을 찾을 수 없습니다 (작은 카테고리의 링크로는 전체 카테고리 다운로드가 불가능합니다)")
        return
    linklist.reverse()
    print("카테고리 내에서 {}개의 게시물 발견".format(str(len(linklist))))
    text2 = input('범위 입력 (예시1 :1 9) (예시2 :-5 -1) (입력하지 않으면 전부 다운)\n')
    a = text2.split(" ")[0]
    try:
        if a == '':
            a = None
        elif int(a) > 0:
            a = int(a) - 1
        elif int(a) == 0:
            a = None
        else:
            a = int(a)
    except:
        print("Error : 범위를 제대로 입력해 주세요\n")
        return
    try:
        b = text2.split(" ")[1]
    except:
        b = 0
    try:
        if int(b) > 0:
            b = int(b)
        elif int(b) == -1 or int(b) == 0:
            b = None
        else:
            b = int(b) + 1
    except:
        print("Error : 범위를 제대로 입력해 주세요\n")
        return
    linklist = linklist[a:b]
    if linklist == []:
        print("Error : 범위를 제대로 입력해 주세요\n")
        return
    global repeated
    repeated = 1


    for link in linklist:
        download(link)
        repeated = repeated + 1
    print("")

# 설정 변경을 위한 부가적인 기능이 제공되는 함수
# 실제 코드 실행
global fileNameOption
fileNameOption = "1"
default_save_path = get_default_save_path()
realdir = os.path.dirname(os.path.abspath(__file__))
os.chdir(realdir)
try:
    setting = open(realdir + "/setting.txt", "r")
    currentdir = setting.read()
    os.chdir(currentdir)
except:
    currentdir = realdir
print("###네이버 블로그 크롤러###\n")
while True:
    select = input("하나만 다운로드:1 / 카테고리 다운로드:2 / 설정 변경:3\n")
    if select == "1":
        print("1개 다운로드 선택")
        showDialog()
    elif select == "2":
        print("개별 카테고리 다운로드 선택")
        showDialog2()
    elif select == "3":
        select = input("저장 경로 변경:1 / 파일 이름 저장 방식 변경:2\n")
        if select == "1":
            pre_savepath = os.path.abspath(input("변경할 저장 경로를 입력하세요\n")).replace("\\", "/")
            try:
                os.chdir(pre_savepath)
                setting = open(realdir + "/setting.txt", "w")
                setting.write(pre_savepath)
                currentdir = pre_savepath
                setting.close()
            except:
                print("Error : 제대로 된 저장 경로를 입력해 주세요\n")
                os.chdir(currentdir)
                setting.close()
        elif select == "2":
            select = input(
                "파일 이름 숫자로 쓰기(원본 이미지 제목 무시):1 / 원래 이름 앞에 접두어로 숫자 붙이기:2 / 원래 이름 그대로 쓰기(같은 이름의 파일이 있으면 한 쪽이 안 받아질 수 있음):3\n")
            if select == "1":
                fileNameOption = "1"
            elif select == "2":
                fileNameOption = "2"
            else:
                print("Error : 1, 2 중 하나를 입력해 주세요")
        else:
            print("Error : 1, 2 중 하나를 입력해 주세요\n")
    else:
        print("Error : 1, 2, 3 중 하나를 입력해 주세요\n")
