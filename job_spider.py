from pprint import pprint
import csv
from collections import Counter
import requests
from bs4 import BeautifulSoup
import jieba
import matplotlib.pyplot as plt
import codecs,sys
#from wordcloud import WordCloud

class JobSpider():

    def __init__(self):
        self.company = []
        self.text = ""
        self.headers = {'X-Requested-With': 'XMLHttpRequest',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                      'Chrome/56.0.2924.87 Safari/537.36'}

    def job_spider(self):
        """ 爬虫入口 """
        url = "http://search.51job.com/list/252C020000,000000,0000,00,9,99,Python,2,{}.html?" \
             "lang=c&stype=1&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&lonlat=0%2C0" \
             "&radius=-1&ord_field=0&confirmdate=9&fromType=1&dibiaoid=0&address=&line=&specialarea=00&from=&welfare="
        urls = [url.format(p) for p in range(1, 10)]
#print(urls)
# count = 0
        for url in urls:
            r = requests.get(url, headers=self.headers).content.decode('gbk')
            bs = BeautifulSoup(r, 'lxml').find("div", class_="dw_table").find_all("div", class_="el")
#print(bs)
            for b in bs:
                try:
                    href, post = b.find('a')['href'], b.find('a')['title']
                    if post.find("实习") != -1:
                        continue
                    locate = b.find('span', class_='t3').text
                    if locate.find("上海")== -1:
                        continue
                    company_name = b.find('span', class_='t2').text
                    salary = b.find('span', class_='t4').text
                    date = b.find('span', class_='t5').text
                    d = {'href':href, 'company_name':company_name, 'post':post, 'locate':locate, 'salary':salary, 'date':date}
                    self.company.append(d)
#                   count += 1
#                   print(count)
#print(d)
                except Exception:
                    pass
#pprint(self.company)

    def post_require(self):
#       count = 0
        """ 爬取职位描述 """
        for c in self.company:
#           count += 1
#           print(count)
#           pprint(c.get('href'))
            r = requests.get(c.get('href'), headers=self.headers).content.decode('gbk')
#pprint(r)
            bs = BeautifulSoup(r, 'lxml').find('div', class_="bmsg job_msg inbox").text
            s = bs.replace("举报", "").replace("分享", "").replace("\t", "").strip()
            self.text += s
        # print(self.text)
        with open(r".\data\post_require.txt", "w+", encoding="utf-8") as f:
            f.write(self.text)

    def post_desc_counter(self):
        """ 职位描述统计 """
        # import thulac
        post = open(r".\data\post_require.txt", "r", encoding="utf-8").read()
        # 使用 thulac 分词
        # thu = thulac.thulac(seg_only=True)
        # thu.cut(post, text=True)

        # 使用 jieba 分词
        jieba.load_userdict(r".\data\user_dict.txt")
        seg_list = jieba.cut(post, cut_all=False)
        counter = dict()
        for seg in seg_list:
            counter[seg] = counter.get(seg, 1) + 1
        counter_sort = sorted(counter.items(), key=lambda value: value[1], reverse=True)
#pprint(counter_sort)
#with open(r".\data\post_pre_desc_counter.csv", "w+", encoding="utf-8") as f:
        with codecs.open(r".\data\post_pre_desc_counter.csv", "w+", 'utf_8_sig') as f:
#f.write(codecs.BOM_UTF8)
            f_csv = csv.writer(f, dialect='excel')
            f_csv.writerows(counter_sort)

    def post_counter(self):
        """ 职位统计 """
        lst = [c.get('post') for c in self.company]
#pprint(lst)
        counter = Counter(lst)
        counter_most = counter.most_common()
        pprint(counter_most)
#with open(r".\data\post_pre_counter.csv", "w+", encoding="utf-8") as f:
        with codecs.open(r".\data\post_pre_counter.csv", "w+", 'utf_8_sig') as f:
            f_csv = csv.writer(f, dialect='excel')
            f_csv.writerows(counter_most)

    def post_salary_locate(self):
        """ 招聘大概信息，职位，薪酬以及工作地点 """
        lst = []
        for c in self.company:
            lst.append((c.get('salary'), c.get('post'), c.get('locate')))
        pprint(lst)
#with open(r".\data\post_salary_locate.csv", "w+", encoding="utf-8") as f:
        with codecs.open(r".\data\post_salary_locate.csv", "w+", 'utf_8_sig') as f:
            f_csv = csv.writer(f, dialect='excel')
            f_csv.writerows(lst)

    def post_salary(self):
        """ 薪酬统一处理 """
        mouth = []
        year = []
        thouand = []
        with open(r".\data\post_salary_locate.csv", "r", encoding="utf-8") as f:
            f_csv = csv.reader(f)
            for row in f_csv:
                if "万/月" in row[0]:
                    mouth.append((row[0][:-3], row[2], row[1]))
                elif "万/年" in row[0]:
                    year.append((row[0][:-3], row[2], row[1]))
                elif "千/月" in row[0]:
                    thouand.append((row[0][:-3], row[2], row[1]))
        pprint(mouth)
        pprint(thouand)
        calc = []
        for m in mouth:
            s = m[0].split("-")
            calc.append((round((float(s[1]) - float(s[0])) * 0.4 + float(s[0]), 1), m[1], m[2]))
        for y in year:
            s = y[0].split("-")
            calc.append((round(((float(s[1]) - float(s[0])) * 0.4 + float(s[0])) / 12, 1), y[1], y[2]))
        for t in thouand:
            try:
                s = t[0].split("-")
                calc.append((round(((float(s[1]) - float(s[0])) * 0.4 + float(s[0])) / 10, 1), t[1], t[2]))
            except Exception:
                print(s)
#pprint(calc)
        with codecs.open(r".\data\post_salary.csv", "w+", 'utf_8_sig') as f:
            f_csv = csv.writer(f)
            f_csv.writerows(calc)

    def post_salary_counter(self):
        """ 薪酬统计 """
        with open(r".\data\post_salary.csv", "r", encoding="utf-8") as f:
            f_csv = csv.reader(f)
            lst = [row[0] for row in f_csv]
        counter = Counter(lst).most_common()
        pprint(counter)
        with open(r".\data\post_salary_counter1.csv", "w+", encoding="utf-8") as f:
            f_csv = csv.writer(f)
            f_csv.writerows(counter)

    def world_cloud(self):
        """ 生成词云 """
        counter = {}
        with open(r".\data\post_desc_counter.csv", "r", encoding="utf-8") as f:
            f_csv = csv.reader(f)
            for row in f_csv:
                counter[row[0]] = counter.get(row[0], int(row[1]))
            pprint(counter)
        wordcloud = WordCloud(font_path=r".\font\msyh.ttf",
                              max_words=100, height=600, width=1200).generate_from_frequencies(counter)
        plt.imshow(wordcloud)
        plt.axis('off')
        plt.show()
        wordcloud.to_file('.\images\worldcloud.jpg')

    def insert_into_db(self):
        """ 插入数据到数据库 
            create table jobpost(
                j_salary float(3, 1),
                j_locate text,
                j_post text
            );
        """
        import pymysql
        conn = pymysql.connect(host="localhost", port=3306, user="root", passwd="0303", db="chenx", charset="utf8")
        cur = conn.cursor()
        with open(r".\data\post_salary.csv", "r", encoding="utf-8") as f:
            f_csv = csv.reader(f)
            sql = "insert into jobpost(j_salary, j_locate, j_post) values(%s, %s, %s)"
            for row in f_csv:
                value = (row[0], row[1], row[2])
                try:
                    cur.execute(sql, value)
                    conn.commit()
                except Exception as e:
                    print(e)
        cur.close()

if __name__ == "__main__":
    spider = JobSpider()
    spider.job_spider()
    print("job_spider finished")
    spider.post_require()
    print("post_require finished")
    spider.post_desc_counter()
    print("post_desc_counter finished")
    spider.post_counter()
    print("post_counter finished")
    spider.post_salary_locate()
    print("post_salary_locate finished")
    spider.post_salary()
    print("post_salary finished")
    spider.post_salary_counter()
    print("post_salary_counter finished")
#spider.insert_into_db()
    # spider.world_cloud()
