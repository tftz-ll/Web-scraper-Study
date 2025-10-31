import requests
import fake_useragent
import lxml
from lxml import etree
import pymongo
import time




class douban():
    rank = ''
    title = ''
    src = ''
    hotContent = ''

    def request(self):
        """post requests to target website"""
        res = requests.get(url, headers=headers, params=params)  # 对目标网站发起请求
        # print(res.text)
        return res.text

    def abstract(self, txt, i):
        """use Xpath function to abstract data from response
        shift document types from text to html
        """
        tree = etree.HTML(txt)
        self.rank = tree.xpath(f"//ol[@class='grid_view']/li[{i}]/div/div/em/text()")
        self.title = tree.xpath(f"//ol[@class='grid_view']/li[{i}]/div/div/a/img/@alt")
        self.src = tree.xpath(f"//ol[@class='grid_view']/li[{i}]/div/div/a/img/@src")
        self.hotContent = tree.xpath(f"//ol[@class='grid_view']/li[{i}]/div/div[2]/div[2]/p/span/text()")
        if self.hotContent == []:
            self.hotContent = ["无热评"]


# 生成发起请求必须数据
ua = fake_useragent.FakeUserAgent()
url = "https://movie.douban.com/top250"
headers = {
    "User-Agent": ua.random
}

"""creat MonGoDB document and saving"""
# 创建MonGoDB数据表单，为了不浪费资源，只在外面进行一次生成关闭
client = pymongo.MongoClient(host="localhost", port=27017)
table = client["douban"]["data"]

txt = douban()

"""we need While loop to make filter
    page for page count
    cnt for one page's data count
"""
page = 0  # 页计数器，记录页数
cnt = 1  # 单页采集的计数器，记录单页面的数据量
while True:
    time.sleep(1)  # 防止请求过快被拦截，当然还有ip代理池的方法，将会在后续持续更新
    params = {
        'start': f'{page*25}',
        'filter': ""
    }
    print(f"正在采集第{page}页")
    a = txt.request()
    print(a)
    page += 1
    """loop abstract data of one page and make a sentence to break one page"""
    while True:
        txt.abstract(a, cnt)
        if txt.rank == []:
            cnt = 1
            break
        table.insert_one({
            "rank": txt.rank[0],
            "title": txt.title[0],
            "src": txt.src[0],
            "hotContent": txt.hotContent[0],
        })
        cnt += 1

client.close()









