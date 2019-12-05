import scrapy
import re

class AuthorSpider(scrapy.Spider):
    name = 'wiki'

    start_urls = ["https://rationalwiki.org/wiki/Capital_punishment","https://www.conservapedia.com/Capital_punishment"
        #,"https://en.wikipedia.org/wiki/Gun_politics_in_the_United_States#Political_arguments","https://en.wikipedia.org/wiki/Prohibition_of_drugs","https://en.wikipedia.org/wiki/Drug_liberalization","https://en.wikipedia.org/wiki/American_Civil_Liberties_Union#Support_and_opposition","https://en.wikipedia.org/wiki/Euthanasia","https://en.wikipedia.org/wiki/Abortion_debate","https://en.wikipedia.org/wiki/Patient_Protection_and_Affordable_Care_Act","https://en.wikipedia.org/wiki/Global_warming","https://en.wikipedia.org/wiki/Net_neutrality","https://en.wikipedia.org/wiki/Genetically_modified_organism","https://en.wikipedia.org/wiki/School_corporal_punishment","https://en.wikipedia.org/wiki/School_voucher","https://en.wikipedia.org/wiki/Same-sex_marriage","https://en.wikipedia.org/wiki/Decriminalizing_sex_work","https://en.wikipedia.org/wiki/Violence_and_video_games","https://en.wikipedia.org/wiki/Minimum_wage#Debate_over_consequences","https://en.wikipedia.org/wiki/Iraq_War","https://en.wikipedia.org/wiki/Illegal_immigration"
                  ]

    def preprocess_text(self, response):
        str = response.xpath('//div[@id="bodyContent"]//text()').get()
        #tags_reg = re.compile('<.*?>')
        #str = re.sub(tags_reg, '', str)
        return str

    def get_source(self, response):
        if "wikipedia" in response.request.url:
            return "wikipedia"

        if "rationalwiki" in response.request.url:
            return "rationalwiki"

        if "conservapedia" in response.request.url:
            return "conservapedia"

    def parse(self, response):

        yield {
            'source': self.get_source(response),
            'title': response.xpath('//*[@id="firstHeading"]/text()').get(),
            #'content': response.xpath('//div[@id="bodyContent"]').get()
            'content': self.preprocess_text(response)
        }