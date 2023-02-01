import scrapy
import re
import json
import pandas as pd
from dateutil.relativedelta import relativedelta
from datetime import date, datetime
import requests
import numpy as np
pd.options.mode.use_inf_as_na=True

class CourseScraper(scrapy.Spider):
    name = 'CodingNinjaSpider'

    df_coupons = pd.DataFrame(columns=['Link','Discount Percentage', 'Discount Price', 'Discount Price Currency', 'Coupon Code', 'Learn Type',
                'Applicability', 'Discount Type', 'Course Specific', 'Course Link', 'Instruction Type', 'User Type',               # New User/ All Users
                'Category', 'Skills', 'Card', 'Validity', 'Price Condition', 'Price Limit', 'Condition', 'Description'])

    def start_requests(self):
        return [scrapy.FormRequest('https://www.ninjasoffers.com/', 
                                    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0'},
                                    callback=self.parse_ninja)]

    def parse_ninja(self, response):
        couponcontainer = response.xpath('//div[@class="listing-item-container"]')
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

            availableOffers['Link'] = 'https://www.codingninjas.com/?referralCode=' + coupons.xpath('./div/div/p[@class="deal-coupon-code"]/text()').get()
            
            availableOffers['Coupon Code'] = coupons.xpath('./div/div/p[@class="deal-coupon-code"]/text()').get()
            
            desc = (coupons.xpath('./div//h5[@class="deal-title"]/text()').get()).strip()
            
            availableOffers['Description'] = desc

            if re.search('(100%|Free Trial|Scholarship)',desc):
                continue
            else:
                if re.search("\d{1,}%", desc):
                    availableOffers['Discount Percentage'] = re.search("\d{1,}%", desc)[0]
                elif re.search("\$\d{1,}", desc):
                    availableOffers['Discount Price'] = re.search("$\d{1,}", desc)[0]

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
                            
                            availableOffers['Course Specific'] = re.sub("\)$", "" ,re.sub("(off|OFF|Off) (\()?","",re.search("off.*\)",desc,re.IGNORECASE)[0]))
                        else:
                            availableOffers['Applicability'] = 'Instruction Type'
                    else:
                        if re.search("(certification|certified|course|Program)", desc, re.IGNORECASE):
                            availableOffers['Applicability'] = 'Course Specific'
                            # availableOffers['Course Specific'] = re.sub("\)$", "" ,re.sub("(off|OFF|Off) (\()?","",re.search("off.*\)",desc,re.IGNORECASE)[0]))
                        else:
                            availableOffers['Applicability'] = 'Category'
                            # availableOffers['Category'] = re.sub("\)$", "" ,re.sub("(off|OFF|Off) (\()?","",re.search("off.*(\)|courses|certifications)",desc,re.IGNORECASE)[0]))
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
        yield scrapy.Request('https://www.grabon.in/codingninjas-coupons/', self.parse_grabon, headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0'})

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
                if re.search("\d{1,}%", desc):
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
                                availableOffers['Category'] = desc.split('-')[0]
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
        
        self.df_coupons.drop_duplicates(subset=['Discount Percentage', 'Coupon Code','Learn Type', 'Applicability', 'Discount Type', 'Course Specific'],inplace=True, ignore_index=True)
        self.df_coupons = self.df_coupons.sort_values(by=['Discount Percentage'], ascending=False, ignore_index=True)
        yield self.df_coupons.to_csv("codingninjas.csv",sep=",")