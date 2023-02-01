import scrapy

class CareerSpider(scrapy.Spider):
    name = "mental_health"
    allowed_domains = ['screening.mhanational.org']
    start_urls = ['https://screening.mhanational.org/screening-tools/']
    
    def parse(self,response):
        url = response.xpath('(//a[@class="button round block text-left large teal"]/@href)').getall()
        for i in url:
            if i not in ('https://screening.mhanational.org/screening-tools/test-de-depresion/?ref','https://screening.mhanational.org/screening-tools/test-de-ansiedad/?ref'):
                yield scrapy.Request(i, callback=self.parse_question)

    def parse_question(self,response):
        question = response.xpath('//label[@class="gfield_label"]/text()').getall()
        ques = ""
        for i in question:
            if i in ('Age Range','Gender','Enter Gender','Race/Ethnicity','Household Income','Do you live in the United States or another country?','State','What country do you live in?','Zip/Postal Code','Which of the following best describes your sexual orientation?','Sexual Orientation - Other','Trauma - OtherHave you ever received treatment/support for a mental health problem?','Comments','First Name','Name','Last Name','Email','Phone Number (Optional)','CAPTCHA','Phone'):
                pass
            else:
                yield{
                    'question': i
                }
    