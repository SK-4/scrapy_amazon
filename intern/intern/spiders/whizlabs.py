import scrapy
import re
import json
import pandas as pd
from xml.dom import minidom
import requests
from collections import OrderedDict

class CourseScraper(scrapy.Spider):
    name = 'whizlabSpider'
    df_whizlabs_contents = pd.DataFrame(columns=['title','learn_type','description','delivery_method','instruction_type','content_module','languages','subtitle_languages','short Description','accessibilities','display_price','pricing_type','currency','regular_price','sale_price','institute','learning_medium','virtual_labs','capstone_project','personalized_teaching','partner_course_url','faq','what_will_learn','short_description'])
    def start_requests(self):
        global key
        file = pd.read_excel("Whizlabs.xlsx")
        for key in file['Link']:
            yield scrapy.Request(key,callback=self.parse_whizlabs_content)
            
    def parse_whizlabs_content(self,response):
        data = (requests.get(f'{response.url}')).text
        title = re.compile('<title>(.+?)</title').findall(data)[0]
        learn_type = 'certification'
        desc = re.compile('"description":"(.+?)","is').findall(data)[0]
        delivery_method = 'Online'
        instruction_type = 'Instructor Paced'
        description = re.sub(r'\\u(.){4}|\\n|\\r|/li|/p|/ul|ul|li|span|/span', '', desc)

        jsonData = json.loads(re.sub("<\/?script(.*type=\"application\/json\")?>","",response.xpath("//script[@id='__NEXT_DATA__']").get()))
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
        question = re.compile('of (\d+|\d+\+) unique|with (\d+) questions|provide (\d+) newly').findall(description)
        total_questions = 0
        for i in question:
            for j in i:
                if j!='':
                    total_questions = j

        languages = 'English'
        subtitle_languages = 'English'
        short_description = description.split('.')[0]
        accessibilities = 'Desktop,Laptop'
        institute = 'Whizlabs'

        price = re.compile('"inr":"(.+?)"}').findall(data)
        regular_price = price[0]
        sale_price = price[1]
        new_price = []
        for i in price:
            new_price.append(int(float(i)))

        if len(new_price)==4:
            regular_price = new_price[0] + new_price[2]
            sale_price = new_price[1] + new_price[3]

        display_price = False
        if regular_price:
            display_price = True

        pricing_type = 'Paid'
        currency = 'INR'
        learning_medium = 'Hands-On Training'
        virtual_labs = True
        capstone_project = False
        case_based_learning = False
        personalized_teaching = True
        partner_link = response.url

        faq_question = re.compile('question":"(.+?)\?').findall(data)
        faq_answer = re.compile('answer":"(.+?)","').findall(data)
        faq = []
        for i in range(len(faq_question)):
            faq.append(f"{faq_question[i]} | {faq_answer[i]}")
            
        what_will_learn_altered = jsonData["props"]["pageProps"]["pageData"]["other_attributes"]["what_will_learn"]
        what_will_learn = re.sub(r'\\u(.){4}|\\n|\\r|/li|/p|/ul|ul|li|span|/span|<div|class="container-left">| \\r\\n<h2|class="title">|</h2>|<>|</div>| \\r\\n<h2|\\r\\n<>\\r\\n<>|<>\\r\\n<>|', '', what_will_learn_altered)
        short_description = jsonData["props"]["pageProps"]["pageData"]["seo_details"]["short_description"]

        self.df_whizlabs_contents = self.df_whizlabs_contents.append({'title':title,'learn_type':learn_type,'description':description,'delivery_method':delivery_method,'instruction_type':instruction_type,'content_module':content_module,'languages':languages,'subtitle_languages':subtitle_languages,'short Description':short_description,'accessibilities':accessibilities,'display_price':display_price,'pricing_type':pricing_type,'currency':currency,'regular_price':regular_price,'sale_price':sale_price,'institute':institute,'learning_medium':learning_medium,'virtual_labs':virtual_labs,'capstone_project':capstone_project,'personalized_teaching':personalized_teaching,'partner_course_url':partner_link,'faq':faq,'what_will_learn':what_will_learn,'short_description':short_description},ignore_index = True)
        yield self.df_whizlabs_contents.to_excel("whizlabs-contents.xlsx")