import scrapy
from urllib.request import urlopen
import xml.etree.cElementTree as ET
import pymysql.cursors
from datetime import datetime
from slugify import slugify


class CrawlerSpider(scrapy.Spider):
    sitemap = 'https://zingnews.vn/sitemap/sitemap-news.xml'
    name = "crawler"
    data = []
    translate_data = []

    def start_requests(self):
        urls = self.crawl_by_sitemap_url(self.sitemap)
        for url in urls:
            if not url:
                continue
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        title = response.css('div.page-wrapper h1.the-article-title::text').get()
        if not isinstance(title, str) or title == '':
            return
        short_description = response.css('p.the-article-summary::text').get()
        content = response.css('.the-article-body *').getall()
        if not isinstance(short_description, str) or not isinstance(content, list):
            return
        article_url = response.url
        image = response.css('div.slideshow-images li::attr(data-image)').get()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.createMultipleRecord(
            [title, 0, 1, None, 1, 1, image, 'Zalo', article_url, now, now, now],
            [str(title), 'vi', str(slugify(title)), 0, str(short_description), str(''.join(content)), 1, now, now]
        )

    @classmethod
    def crawl_by_sitemap_url(cls, sitemap_url):
        with urlopen(sitemap_url) as file_data:
            tree = ET.parse(file_data)
            url_set = tree.getroot()
            ns = {'xmlns': 'http://www.sitemaps.org/schemas/sitemap/0.9',
                  'ns_image': 'http://www.google.com/schemas/sitemap-news/0.9'}
            article_data = []
            for url in url_set.findall('xmlns:url', ns):
                article_data.append(url.find('xmlns:loc', ns).text)
        return article_data

    @classmethod
    def createMultipleRecord(cls, article, translation):
        connection = pymysql.connect(
            host='localhost',
            user='sail',
            password='123qwe',
            db='laravel'
        )

        # Save article data to database

        with connection.cursor() as cursor:
            article_sql = "INSERT INTO articles " \
                          "(`name` , `author_id`, `is_crawl`, `category_id`, `is_feature`, `status`, " \
                          "`thumbnail_image`, `source`, `source_link`, `publish_date`, `created_at`, `updated_at`) " \
                          "value (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(article_sql, article)
            translation.append(cursor.lastrowid)
            translation_sql = "INSERT INTO article_translations " \
                              "(`title`, `language_code`, `slug`, `meta_data_id`, `short_description`, `content`, " \
                              "`status`, `created_at`, `updated_at`, `article_id`) " \
                              "values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(translation_sql, translation)
            connection.commit()

        connection.close()

    @classmethod
    def checkTheArticleIsExist(cls, connection, url):
        sql = "SELECT EXISTS(SELECT source_link FROM articles WHERE source_link=%s)"
        with connection.cursor() as cursor:
            cursor.execute(sql, url)
            for row in cursor:
                return row[0]
