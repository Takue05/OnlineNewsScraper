import csv
import os
from datetime import datetime
from scrapy import signals
from scrapy.exporters import CsvItemExporter


class DailyCSVPipeline:
    def __init__(self):
        self.files = {}
        self.exporters = {}
        self.data_dir = 'data/daily'
        os.makedirs(self.data_dir, exist_ok=True)

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        today = datetime.now().strftime('%Y-%m-%d')
        file_path = f'{self.data_dir}/{today}_{spider.name}.csv'
        self.files[spider] = open(file_path, 'wb')
        self.exporters[spider] = CsvItemExporter(self.files[spider])
        self.exporters[spider].start_exporting()

    def spider_closed(self, spider):
        self.exporters[spider].finish_exporting()
        self.files[spider].close()

    def process_item(self, item, spider):
        self.exporters[spider].export_item(item)
        return item