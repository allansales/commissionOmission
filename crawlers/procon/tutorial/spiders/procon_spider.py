import scrapy
import re


class AuthorSpider(scrapy.Spider):
	name = 'procon'

	TOP_TEN_EXPR_TXT = "Top 10 Pro & Con Arguments" #identifier for parse_paired_args_by_multi_topics
	PRO_CON_EXPR_TXT = "Pro & Con Arguments" #identifier for parse_unpaired_args_page

	TOP_TEN_EXPR = '//h1[@class="title-newblue"]//text()|//h1[@class="entry-title"]' #XPATH for parse_paired_args_by_multi_topics
	PRO_CON_EXPR = '//*[@class="top-pca"]/text()' # XPATH for parse_unpaired_args_page

	start_urls = ["https://deathpenalty.procon.org/view.resource.php?resourceID=002000","https://gun-control.procon.org/","https://marijuana.procon.org/",
	"https://aclu.procon.org/top-10-pro-con-arguments/","https://euthanasia.procon.org/view.resource.php?resourceID=000126","https://abortion.procon.org/",
	"https://healthcarereform.procon.org/view.resource.php?resourceID=003725","https://climatechange.procon.org/",
	"https://www.procon.org/headline.php?headlineID=005390",
	"https://www.procon.org/headline.php?headlineID=005447","https://www.procon.org/headline.php?headlineID=005350","https://www.procon.org/headline.php?headlineID=005354",
	"https://gaymarriage.procon.org/","https://prostitution.procon.org/view.resource.php?resourceID=000115","https://videogames.procon.org/",
	"https://minimum-wage.procon.org/","https://usiraq.procon.org/view.resource.php?resourceID=000668","https://immigration.procon.org/view.resource.php?resourceID=000842"
	]

	topic_urls = ["Death Penalty", "Gun Control", "Marijuana", "ACLU", "Euthanasia", "Abortion", "Health Care Form", "Climate Change", "Net Neutrality", "GMOs", "Corporal Punishment",
				  "School Vouchers", "Gay Marriage", "Prostitution", "Video Games", "Minimum Wage", "Iraq War", "Immigration"]

	# Get information whether the argument is Pro or Con the subject
	def get_pro_con(self, pro_args, con_args):
		pro = ["Pro "+ str(x) for x in range(1, len(pro_args)+1)]
		con = ["Con "+ str(x) for x in range(1, len(con_args)+1)]
		return pro + con

	def get_topic(self, response):
		url = response.request.url
		idx = self.start_urls.index(url)
		return self.topic_urls[idx]

	# manually remove persistent tags and unwanted strings from text
	def preprocess_text(self, str_array):

		new_str_array = []
		# detect tags
		tags_reg = re.compile('<.*?>')

		# detect pro con string
		procon_reg = re.compile('Pro [\d]+|Con [\d]+')

		# detect citation
		citation_reg = re.compile('\[\d+\]')

		# detect brackets. i.e., [ or ]
		bracket_reg = re.compile('[\[\]]')

		# detect \n
		paragraph_reg = re.compile('\n+')

		# remove signature of text (e.g., the ones contained in https://euthanasia.procon.org/view.resource.php?resourceID=000126)
		# by retrieving only the quoted text

		for string in str_array:
			string = re.sub(tags_reg, '', string)
			string = re.sub(bracket_reg, '', string)
			string = re.sub(citation_reg, '', string)
			string = re.sub(paragraph_reg, ' ', string)
			string = re.sub(procon_reg, '', string, 1).strip()
			print("==================================================")
			print(string)
			print("==================================================")
			if string.startswith('"'):
				string = re.findall('"([^"]*)"', string)[0]
			new_str_array.append(string)
		return new_str_array

	# parse pages with top 10 arguments pro and con a subject
	# e.g., in Death penalty page is shown 10 arguments pro and against the
	# subject, in which the pro and the con arguments are counter points addressing the same topic
	# such as, 1. Morality, 2. Constitutionality, etc
	def parse_paired_args_by_multi_topics(self, response):
		pro_args = response.xpath('//td[@id="newblue-pro-column-2"]').getall()
		con_args = response.xpath('//td[@id="newblue-con-column-2"]').getall()
		topic = response.xpath('//a[@class="newblue-topic-links"]/text()').getall()

		def format_args(args_array, sep):
			fulltext = ' '.join(args_array)
			text_by_args = fulltext.split(sep)[1:]
			return text_by_args

		if (not pro_args) | (not con_args):
			pro_args = response.xpath('//table[@cellpadding="10"]/tbody/tr[position()>1 and position()<last()]//td[position()=1][not(contains(@colspan,2))]/p[contains(@align,"left")]//text()').getall()
			pro_args = format_args(pro_args, "PRO: ")

			con_args = response.xpath('//table[@cellpadding="10"]/tbody/tr[position()>1 and position()<last()]//td[position()=2][not(contains(@colspan,2))]/p[contains(@align,"left")]//text()').getall()
			con_args = format_args(con_args, "CON: ")

			topic = topic = response.xpath('//table[@cellpadding="10"]/tbody/tr[position()>1 and position()<last()]//td[contains(@colspan,2)]//a/text()').getall()

		return {
			'url': response.request.url,
			'topic': self.get_topic(response),
			'pro_con': self.get_pro_con(pro_args, con_args),
			'argument_topic': topic + topic,
			'argument': self.preprocess_text(pro_args) + self.preprocess_text(con_args)
		}

	def parse_paired_args_by_one_topic(self, response):

		pro_args = response.xpath('//td[contains(@style,"WIDTH: 50%; VERTICAL-ALIGN: top; BACKGROUND-IMAGE: none; WORD-SPACING: 0px; BACKGROUND-REPEAT: repeat; BACKGROUND-POSITION: 0% 0%; PADDING-BOTTOM: 5px; PADDING-TOP: 5px; PADDING-LEFT: 5px; LETTER-SPACING: 0px; PADDING-RIGHT: 5px; BACKGROUND-COLOR: rgb(240,249,255)")]|//td[contains(@style,"TEXT-DECORATION: ; WIDTH: 50%; VERTICAL-ALIGN: top; BACKGROUND-IMAGE: none; WORD-SPACING: 0px; BACKGROUND-REPEAT: repeat; BACKGROUND-POSITION: 0% 0%; COLOR: ; PADDING-BOTTOM: 5px; PADDING-TOP: 5px; PADDING-LEFT: 5px; LETTER-SPACING: 0px; PADDING-RIGHT: 5px; BACKGROUND-COLOR: #f0f9ff")]').getall()
		con_args = response.xpath('//td[contains(@style,"WIDTH: 50%; VERTICAL-ALIGN: top; BACKGROUND-IMAGE: none; WORD-SPACING: 0px; BACKGROUND-REPEAT: repeat; BACKGROUND-POSITION: 0% 0%; PADDING-BOTTOM: 5px; PADDING-TOP: 5px; PADDING-LEFT: 5px; LETTER-SPACING: 0px; PADDING-RIGHT: 5px; BACKGROUND-COLOR: rgb(249,241,234)")]|//td[contains(@style,"TEXT-DECORATION: ; WIDTH: 50%; VERTICAL-ALIGN: top; BACKGROUND-IMAGE: none; WORD-SPACING: 0px; BACKGROUND-REPEAT: repeat; BACKGROUND-POSITION: 0% 0%; COLOR: ; PADDING-BOTTOM: 5px; PADDING-TOP: 5px; PADDING-LEFT: 5px; LETTER-SPACING: 0px; PADDING-RIGHT: 5px; BACKGROUND-COLOR: #f9f1ea")]').getall()

		return {
			'url': response.request.url,
			'topic': self.get_topic(response),
			'pro_con': self.get_pro_con(pro_args, con_args),
			'argument': self.preprocess_text(pro_args) + self.preprocess_text(con_args)
		}

	# parse pages without paired topics. In that pages is possible to find
	# distinct number of arguments pro and against the subject. The main
	# characteristic is that the arguments pro and against are not necessarily
	# align to a topic.
	def parse_unpaired_args_page(self, response):
		return {
			'url': response.request.url,
			'topic': self.get_topic(response),
			'pro_con': response.xpath('//div[@class="argument-container"]/blockquote/h3/text()').getall(),
			'argument_summary': response.xpath('//div[@class="argument-container"]/blockquote/h4/text()').getall(),
			'argument': self.preprocess_text(response.xpath('//div[@class="argument-container"]//blockquote').getall())
		}

	def parser_chooser(self, response):

		expr = response.xpath(self.TOP_TEN_EXPR + '|' + self.PRO_CON_EXPR).get()

		if expr is None:
			return self.parse_paired_args_by_one_topic(response)

		if expr == self.TOP_TEN_EXPR_TXT:
			return self.parse_paired_args_by_multi_topics(response)

		if expr == self.PRO_CON_EXPR_TXT:
			return self.parse_unpaired_args_page(response)

	def parse(self, response):
		return self.parser_chooser(response)



