from bs4 import BeautifulSoup
import re
import requests
import pymysql
import datetime
import time
def data2mysql(data):
    cnx = pymysql.connect(user='root', password='123456',
                                host='127.0.0.1',
                                database='pearadminflask', port=3306)

    cursor = cnx.cursor()
    
    add_data = ("INSERT INTO vulnerability "
                "(CNNVD, 危害等级, CVE编号, 漏洞类型, 发布时间, 威胁类型, 更新时间, 厂商, 漏洞来源, 漏洞公告, 参考网址, 受影响实体, 补丁) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
    data['发布时间'] = datetime.datetime.strptime(data['发布时间'], '%Y-%m-%d')
    data['更新时间'] = datetime.datetime.strptime(data['更新时间'], '%Y-%m-%d')

    data_tuple = (data['CNNVD'], data['危害等级'], data['CVE编号'], data['漏洞类型'], data['发布时间'], data['威胁类型'], data['更新时间'], data['厂商'], data['漏洞来源'], data['漏洞公告'], data['参考网址'], data['受影响实体'], data['补丁'])

    query = "SELECT COUNT(*) FROM vulnerability WHERE CNNVD = %(CNNVD)s"
    # execute the query
    cursor.execute(query, data)
    # fetch the result
    result = cursor.fetchone()
    # check if the CNNVD already exists
    if result[0] == 0:
        print("NOT EXIST")
        cursor.execute(add_data, data_tuple)
    else:
        print("IS EXISTED")
    cnx.commit()
    cursor.close()
    cnx.close()


CNNVD_ID = []

CVE = []
def spider_main(page):
# 设置要爬取的网页URL
    
    for i in range(page):
        url = 'http://123.124.177.30/web/vulnerability/querylist.tag?pageno=' + str(i) + '&repairLd='

        # 使用requests库发送GET请求获取网页HTML
        response = requests.get(url)
        response.encoding = response.apparent_encoding  # 确保正确的字符编码

        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找所有的<p>标签
        paragraphs = soup.find_all('p')
        print(i)
        # 遍历所有的<p>标签
        for paragraph in paragraphs:
        # 检查该标签是否有<a>标签，且<a>标签的文本是否包含"CNNVD"
            a_tag = paragraph.find('a')
            if a_tag and "CNNVD" in a_tag.text:
                print(a_tag.text)  # 打印符合条件的<a>标签的文本
                CNNVD_ID.append(a_tag.text)




def spider_page(ID):
    url = 'http://123.124.177.30/web/xxk/ldxqById.tag?CNNVD=' + ID
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')#'lxml')

    
    
    info = {"CNNVD": ID}
    
    skip_first_span = True
    detail_info = soup.find('div', {'class': 'detail_xq w770'}).find_all('li')
    for item in detail_info:
        span_tag = item.find('span')
        if span_tag is not None:
            if skip_first_span:
                skip_first_span = False
                continue

            info_type = span_tag.text.strip('：')
            a_tag = item.find('a')
            if a_tag is not None:
                info_data = a_tag.text.strip()
            else:
                info_data = ''
            
            info_type = info_type.replace('\xa0', '')
            info[info_type] = info_data
    

    sections = soup.find_all('div', class_='d_ldjj m_t_20')
    for section in sections:
        title = section.find('h2').text.strip()
        paragraphs = section.find_all('p')
        p_texts = [p.text.strip() for p in paragraphs]
        info[title] = p_texts

    # Extract patch link
    patch_div = soup.find('ul', {'id': 'pat'})
    if patch_div:
        a_tag = patch_div.find('a')
        if a_tag and 'href' in a_tag.attrs:
            patch_link = a_tag['href']
            info['补丁'] = [f'http://123.124.177.30{patch_link}']


    for key, value in info.items():
        if isinstance(value, list):
            info[key] = ' '.join(value)

    CVE.append(info)
    return info


def spider_update():
    for i in range(5):
        url = 'http://123.124.177.30/web/vulnerability/querylist.tag?pageno=' + str(i) + '&repairLd='

        # 使用requests库发送GET请求获取网页HTML
        response = requests.get(url)
        response.encoding = response.apparent_encoding  # 确保正确的字符编码

        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找所有的<p>标签
        paragraphs = soup.find_all('p')
        print(i)
        # 遍历所有的<p>标签
        for paragraph in paragraphs:
        # 检查该标签是否有<a>标签，且<a>标签的文本是否包含"CNNVD"
            a_tag = paragraph.find('a')
            if a_tag and "CNNVD" in a_tag.text:
                print(a_tag.text)  # 打印符合条件的<a>标签的文本
                CNNVD_ID.append(a_tag.text)

    for i in CNNVD_ID:
        time.sleep(5)
        res = spider_page(i)
        print(res)
        data2mysql(res)
        print("===DONE===")

def handle():
    url = 'http://123.124.177.30/web/vulnerability/querylist.tag?pageno=1'

    response = requests.get(url)
    response.encoding = response.apparent_encoding  # 确保正确的字符编码

    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(response.text, 'html.parser')


    # find all 'a' tags with 'href' that contains 'CNNVD'
    a_tags = soup.find_all('a', href=re.compile("CNNVD"))

    # get the CNNVD number from the first 'a' tag
    if a_tags:
        href = a_tags[0].get('href')
        cnnvd_number = re.search('CNNVD=(CNNVD-\d+-\d+)', href)
        
        if cnnvd_number:
            print(cnnvd_number.group(1))

    data = cnnvd_number.group(1)
    cnx = pymysql.connect(user='vul', password='123456',
                            host='159.75.50.79',
                            database='vul', port=3306)

    cursor = cnx.cursor()

    query = "SELECT COUNT(*) FROM vulnerability WHERE CNNVD =" + data
    # execute the query
    cursor.execute(query)

    result = cursor.fetchone()
    # check if the CNNVD already exists
    if result[0] != 0:
        print("DO NOT NEED UPDATE")
        return
    else:
        spider_update()

handle()