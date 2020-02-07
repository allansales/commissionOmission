import scrapy
import re

class AuthorSpider(scrapy.Spider):
    name = 'wiki'

    conservapedia_urls = ["https://www.conservapedia.com/Capital_punishment","https://www.conservapedia.com/Gun#Gun_control","https://www.conservapedia.com/Marijuana",
                          "https://www.conservapedia.com/ACLU","https://www.conservapedia.com/Euthanasia","https://www.conservapedia.com/Abortion",
                          "https://www.conservapedia.com/ObamaCare","https://www.conservapedia.com/Climate_change","https://www.conservapedia.com/Network_neutrality",
                          "https://www.conservapedia.com/Genetically_modified_organism","https://www.conservapedia.com/Corporal_punishment","https://www.conservapedia.com/School_vouchers",
                          "https://www.conservapedia.com/Same-sex_marriage","https://www.conservapedia.com/Prostitution",
                          "https://www.conservapedia.com/Video_game#Arguments_against_video_game_usage","https://www.conservapedia.com/Minimum_wage",
                          "https://www.conservapedia.com/Iraq_War","https://www.conservapedia.com/Illegal_immigration"]
    rationalwiki_urls = ["https://rationalwiki.org/wiki/Capital_punishment","https://rationalwiki.org/wiki/Gun_control#Common_arguments_against_gun_control",
                         "https://rationalwiki.org/wiki/Cannabis","https://rationalwiki.org/wiki/American_Civil_Liberties_Union",
                         "https://rationalwiki.org/wiki/Euthanasia","https://rationalwiki.org/wiki/Abortion","https://rationalwiki.org/wiki/Affordable_Care_Act",
                         "https://rationalwiki.org/wiki/Global_warming","https://rationalwiki.org/wiki/Net_neutrality","https://rationalwiki.org/wiki/Genetically_modified_food",
                         "https://rationalwiki.org/wiki/Corporal_punishment","https://rationalwiki.org/wiki/School_vouchers","https://rationalwiki.org/wiki/Same-sex_marriage",
                         "https://rationalwiki.org/wiki/Prostitution","https://rationalwiki.org/wiki/Video_game#Violence","https://rationalwiki.org/wiki/Minimum_wage",
                         "https://rationalwiki.org/wiki/Iraq_War","https://rationalwiki.org/wiki/Illegal_immigration"]

    topic_urls = ["Death Penalty", "Gun Control", "Marijuana", "ACLU", "Euthanasia", "Abortion", "Health Care Form", "Climate Change", "Net Neutrality", "GMOs",
                  "Corporal Punishment", "School Vouchers", "Gay Marriage", "Prostitution", "Video Games", "Minimum Wage", "Iraq War", "Immigration"]

    conservapedia_stances = ["Pro","Con","Con","Con","Con","Con","Con","Con-","Con","Con*","Con","Con*","Con","Con","Con-","Con","Pro","Con-"]
    rationalwiki_stances = ["Con","Pro","Pro","Pro","Pro*","Pro","Pro*","Pro-","Pro","Pro*","Con","Pro*","Pro","Pro*","Pro-","Pro*","Con","Pro-"]

    CONSERVAPEDIA = "conservapedia"

    #* cannot say that they are pro/con the topic. They either can be partially pro and con or we could not identify their stance
    #- do not address specifically the topic. e.g., The climate change discussion in procon.org is about who is guilty for the fact while in conservapedia and rationalwiki they argue pro/con the existance of climate change

    start_urls = conservapedia_urls + rationalwiki_urls

    def preprocess_text(self, response):

        #str = response.xpath('//div[@class="mw-content-ltr"]/*[not(@class="toc")]').get()
        str = response.xpath('//div[@class="mw-content-ltr"]').get()

        # remove tags
        tags_reg = re.compile('<.*?>')
        str = re.sub(tags_reg, '', str)

        # replace multiple \n by one
        str = re.sub('\n+','\n',str).strip()

        # remove brackets texts. e.g., [1], [edit], [cite] or [citation NOT needed]
        bracket_reg = re.compile('\[\w+\s*\w*\s*\w*\]')
        str = re.sub(bracket_reg, '', str)

        # split text by paragraph
        paragraphs = str.split("\n")

        # delete text after the "See Also" section, "Further reading" or "References"
        if "See also" in paragraphs:
            idx = paragraphs.index("See also")
            paragraphs = paragraphs[:idx]

        if "Further reading" in paragraphs:
            idx = paragraphs.index("Further reading")
            paragraphs = paragraphs[:idx]

        if "References" in paragraphs:
            idx = paragraphs.index("References")
            paragraphs = paragraphs[:idx]

        return paragraphs

    def get_idx(self, response, source):
        url = response.request.url

        urls = self.rationalwiki_urls
        if source == self.CONSERVAPEDIA:
            urls = self.conservapedia_urls

        idx = urls.index(url)
        return idx

    def get_topic(self, idx):
        return self.topic_urls[idx]

    def get_stance(self, idx, source):
        stances = self.rationalwiki_stances
        if source == self.CONSERVAPEDIA:
            stances = self.conservapedia_stances
        return stances[idx]

    def get_source(self, response):
        if "wikipedia" in response.request.url:
            return "wikipedia"

        if "rationalwiki" in response.request.url:
            return "rationalwiki"

        if "conservapedia" in response.request.url:
            return "conservapedia"

    def parse(self, response):
        source = self.get_source(response)
        idx = self.get_idx(response, source)
        yield {
            'url': response.request.url,
            'source': source,
            'topic': self.get_topic(idx),
            'stance': self.get_stance(idx, source),
            'title': response.xpath('//*[@id="firstHeading"]//text()').get(),
            #'content': response.xpath('//div[@id="bodyContent"]').get()
            'content': self.preprocess_text(response)
        }