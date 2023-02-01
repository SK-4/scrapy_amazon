# import scrapy
# import requests
# import regex as re
# from collections import OrderedDict

# class CareerSpider(scrapy.Spider):
#     name = "aipathshala"
#     allowed_domains = ['aipatasala.com']
#     start_urls = ['https://aipatasala.com/all-courses']

#     def parse(self, response):
#         global link
#         uxls = response.xpath('//div[@class="ant-col ant-col-xs-10 ant-col-sm-8"]//@href').getall()
#         # pattern = re.compile(r'<a\s+(?:[^>]*?\s+)?href="([^"]*)"').findall(f"{uxls}") #Used Regex for extracting href tag but got the alternative
#         for key in uxls:
#             if key not in ("tel: 91-606-22221","mailto: info@aipatasala.com","https://g.page/aipatasala?share"):
#                 link = f'https://aipatasala.com{key}/'
#             yield scrapy.Request(link, callback=self.parse_url)
            
#     def replace_all(text, dic): #For removing unneccessary tags present inside the contents of what_will_you_learn and target_students
#         for i, j in dic.items():
#             text = text.replace(i, j)
#         return text.strip()

#     def parse_url(self,response):
#         title = response.xpath('//h1/text()').extract_first()#Formatted
#         instruction_type = ','.join(response.xpath('//h3[@class="ant-typography fee_category_heading"]/text()').extract())#Formatted
#         self_paced_retail_price = response.xpath('//div[@class="ant-col price"]/text()')[1].get()#Formatted
#         self_paced_discounted_price = response.xpath('//div[@class="ant-col discount_price"]/text()')[1].get()#Formatted
#         online_instructor_led_retail_price = response.xpath('//div[@class="ant-col price"]/text()')[3].get()#formatted
#         online_instructor_led_discounted_price = response.xpath('//div[@class="ant-col discount_price"]/text()')[5].get()#Formatted
#         skill = ' | '.join(response.xpath('//h3[@class="ant-typography course_overview_skill_item"]/text()').getall())#Formatted
#         instructor_name = ' | '.join(response.xpath('//div[@class="instructor_name"]/text()').getall()) #Formatted
#         instructor_experience =  ' | '.join(response.xpath('//h3[@class="ant-typography instructor_exp_desc"]/text()').getall())#Formatted
#         instructor_image = ' | '.join(response.xpath('//img[@class="instructor_avatar"]/@src').getall())#Formatted
#         instructor_linkedin_url = ' | '.join(response.xpath('//div[@class="social_icon"]/a/@href').getall())#Formatted                
#         reviewer_name = ' | '.join(response.xpath('//div[@class="ant-card-meta-title"]/text()').getall()) #Formatted
#         reviewer_position = ' | '.join(response.xpath('//div[@class="ant-card-meta-description"]/text()').getall()) #Formatted
#         chunk = response.xpath('//script/@src')[35].get()
#         res = requests.get('https://aipatasala.com'+f'{chunk}')
#         data_ = res.text
#         what_will_you_learn = []
#         od = OrderedDict([("</li><li>",""), ("</li>",""),("<li>",""),("<b>",""),("\\u2019s",""),("</b>",""),("</b><b>",""),("\\u201c",""),("<br><br>",""),("\\u201d","")])
#         pattern = re.compile(r'answer\":\"([^\"]+)\"*')
#         x = (pattern.findall(f"{data_}"))[1].split('.')
#         for i in x:
#             what_will_you_learn.append(CareerSpider.replace_all(i,od))

#         #   Target_Students_Data
#         target_pattern = (re.compile(r'question\":\"([^\"]+)\"*').findall(f"{data_}"))
#         target_student_question_index = 0
#         for idx, val in enumerate(target_pattern):
#             if val.startswith('Who'):
#                 target_student_question_index = idx
#         target_students = []
#         target = (pattern.findall(f"{data_}"))[target_student_question_index]
#         for i in target.split('.')[1:]:
#             target_students.append(CareerSpider.replace_all(target,od))

#         # FAQ_Question_Data
#         faq_question = ""
#         yes = requests.get(f'{link}')
#         faq_question_value = yes.text

#         # faq_question_idx = 0
#         # for idx, val in enumerate(faq_question_value):
#         #     if val.startswith('What'):
#         #         faq_question_idx = idx

#         faq_question += " | ".join(re.compile(r'name\":\"([^\"]+)\"*').findall(f"{faq_question_value}")[5:-1])
        
#         #FAQ_ANSWER_DATA
#         faq_answer = ""
#         yes = requests.get(f'{link}')
#         faq_answer_value = yes.text

#         # faq_answer_idx = 0
#         # for idx, val in enumerate(faq_question_value):
#         #     if val.startswith('we'):
#         #         faq_answer_idx = idx

#         faq_answer += " | ".join(re.compile(r'text\":\"([^\"]+)\"*').findall(f"{faq_answer_value}")[3:-1])

#         yield{
#             'title':title,
#             'instruction_type':instruction_type,
#             # 'self_paced_retail_price': self_paced_retail_price,
#             # 'self_paced_discounted_price':self_paced_discounted_price,
#             # 'online_instructor_led_retail_price':online_instructor_led_retail_price,
#             # 'online_instructor_led_discounted_price':online_instructor_led_discounted_price,
#             # 'skill': skill,
#             # 'instructor_name':instructor_name,
#             # 'instructor_experience':instructor_experience,
#             # 'instructor_image':instructor_image,
#             # 'instructor_linkedin_url':instructor_linkedin_url,
#             # 'reviewer_name':reviewer_name,
#             # 'reviewer_position':reviewer_position,
#             # 'what_will_you_learn':what_will_you_learn,
#             # 'target_students':target_students,
#             # 'faq_questions':faq_question,
#             # 'faq_answer':faq_answer
#         }
import scrapy
import re
import json
import pandas as pd
from xml.dom import minidom
import requests
from collections import OrderedDict

class CourseScraper(scrapy.Spider):
    name = 'ai'
    df_whizlabs_contents = pd.DataFrame(columns=['Link','Content'])
    def start_requests(self):
        global link
        file = pd.read_excel("Whizlabs.xlsx")
        for key in file['Link']:
            link = key
            yield scrapy.Request(link,  callback=self.parse_whizlabs_content)
        
    def parse_whizlabs_content(self, response):
        jsonData = json.loads(re.sub("<\/?script(.*type=\"application\/json\")?>","",response.xpath("//script[@id='__NEXT_DATA__']").get()))
        # print(jsonData)
        title = jsonData['props']['pageProps']['pageData']['name']
        learn_type = 'Certification'
        description = jsonData['props']['pageProps']['pageData']['description']
        delivery_method = 'Online'
        instructor_lead = jsonData['props']['pageProps']['pageData']['seo_details']['is_instructor_course']
        what_will_learn = jsonData['props']['pageProps']['pageData']['other_attributes']['what_will_learn']
        languages = 'English'
        subtitle_language = 'English'
        accessibilities = 'Desktop,Laptop'
        regular_price = jsonData['props']['pageProps']['pageData']['products'][2]['regular_price']['inr']
        sale_price = jsonData['props']['pageProps']['pageData']['products'][2]['sale_price']['inr']
        display_price = False
        if regular_price:
            display_price = True
        pricing_type = False
        if display_price:
            pricing_type = True
        currency = 'INR'
        institute = 'Whizlabs'
        partner_course_url = link
        learning_medium = 'Hands-On Training'
        if instructor_lead:
            learning_medium = 'Instructor lead'
        virtual_labs = jsonData['props']['pageProps']['pageData']['seo_details']['is_lab']
        if virtual_labs:
            case_based_learning = True
        capstone_project = False
        pageInfo = jsonData["props"]["pageProps"]["pageData"]["detailedInfo"]
        
        root = minidom.Document()
        xml = root.createElement(f'mainmodule')
        root.appendChild(xml)
        i = 1

        if "praticetest_info" in pageInfo:
            if "praticetest_info" in pageInfo:
                practiceTests = pageInfo["praticetest_info"]

                module = root.createElement(f'module{i}')
                i+=1
                heading = root.createElement('heading')
                text = root.createTextNode('Practice Tests')
                heading.appendChild(text)
                module.appendChild(heading)
                
                subHeading = root.createElement('subheading')
                j = 1
                for tests in practiceTests:
                    if 'quiz_name' in tests and tests['quiz_name'] != None:
                        item = root.createElement(f'item{j}')
                        Text = root.createTextNode(tests['quiz_name'])
                        item.appendChild(Text)
                        subHeading.appendChild(item)
                        j += 1
                module.appendChild(subHeading)
                xml.appendChild(module)

        if "onlinecourse_info" in pageInfo:
            if "onlinecourse_info" in pageInfo:
                videoCourses = pageInfo["onlinecourse_info"]

                module = root.createElement(f'module{i}')
                i+=1
                heading = root.createElement('heading')
                text = root.createTextNode('Video Course')
                heading.appendChild(text)
                module.appendChild(heading)

                subHeading = root.createElement('subheading')
                j = 1
                for courses in videoCourses:
                    if 'section_heading' in courses and courses['section_heading'] != None:
                        if re.search("Thank you for your patience.", courses['section_heading']):
                            continue
                        item = root.createElement(f'item{j}')
                        Text = root.createTextNode(courses['section_heading'])
                        item.appendChild(Text)
                        subHeading.appendChild(item)
                        j += 1
                module.appendChild(subHeading)
                xml.appendChild(module)

        if "lab_info" in pageInfo:
            if "lab_info" in pageInfo:
                labs = pageInfo["lab_info"]
                module = root.createElement(f'module{i}')
                i+=1
                heading = root.createElement('heading')
                text = root.createTextNode('Hands-On Labs')
                heading.appendChild(text)
                module.appendChild(heading)
                
                subHeading = root.createElement('subheading')
                j = 1
                for lab in labs:
                    if 'lab_name' in lab and lab['lab_name'] != None:
                        item = root.createElement(f'item{j}')
                        Text = root.createTextNode(lab['lab_name'])
                        item.appendChild(Text)
                        subHeading.appendChild(item)
                        j += 1
                module.appendChild(subHeading)
                xml.appendChild(module)
    
        content_module = root.toprettyxml(indent ="\t")

        yield{
            'title':title,
            'learn type':learn_type,
            'description':description,
            'delivery_method':delivery_method,
            'instruction_type':instructor_lead,
            'what_will_learn':what_will_learn,
            'content_module':content_module,
            'languages':languages,
            'subtitle_language':subtitle_language,
            'accessibilities':accessibilities,
            'learning_medium':learning_medium,
            'regular_price':regular_price,
            'sale_price':sale_price,
            'display_price':display_price,
            'pricing_type':pricing_type,
            'currency':currency,
            'institute':institute,
            'partner_course_url':partner_course_url,
            'capstone_project':capstone_project
        }