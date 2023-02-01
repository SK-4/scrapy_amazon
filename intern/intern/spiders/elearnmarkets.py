import scrapy
import regex as re
import json
import pandas as pd
from dateutil.relativedelta import relativedelta
from datetime import date, datetime
import requests
import numpy as np
pd.options.mode.use_inf_as_na=True

class CourseScraper(scrapy.Spider):
    name = 'elearnmarkets'

    df_coupons = pd.DataFrame(columns=['Link','Discount Percentage', 'Discount Price', 'Discount Price Currency', 'Coupon Code', 'Learn Type',
                'Applicability', 'Discount Type', 'Course Specific', 'Course Link', 'Instruction Type', 'User Type',               # New User/ All Users
                'Category', 'Skills', 'Card', 'Validity', 'Price Condition', 'Price Limit', 'Condition', 'Description'])

    def start_requests(self):
        return [scrapy.FormRequest('https://www.grabon.in/elearnmarkets-coupons/', 
                                    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0'},
                                    callback=self.parse_grabon)]

    def parse_grabon(self, response):
        coupon_container = response.xpath('//ul[@class="gmc-list list-unstyled"]/li')
        for coupons in coupon_container:
            availableOffers = {
                'Link': '',
                'Discount Percentage' : '', 
                'Discount Price' : '',
                'Discount Price Currency' : '',
                'Coupon Code' : '',	
                'Learn Type' : '',
                'Applicability' : '',
                'Discount Type' : '',
                'Course Specific' : '',
                'Course Link': '',
                'Instruction Type' : '',
                'User Type' : '',               # New User/ All Users
                'Category': '',
                'Skills' : '',	
                'Card' : '',
                'Validity' : '',                # Expiry Date
                'Price Condition' : '',
                'Price Limit' : '',
                'Condition' : '',
                'Description': ''
            }

            code = coupons.xpath('./div/@data-cid').get()

            availableOffers['Link'] = f'https://www.grabon.in/coupon-codes/{code}/'

            data = (requests.get(availableOffers['Link'])).text

            availableOffers['Coupon Code'] = re.compile('code">(.+?)</p').findall(data)[0]

            desc = coupons.xpath('.//div[@class="gcbr go-cpn-show go-cpy"]/p/text()').get()

            availableOffers['Description'] = desc

            if re.search('(100%|Free Trial|Scholarship)',desc):
                continue
            else:
                if re.search("d{1,}%", desc):
                    availableOffers['Discount Percentage'] = re.search("\d{1,}%", desc)[0]
                elif re.search("\$\d{1,}", desc):
                    availableOffers['Discount Price'] = re.search("$\d{1,}", desc)[0]
                else:
                    continue

                if re.search("All Coding Ninjas Courses|On Courses|All Online Courses",desc, re.IGNORECASE):
                    availableOffers['Applicability'] = 'Sitewide'

                elif re.search("(off \(certifications\))| (.* or more certification)", desc, re.IGNORECASE):
                    availableOffers['Applicability'] = 'Learn Type'
                    availableOffers['Learn Type'] = 'Certification'

                elif re.search("membership|subscription",desc,re.IGNORECASE):
                    availableOffers['Applicability'] = 'Subscription'

                elif re.search("(Master\'s)|(Post Grad)", desc, re.IGNORECASE):
                    availableOffers['Applicability'] = "Learn Type"
                    availableOffers['Learn Type'] = 'Masters'

                else:
                    if re.search("(Live|Instructor).*? Training", desc,re.IGNORECASE):
                        if re.search("certified|certification", desc, re.IGNORECASE):
                            availableOffers['Applicability'] = 'Course Specific'
                            course_specific = re.compile('On(.+?)Course').findall(desc)[0]
                            availableOffers['Course Specific'] = course_specific
                        else:
                            availableOffers['Applicability'] = 'Instruction Type'
                    else:
                        if re.search("(certification|certified|course|Program)", desc, re.IGNORECASE):
                            availableOffers['Applicability'] = 'Course Specific'
                            course_specific = re.compile('On(.+?)Course').findall(desc)
                            availableOffers['Course Specific'] = course_specific[0]
                        else:
                            availableOffers['Applicability'] = 'Category'
                            category_ = re.compile('On(.+?)Course').findall(desc)
                            category_1 = re.compile('li>Applicable(.+?)</li').findall(data)
                            if len(category_)>0:
                                availableOffers['Category'] = category_[0]
                            elif len(category_1)>0:
                                availableOffers['Category'] = re.compile('m">(.+?)</span').findall(category_1[0])[0]
                            elif len(category_)==0:
                                availableOffers['Category'] = desc.split(':')[0]
                            else:
                                availableOffers['Category'] = 'None'

                    availableOffers['Learn Type'] = 'Certification'

                if re.search("(Live|Instructor)?.*Training",desc, re.IGNORECASE):
                    availableOffers['Instruction Type'] = 'Instructor Paced'
                else:
                    availableOffers['Instruction Type'] = 'Self Paced'
                
                if re.search("Up To", desc, re.IGNORECASE):
                    availableOffers['Discount Type'] = 'Up To'
                else:
                    availableOffers['Discount Type'] = 'Flat'

                if availableOffers['Applicability'] != 'Subscription' and availableOffers['Applicability'] != 'Sitewide':
                    availableOffers['Learn Type'] = 'Certification'
                
                if re.search("(One|Two|Three|Four|Five|Six|\d) or more (orders|purchases|courses|certifications)?",desc,re.IGNORECASE):
                    availableOffers['Condition'] = re.search("(One|Two|Three|Four|Five|Six|\d) or more (orders|purchases|courses|certifications)?",desc,re.IGNORECASE)[0]

                self.df_coupons = self.df_coupons.append(availableOffers,ignore_index = True)
        yield scrapy.Request('https://zifup.com/store/elearnmarkets/', self.parse_zifup, headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0'})
    
    def parse_zifup(self, response):
        couponcontainer = response.xpath('//div[@class="flex flex-col justify-between h-full zf-cpn"]')
        for coupons in couponcontainer:
            availableOffers = {
                'Link': '',
                'Discount Percentage' : '', 
                'Discount Price' : '',
                'Discount Price Currency' : '',
                'Coupon Code' : '',	
                'Learn Type' : '',
                'Applicability' : '',
                'Discount Type' : '',
                'Course Specific' : '',
                'Course Link': '',
                'Instruction Type' : '',
                'User Type' : '',               # New User/ All Users
                'Category': '',
                'Skills' : '',	
                'Card' : '',
                'Validity' : '',                # Expiry Date
                'Price Condition' : '',
                'Price Limit' : '',
                'Condition' : '',
                'Description': ''
            }

            link_code = coupons.xpath('./div[@itemprop="offers"]/@id').get()

            # availableOffers['Link'] = response.url + '#' + link_code

            code = requests.get('https://zifup.com/store/elearnmarkets/').text
            availableOffers['Coupon Code'] = re.compile(f'<p id="{link_code}-code" class="flex-1 text-center truncate text-sm select-none">(.+?)</p>').findall(code)

            desc = coupons.xpath('./div/div/h3[@class="zf-coupon-title break-words text-base font-medium text-gray-900 overflow-y-hidden mb-3"]/text()').get()
            availableOffers['Description'] = desc

            print(f'Description {availableOffers["Description"]}')
            print(f'Link - {link_code}')
            print(f'Coupon Code {availableOffers["Coupon Code"]}')

            # if re.search('(100%|Free Trial|Scholarship)',desc):
            #     continue
            # else:
            #     if re.search("\d{1,}%", desc):
            #         availableOffers['Discount Percentage'] = re.search("\d{1,}%", desc)[0]
            #     elif re.search("\d{1,}", desc):
            #         availableOffers['Discount Price'] = re.search("[0-9]+", desc)[0]
            #         availableOffers['Discount Price Currency'] = "INR"

            #     if re.search("All Coding Ninjas Courses|On Courses|All Online Courses",desc, re.IGNORECASE):
            #         availableOffers['Applicability'] = 'Sitewide'

            #     elif re.search("(off \(certifications\))| (.* or more certification)", desc, re.IGNORECASE):
            #         availableOffers['Applicability'] = 'Learn Type'
            #         availableOffers['Learn Type'] = 'Certification'

            #     elif re.search("membership|subscription",desc,re.IGNORECASE):
            #         availableOffers['Applicability'] = 'Subscription'

            #     elif re.search("(Master\'s)|(Post Grad)", desc, re.IGNORECASE):
            #         availableOffers['Applicability'] = "Learn Type"
            #         availableOffers['Learn Type'] = 'Masters'

            #     else:
            #         if re.search("(Live|Instructor).*? Training", desc,re.IGNORECASE):
            #             if re.search("certified|certification", desc, re.IGNORECASE):
            #                 availableOffers['Applicability'] = 'Course Specific'
            #                 availableOffers['Course Specific'] = desc.split('on')[-1]
            #             else:
            #                 availableOffers['Applicability'] = 'Instruction Type'
            #         else:
            #             if re.search("(certification|certified|course|Program)", desc, re.IGNORECASE):
            #                 availableOffers['Applicability'] = 'Course Specific'
            #                 availableOffers['Course Specific'] = desc.split('on')[-1]

            #             else:
            #                 availableOffers['Applicability'] = 'Category'
            #                 availableOffers['Category'] = desc.split('on')[-1]
            #             availableOffers['Learn Type'] = 'Certification'

            #     if re.search("(Live|Instructor)?.*Training",desc, re.IGNORECASE):
            #         availableOffers['Instruction Type'] = 'Instructor Paced'
            #     else:
            #         availableOffers['Instruction Type'] = 'Self Paced'
                
            #     if re.search("Up To", desc, re.IGNORECASE):
            #         availableOffers['Discount Type'] = 'Up To'
            #     else:
            #         availableOffers['Discount Type'] = 'Flat'

            #     if availableOffers['Applicability'] != 'Subscription' and availableOffers['Applicability'] != 'Sitewide':
            #         availableOffers['Learn Type'] = 'Certification'
                
            #     if re.search("(One|Two|Three|Four|Five|Six|\d) or more (orders|purchases|courses|certifications)?",desc,re.IGNORECASE):
            #         availableOffers['Condition'] = re.search("(One|Two|Three|Four|Five|Six|\d) or more (orders|purchases|courses|certifications)?",desc,re.IGNORECASE)[0]

                # self.df_coupons = self.df_coupons.append(availableOffers,ignore_index = True)

            yield scrapy.Request('https://www.couponzguru.com/elearnmarkets-coupons/', self.parse_couponsguru, headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0'})
    
    def parse_couponsguru(self, response):
        couponcontainer = response.xpath('//div[@class="coupon-list"]')
        for coupons in couponcontainer:
            availableOffers = {
                'Link': '',
                'Discount Percentage' : '', 
                'Discount Price' : '',
                'Discount Price Currency' : '',
                'Coupon Code' : '',	
                'Learn Type' : '',
                'Applicability' : '',
                'Discount Type' : '',
                'Course Specific' : '',
                'Course Link': '',
                'Instruction Type' : '',
                'User Type' : '',               # New User/ All Users
                'Category': '',
                'Skills' : '',	
                'Card' : '',
                'Validity' : '',                # Expiry Date
                'Price Condition' : '',
                'Price Limit' : '',
                'Condition' : '',
                'Description': ''
            }
            code = response.xpath('./h3/@id').get()

            link_code = response.url + '?c=' + code.split('-')[1] #https://www.couponzguru.com/elearnmarkets-coupons/ #https://www.couponzguru.com/elearnmarkets-coupons/?c=788290

            # availableOffers['Link'] = response.url + '#' + link_code

            code = requests.get('https://www.couponzguru.com/elearnmarkets-coupons/?c={code.split('-')[1]}').text
            availableOffers['Coupon Code'] = re.compile(f'<p id="{link_code}-code" class="flex-1 text-center truncate text-sm select-none">(.+?)</p>').findall(code)

            desc = coupons.xpath('./h3//a[@rel="nofollow"]/text()').get()
            availableOffers['Description'] = desc

            print(f'Description {availableOffers["Description"]}')
            print(f'Link - {link_code}')
            print(f'Coupon Code {availableOffers["Coupon Code"]}')

        #     if re.search('(100%|Free Trial|Scholarship)',desc):
        #         continue
        #     else:
        #         if re.search("\d{1,}%", desc):
        #             availableOffers['Discount Percentage'] = re.search("\d{1,}%", desc)[0]
        #         elif re.search("\d{1,}", desc):
        #             availableOffers['Discount Price'] = re.search("[0-9]+", desc)[0]
        #             availableOffers['Discount Price Currency'] = "INR"

        #         if re.search("All Coding Ninjas Courses|On Courses|All Online Courses",desc, re.IGNORECASE):
        #             availableOffers['Applicability'] = 'Sitewide'

        #         elif re.search("(off \(certifications\))| (.* or more certification)", desc, re.IGNORECASE):
        #             availableOffers['Applicability'] = 'Learn Type'
        #             availableOffers['Learn Type'] = 'Certification'

        #         elif re.search("membership|subscription",desc,re.IGNORECASE):
        #             availableOffers['Applicability'] = 'Subscription'

        #         elif re.search("(Master\'s)|(Post Grad)", desc, re.IGNORECASE):
        #             availableOffers['Applicability'] = "Learn Type"
        #             availableOffers['Learn Type'] = 'Masters'

        #         else:
        #             if re.search("(Live|Instructor).*? Training", desc,re.IGNORECASE):
        #                 if re.search("certified|certification", desc, re.IGNORECASE):
        #                     availableOffers['Applicability'] = 'Course Specific'
        #                     availableOffers['Course Specific'] = desc.split('on')[-1]
        #                 else:
        #                     availableOffers['Applicability'] = 'Instruction Type'
        #             else:
        #                 if re.search("(certification|certified|course|Program)", desc, re.IGNORECASE):
        #                     availableOffers['Applicability'] = 'Course Specific'
        #                     availableOffers['Course Specific'] = desc.split('on')[-1]

        #                 else:
        #                     availableOffers['Applicability'] = 'Category'
        #                     availableOffers['Category'] = desc.split('on')[-1]
        #                 availableOffers['Learn Type'] = 'Certification'

        #         if re.search("(Live|Instructor)?.*Training",desc, re.IGNORECASE):
        #             availableOffers['Instruction Type'] = 'Instructor Paced'
        #         else:
        #             availableOffers['Instruction Type'] = 'Self Paced'
                
        #         if re.search("Up To", desc, re.IGNORECASE):
        #             availableOffers['Discount Type'] = 'Up To'
        #         else:
        #             availableOffers['Discount Type'] = 'Flat'

        #         if availableOffers['Applicability'] != 'Subscription' and availableOffers['Applicability'] != 'Sitewide':
        #             availableOffers['Learn Type'] = 'Certification'
                
        #         if re.search("(One|Two|Three|Four|Five|Six|\d) or more (orders|purchases|courses|certifications)?",desc,re.IGNORECASE):
        #             availableOffers['Condition'] = re.search("(One|Two|Three|Four|Five|Six|\d) or more (orders|purchases|courses|certifications)?",desc,re.IGNORECASE)[0]

        #         self.df_coupons = self.df_coupons.append(availableOffers,ignore_index = True)

        # self.df_coupons.drop_duplicates(subset=['Discount Percentage', 'Coupon Code','Learn Type', 'Applicability', 'Discount Type', 'Course Specific'],inplace=True, ignore_index=True)
        # self.df_coupons = self.df_coupons.sort_values(by=['Discount Percentage'], ascending=False, ignore_index=True)
        # yield self.df_coupons.to_csv("elearnmarket.csv",sep=",")


import scrapy
import regex as re
import json
import pandas as pd
from dateutil.relativedelta import relativedelta
from datetime import date, datetime
import requests
import numpy as np
pd.options.mode.use_inf_as_na=True

class CourseScraper(scrapy.Spider):
    name = 'elearnmarkets'

    df_coupons = pd.DataFrame(columns=['Link','Discount Percentage', 'Discount Price', 'Discount Price Currency', 'Coupon Code', 'Learn Type',
                'Applicability', 'Discount Type', 'Course Specific', 'Course Link', 'Instruction Type', 'User Type',               # New User/ All Users
                'Category', 'Skills', 'Card', 'Validity', 'Price Condition', 'Price Limit', 'Condition', 'Description'])

    def start_requests(self):
        return [scrapy.FormRequest('https://www.grabon.in/elearnmarkets-coupons/', 
                                    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0'},
                                    callback=self.parse_grabon)]

    def parse_grabon(self, response):
        coupon_container = response.xpath('//ul[@class="gmc-list list-unstyled"]/li')
        for coupons in coupon_container:
            availableOffers = {
                'Link': '',
                'Discount Percentage' : '', 
                'Discount Price' : '',
                'Discount Price Currency' : '',
                'Coupon Code' : '',	
                'Learn Type' : '',
                'Applicability' : '',
                'Discount Type' : '',
                'Course Specific' : '',
                'Course Link': '',
                'Instruction Type' : '',
                'User Type' : '',               # New User/ All Users
                'Category': '',
                'Skills' : '',	
                'Card' : '',
                'Validity' : '',                # Expiry Date
                'Price Condition' : '',
                'Price Limit' : '',
                'Condition' : '',
                'Description': ''
            }

            code = coupons.xpath('./div/@data-cid').get()

            availableOffers['Link'] = f'https://www.grabon.in/coupon-codes/{code}/'

            data = (requests.get(availableOffers['Link'])).text

            availableOffers['Coupon Code'] = re.compile('code">(.+?)</p').findall(data)[0]

            desc = coupons.xpath('.//div[@class="gcbr go-cpn-show go-cpy"]/p/text()').get()

            availableOffers['Description'] = desc
            print(desc)
    #         if re.search('(100%|Free Trial|Scholarship)',desc):
    #             continue
    #         else:
    #             if re.search("\d{1,}%", desc):
    #                 availableOffers['Discount Percentage'] = re.search("\d{1,}%", desc)[0]
    #             elif re.search("\$\d{1,}", desc):
    #                 availableOffers['Discount Price'] = re.search("$\d{1,}", desc)[0]
    #             else:
    #                 continue

    #             if re.search("All Coding Ninjas Courses|On Courses|All Online Courses",desc, re.IGNORECASE):
    #                 availableOffers['Applicability'] = 'Sitewide'

    #             elif re.search("(off \(certifications\))| (.* or more certification)", desc, re.IGNORECASE):
    #                 availableOffers['Applicability'] = 'Learn Type'
    #                 availableOffers['Learn Type'] = 'Certification'

    #             elif re.search("membership|subscription",desc,re.IGNORECASE):
    #                 availableOffers['Applicability'] = 'Subscription'

    #             elif re.search("(Master\'s)|(Post Grad)", desc, re.IGNORECASE):
    #                 availableOffers['Applicability'] = "Learn Type"
    #                 availableOffers['Learn Type'] = 'Masters'

    #             else:
    #                 if re.search("(Live|Instructor).*? Training", desc,re.IGNORECASE):
    #                     if re.search("certified|certification", desc, re.IGNORECASE):
    #                         availableOffers['Applicability'] = 'Course Specific'
    #                         course_specific = re.compile('On(.+?)Course').findall(desc)[0]
    #                         availableOffers['Course Specific'] = course_specific
    #                     else:
    #                         availableOffers['Applicability'] = 'Instruction Type'
    #                 else:
    #                     if re.search("(certification|certified|course|Program)", desc, re.IGNORECASE):
    #                         availableOffers['Applicability'] = 'Course Specific'
    #                         course_specific = re.compile('On(.+?)Course').findall(desc)
    #                         availableOffers['Course Specific'] = course_specific[0]
    #                     else:
    #                         availableOffers['Applicability'] = 'Category'
    #                         category_ = re.compile('On(.+?)Course').findall(desc)
    #                         category_1 = re.compile('li>Applicable(.+?)</li').findall(data)
    #                         if len(category_)>0:
    #                             availableOffers['Category'] = category_[0]
    #                         elif len(category_1)>0:
    #                             availableOffers['Category'] = re.compile('m">(.+?)</span').findall(category_1[0])[0]
    #                         elif len(category_)==0:
    #                             availableOffers['Category'] = desc.split(':')[0]
    #                         else:
    #                             availableOffers['Category'] = 'None'

    #                 availableOffers['Learn Type'] = 'Certification'

    #             if re.search("(Live|Instructor)?.*Training",desc, re.IGNORECASE):
    #                 availableOffers['Instruction Type'] = 'Instructor Paced'
    #             else:
    #                 availableOffers['Instruction Type'] = 'Self Paced'
                
    #             if re.search("Up To", desc, re.IGNORECASE):
    #                 availableOffers['Discount Type'] = 'Up To'
    #             else:
    #                 availableOffers['Discount Type'] = 'Flat'

    #             if availableOffers['Applicability'] != 'Subscription' and availableOffers['Applicability'] != 'Sitewide':
    #                 availableOffers['Learn Type'] = 'Certification'
                
    #             if re.search("(One|Two|Three|Four|Five|Six|\d) or more (orders|purchases|courses|certifications)?",desc,re.IGNORECASE):
    #                 availableOffers['Condition'] = re.search("(One|Two|Three|Four|Five|Six|\d) or more (orders|purchases|courses|certifications)?",desc,re.IGNORECASE)[0]

    #             self.df_coupons = self.df_coupons.append(availableOffers,ignore_index = True)
    #     yield scrapy.Request('https://www.elearnmarkets.com/coupons', self.parse_elearnmarkets, headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0'})
    
    # def parse_elearnmarkets(self, response):
    #     couponcontainer = response.xpath('//div[@class="coupons_card_box"]')
    #     for coupons in couponcontainer:
    #         availableOffers = {
    #             'Link': '',
    #             'Discount Percentage' : '', 
    #             'Discount Price' : '',
    #             'Discount Price Currency' : '',
    #             'Coupon Code' : '',	
    #             'Learn Type' : '',
    #             'Applicability' : '',
    #             'Discount Type' : '',
    #             'Course Specific' : '',
    #             'Course Link': '',
    #             'Instruction Type' : '',
    #             'User Type' : '',               # New User/ All Users
    #             'Category': '',
    #             'Skills' : '',	
    #             'Card' : '',
    #             'Validity' : '',                # Expiry Date
    #             'Price Condition' : '',
    #             'Price Limit' : '',
    #             'Condition' : '',
    #             'Description': ''
    #         }

    #         availableOffers['Link'] = coupons.xpath('./p[@class="mt-3"]/a/@href').get()

    #         availableOffers['Coupon Code'] = coupons.xpath('./p[@class="coupon_box mb-3"]/span/text()').get()
    #         desc = coupons.xpath('./p[@class="description"]/text()').get()
    #         availableOffers['Description'] = desc

    #         if re.search('(100%|Free Trial|Scholarship)',desc):
    #             continue
    #         else:
    #             if re.search("\d{1,}%", desc):
    #                 availableOffers['Discount Percentage'] = re.search("\d{1,}%", desc)[0]
    #             elif re.search("\d{1,}", desc):
    #                 availableOffers['Discount Price'] = re.search("[0-9]+", desc)[0]
    #                 availableOffers['Discount Price Currency'] = "INR"

    #             if re.search("All Coding Ninjas Courses|On Courses|All Online Courses",desc, re.IGNORECASE):
    #                 availableOffers['Applicability'] = 'Sitewide'

    #             elif re.search("(off \(certifications\))| (.* or more certification)", desc, re.IGNORECASE):
    #                 availableOffers['Applicability'] = 'Learn Type'
    #                 availableOffers['Learn Type'] = 'Certification'

    #             elif re.search("membership|subscription",desc,re.IGNORECASE):
    #                 availableOffers['Applicability'] = 'Subscription'

    #             elif re.search("(Master\'s)|(Post Grad)", desc, re.IGNORECASE):
    #                 availableOffers['Applicability'] = "Learn Type"
    #                 availableOffers['Learn Type'] = 'Masters'

    #             else:
    #                 if re.search("(Live|Instructor).*? Training", desc,re.IGNORECASE):
    #                     if re.search("certified|certification", desc, re.IGNORECASE):
    #                         availableOffers['Applicability'] = 'Course Specific'
    #                         availableOffers['Course Specific'] = desc.split('on')[-1]
    #                     else:
    #                         availableOffers['Applicability'] = 'Instruction Type'
    #                 else:
    #                     if re.search("(certification|certified|course|Program)", desc, re.IGNORECASE):
    #                         availableOffers['Applicability'] = 'Course Specific'
    #                         availableOffers['Course Specific'] = desc.split('on')[-1]

    #                     else:
    #                         availableOffers['Applicability'] = 'Category'
    #                         availableOffers['Category'] = desc.split('on')[-1]
    #                     availableOffers['Learn Type'] = 'Certification'

    #             if re.search("(Live|Instructor)?.*Training",desc, re.IGNORECASE):
    #                 availableOffers['Instruction Type'] = 'Instructor Paced'
    #             else:
    #                 availableOffers['Instruction Type'] = 'Self Paced'
                
    #             if re.search("Up To", desc, re.IGNORECASE):
    #                 availableOffers['Discount Type'] = 'Up To'
    #             else:
    #                 availableOffers['Discount Type'] = 'Flat'

    #             if availableOffers['Applicability'] != 'Subscription' and availableOffers['Applicability'] != 'Sitewide':
    #                 availableOffers['Learn Type'] = 'Certification'
                
    #             if re.search("(One|Two|Three|Four|Five|Six|\d) or more (orders|purchases|courses|certifications)?",desc,re.IGNORECASE):
    #                 availableOffers['Condition'] = re.search("(One|Two|Three|Four|Five|Six|\d) or more (orders|purchases|courses|certifications)?",desc,re.IGNORECASE)[0]

    #             self.df_coupons = self.df_coupons.append(availableOffers,ignore_index = True)

    #     self.df_coupons.drop_duplicates(subset=['Discount Percentage', 'Coupon Code','Learn Type', 'Applicability', 'Discount Type', 'Course Specific'],inplace=True, ignore_index=True)
    #     self.df_coupons = self.df_coupons.sort_values(by=['Discount Percentage'], ascending=False, ignore_index=True)
    #     yield self.df_coupons.to_csv("elearnmarket.csv",sep=",")