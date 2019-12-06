import scrapy
import re

class AuthorSpider(scrapy.Spider):
    name = 'wiki'

    start_urls = ["https://www.conservapedia.com/Capital_punishment","https://www.conservapedia.com/Gun#Gun_control","https://www.conservapedia.com/Marijuana","https://www.conservapedia.com/ACLU","https://www.conservapedia.com/Euthanasia","https://www.conservapedia.com/Abortion","https://www.conservapedia.com/ObamaCare","https://www.conservapedia.com/Climate_change","https://www.conservapedia.com/Network_neutrality","https://www.conservapedia.com/Genetically_modified_organism","https://www.conservapedia.com/Corporal_punishment","https://www.conservapedia.com/School_vouchers","https://www.conservapedia.com/Same-sex_marriage","https://www.conservapedia.com/Prostitution","https://www.conservapedia.com/Video_game#Arguments_against_video_game_usage","https://www.conservapedia.com/Minimum_wage","https://www.conservapedia.com/Iraq_War","https://www.conservapedia.com/Illegal_immigration",
                  "https://rationalwiki.org/wiki/Capital_punishment","https://rationalwiki.org/wiki/Gun_control#Common_arguments_against_gun_control","https://rationalwiki.org/wiki/Cannabis","https://rationalwiki.org/wiki/American_Civil_Liberties_Union","https://rationalwiki.org/wiki/Euthanasia","https://rationalwiki.org/wiki/Abortion","https://rationalwiki.org/wiki/Affordable_Care_Act","https://rationalwiki.org/wiki/Global_warming","https://rationalwiki.org/wiki/Net_neutrality","https://rationalwiki.org/wiki/Genetically_modified_food","https://rationalwiki.org/wiki/Corporal_punishment","https://rationalwiki.org/wiki/School_vouchers","https://rationalwiki.org/wiki/Same-sex_marriage","https://rationalwiki.org/wiki/Prostitution","https://rationalwiki.org/wiki/Video_game#Violence","https://rationalwiki.org/wiki/Minimum_wage","https://rationalwiki.org/wiki/Iraq_War","https://rationalwiki.org/wiki/Illegal_immigration"
                  #"https://www.conservapedia.com/Marijuana","https://www.conservapedia.com/Network_neutrality","https://www.conservapedia.com/Genetically_modified_organism","https://www.conservapedia.com/Corporal_punishment","https://www.conservapedia.com/Prostitution","https://rationalwiki.org/wiki/Capital_punishment","https://rationalwiki.org/wiki/Net_neutrality","https://rationalwiki.org/wiki/Genetically_modified_food","https://rationalwiki.org/wiki/School_vouchers","https://rationalwiki.org/wiki/Minimum_wage"
                  ]

    def preprocess_text(self, response):

        str = response.xpath('//div[@class="mw-content-ltr"]').get()

        # remove tags
        tags_reg = re.compile('<.*?>')
        str = re.sub(tags_reg, '', str)

        # replace multiple \n by one
        str = re.sub('\n+','\n',str).strip()

        # remove brackets texts. e.g., [1], [edit], [cite] or [citation NOT needed]
        bracket_reg = re.compile('\[\w+\s*\w*\s*\w*\]')
        #bracket_reg = re.compile('\[(\w+\s*\w*\d*/*:*)+\]')
        str = re.sub(bracket_reg, '', str)

        # split text by paragraph
        paragraph = str.split("\n")

        # delete text after the "See Also" section
        idx = paragraph.index("References")
        paragraph = paragraph[:idx]

        return paragraph

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
            'title': response.xpath('//*[@id="firstHeading"]//text()').get(),
            #'content': response.xpath('//div[@id="bodyContent"]').get()
            'content': self.preprocess_text(response)
        }