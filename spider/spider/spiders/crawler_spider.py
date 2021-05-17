import scrapy
from urllib.request import urlopen
import xml.etree.cElementTree as ET
import pymysql.cursors


class CrawlerSpider(scrapy.Spider):
    name = "crawler"
    data = []
    translate_data = []

    def start_requests(self):

        sitemap = 'https://zingnews.vn/sitemap/sitemap-article-20210418.xml'
        urls = self.crawl_by_sitemap_url(sitemap)
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        if not isinstance(response.css('div.page-wrapper h1.the-article-title::text').get(), str):
            return
        title = response.css('div.page-wrapper h1.the-article-title::text').get()
        content = response.css('section.main div.the-article-body::text').get()
        author = response.css('ul.the-article-meta li.the-article-author a::text').get()
        image = response.css('section.main div.the-article-body img::text').get()
        data = [title, author, 1, 1, image]
        print(title)
        # self.data.append()
        # self.translate_data.append([title])
        # self.createMultipleRecord()

    @classmethod
    def crawl_by_sitemap_url(cls, sitemap_url):
        # connection = pymysql.connect(
        #     host='localhost',
        #     user='sail',
        #     password='123qwe',
        #     db='laravel'
        # )
        with urlopen(sitemap_url) as file_data:
            tree = ET.parse(file_data)
            url_set = tree.getroot()

            ns = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9',
                  'sitemap_image': 'http://www.google.com/schemas/sitemap-image/1.1'}
            article_data = []
            article_translation_data = []
            for url in url_set.findall('sitemap:url', ns):
                article = cls.analyzeZingSiteMap(url, ns)
                article_data.append(article)
                # print(article[0])
            # cls.createMultipleRecord(connection=connection, data=data)
            # created_count = len(article_data)

            # print("Record mới được tạo: " + str(created_count))
        # connection.close()
        return article_data

    @classmethod
    def createMultipleRecord(cls, connection, data):
        with connection.cursor() as cursor:
            sql = "INSERT INTO articles " \
                  "(name , author_id, is_feature, status, thumbnail_image, source_link, " \
                  "publish_date, created_at, updated_at) " \
                  "values " \
                  "(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.executemany(sql, data)
            connection.commit()

    @classmethod
    def checkTheArticleIsExist(cls, connection, url):
        sql = "SELECT EXISTS(SELECT source_link FROM articles WHERE source_link=%s)"
        with connection.cursor() as cursor:
            cursor.execute(sql, url)
            for row in cursor:
                return row[0]

    @classmethod
    def analyzeZingSiteMap(cls, url, ns):
        site_loc = url.find('sitemap:loc', ns).text
        return site_loc
