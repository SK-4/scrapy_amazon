import scrapy
import regex as re
import json
import pandas as pd
import requests

class CourseScraper(scrapy.Spider):
    name = 'digitalvidya'
    allowed_domains = ['www.couponbirds.com']
    start_urls = ['https://www.couponbirds.com/codes/digitalvidya.com']

    def parse(self, response):
        couponContainer = response.xpath("//a[@class='overlay']")
        
        for coupons in couponContainer:
            availableOffers = {
                'Discount Percentage' : '', 
                'Discount Price' : '',
                'Coupon Code' : '',	
                'Learn Type' : '',
                'Applicability' : '',
                'Discount Type' : '',
                'Course Specific' : '',
                'Course Link': '',
                'Instruction Type' : '',
                'User Type' : '',               
                'Category': '',
                'Skills' : '',	
                'Card' : '',
                'validity' : '',                
                'Price Condition' : '',
                'Price Limit' : '',
                'Condition' : ''
            }

            desc = ''
            res = requests.get(coupons.xpath('//h2//a/@data-url'))
            availableOffers['Coupon Code'] = res.xpath("//div[@class='input-group mb-3 cp-code']/input/@value").get()
            
            if re.search("\d.*%", desc):
                availableOffers['Discount Percentage'] = re.search("\d.*%", desc)[0]
            elif re.search("$\d.*\d", desc):
                availableOffers['Discount Price'] = re.search("$\d.*\d", desc)[0]
            
            if re.search("(store-wide)|(site-wide)",desc, re.IGNORECASE):
                availableOffers['Applicability'] = 'Sitewide'
            elif re.search("membership",desc,re.IGNORECASE):
                availableOffers['Applicability'] = 'Subscription'
            else:
                availableOffers['Applicability'] = 'Course Specific'
                availableOffers['Course Specific'] = re.search("off.*((at digitalvidya)|(w/Coupon))",desc,re.IGNORECASE)[0].replace("Off ","").replace(" at digitalvidya","").replace(" w/Coupon","")

            if re.search("Expert?.*(Interactive|Instructor)",desc, re.IGNORECASE):
                availableOffers['Instruction Type'] = 'Instructor'
            else:
                availableOffers['Instruction Type'] = 'Self'
            
            if re.search("Up to",desc,re.IGNORECASE):
                availableOffers['Discount Type'] = 'Up to'
            else:
                availableOffers['Discount Type'] = 'Flat'

            if re.search("certified|certification", desc, re.IGNORECASE):
                availableOffers['Learn Type'] = 'Certification'
            
            if re.search("\(Qualifying.*\)",desc,re.IGNORECASE):
                availableOffers['Condition'] = re.search("\(Qualifying.*\)",desc, re.IGNORECASE)[0].replace("(","").replace(")","")

            self.df_coupons = self.df_coupons.append(availableOffers,ignore_index = True)

        # yield self.df_coupons.to_csv("digitalvidya.csv",sep=",")
        yield {
            'ans':availableOffers
        }
    