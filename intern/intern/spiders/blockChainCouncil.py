# import scrapy
# import re
# import json
# import pandas as pd
# from dateutil.relativedelta import relativedelta
# from datetime import date, datetime

# class CourseScraper(scrapy.Spider):
#     name = 'blockChainCouncilSpider'

#     df_coupons = pd.DataFrame(columns=['Link','Discount Percentage', 'Discount Price', 'Discount Price Currency', 'Coupon Code', 'Learn Type',
#                 'Applicability', 'Discount Type', 'Course Specific', 'Course Link', 'Instruction Type', 'User Type',               # New User/ All Users
#                 'Category', 'Skills', 'Card', 'Validity', 'Price Condition', 'Price Limit', 'Condition', 'Description'])

#     def start_requests(self):
#         return [scrapy.FormRequest('https://www.discountreactor.com/coupons/blockchain-council.org', 
#                                     headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0'},
#                                     callback=self.parse_discountreactor)]
 
#     def parse_discountreactor(self, response):
        
#         couponContainer = response.xpath("//div[@data-section='active']//span[contains(text(),'Verified')]/../../../..")
        
#         for coupons in couponContainer:
#             availableOffers = {
#                 'Link': '',
#                 'Discount Percentage' : '', 
#                 'Discount Price' : '',
#                 'Discount Price Currency' : '',
#                 'Coupon Code' : '',	
#                 'Learn Type' : '',
#                 'Applicability' : '',
#                 'Discount Type' : '',
#                 'Course Specific' : '',
#                 'Course Link': '',
#                 'Instruction Type' : '',
#                 'User Type' : '',               # New User/ All Users
#                 'Category': '',
#                 'Skills' : '',	
#                 'Card' : '',
#                 'Validity' : '',                # Expiry Date
#                 'Price Condition' : '',
#                 'Price Limit' : '',
#                 'Condition' : '',
#                 'Description': ''
#             }

#             availableOffers['Link'] = response.url + '?oid=' + coupons.xpath("./@data-id").get()
    
#             desc = coupons.xpath("./div[@class='offer-list-item-right']/div/div[@class='offer-list-item-title h3']/a/text()").get()

#             availableOffers['Description'] = desc.replace('\"',"").strip()

#             availableOffers['Coupon Code'] = coupons.xpath("./div[@class='offer-list-item-right']/div/div[@class='offer-list-item-button-content']/a/div[@class='offer-list-item-button_hidden-code']/@data-code").get()

#             valid = coupons.xpath("./div[@class='offer-list-item-right']/div/div[@class='offer-list-item-used']/span[contains(text(),'Valid')]/text()").get()

#             if valid:
#                 if re.search("week(s)?", valid,re.IGNORECASE):
#                     period = date.today() + relativedelta(weeks=+int(re.search("\d{1,3}",valid)[0]))
#                     availableOffers['Validity'] = period
#                 elif re.search("day(s)?", valid,re.IGNORECASE):
#                     period = date.today() + relativedelta(days=+int(re.search("\d{1,3}",valid)[0]))
#                     availableOffers['Validity'] = period
#                 elif re.search("year(s)?", valid,re.IGNORECASE):
#                     period = date.today() + relativedelta(years=+int(re.search("\d{1,3}",valid)[0]))
#                     availableOffers['Validity'] = period
#                 elif re.search("month(s)?", valid,re.IGNORECASE):
#                     period = date.today() + relativedelta(months=+int(re.search("\d{1,3}",valid)[0]))
#                     availableOffers['Validity'] = period
#                 # else
#                 #     availableOffers['Validity'] = re.search("[0-9].*(day|week|hour|month|year)s",valid,re.IGNORECASE)[0]

#             if re.search("\d{1,}%", desc):
#                 availableOffers['Discount Percentage'] = re.search("\d{1,}%", desc)[0]
#             elif re.search("$\d{1,}", desc):
#                     availableOffers['Discount Price'] = re.search("$\d{1,}", desc)[0]
                    
#             if re.search("(store([ -]?)wide)|(site([ -]?)wide)|((any|all|next|first|your) (order|course)(s?))",desc, re.IGNORECASE):
#                 availableOffers['Applicability'] = 'Sitewide'

#             elif re.search("(off \(certifications\))|(.* or more certification)", desc, re.IGNORECASE):
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
#                         availableOffers['Course Specific'] = re.sub("(off|OFF|Off) (\()?","",re.search("off.*(Training|certification|certified|course)",desc,re.IGNORECASE)[0]).replace("(","")

#                     else:
#                         availableOffers['Applicability'] = 'Instruction Type'
#                 else:
#                     if re.search("(certification|Certified|course|Program)", desc, re.IGNORECASE):
#                         availableOffers['Applicability'] = 'Course Specific'
#                         availableOffers['Course Specific'] = re.sub("(off|OFF|Off) (\()?","",re.search("off.*(Training|certification|certified|course)",desc,re.IGNORECASE)[0]).replace("(","")
#                     else:
#                         availableOffers['Applicability'] = 'Category'
#                         availableOffers['Category'] = re.sub("(off|OFF|Off) (\()?","",re.search("off.*(Training|certification|certified|course)",desc,re.IGNORECASE)[0]).replace("(","")
#                 availableOffers['Learn Type'] = 'Certification'
    

#             if re.search("(Live|Instructor)?.*Training",desc, re.IGNORECASE):
#                 availableOffers['Instruction Type'] = 'Instructor Paced'
#             else:
#                 availableOffers['Instruction Type'] = 'Self Paced'
            

#             if re.search("Up To", desc):
#                 availableOffers['Discount Type'] = 'Up To'
#             else:
#                 availableOffers['Discount Type'] = 'Flat'


#             if re.search("(One|Two|Three|Four|Five|Six|\d) or more (orders|purchases|courses|certifications)?",desc,re.IGNORECASE):
#                 availableOffers['Condition'] = re.search("(One|Two|Three|Four|Five|Six|\d) or more (orders|purchases|courses|certifications)?",desc,re.IGNORECASE)[0]

#             if re.search("Next (orders|purchases|courses|certifications)",desc,re.IGNORECASE):
#                 availableOffers['Condition'] = re.search("Next (orders|purchases|courses|certifications)",desc,re.IGNORECASE)[0]

#             self.df_coupons = self.df_coupons.append(availableOffers,ignore_index = True)

#         yield scrapy.Request('https://blockchaincouncil.knoji.com/promo-codes/', self.parse_konji, headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0'})

    
#     def parse_konji(self, response):

#         couponTable = response.xpath("//div[@class='module filter-promo']/h2[contains(text(),'Blockchain Council Coupon Codes: Complete Timetable')]/..")
#         validCoupons = couponTable.xpath("./div/div[@class='tablerow']/div/div[contains(text(),'Yes')]/../..")

#         hiddenCoupons = couponTable.xpath("./div/div[@class='tablerow--hidden']/div/div[contains(text(),'Yes')]/../..")

#         if hiddenCoupons:
#             validCoupons += hiddenCoupons

#         for coupons in validCoupons:
#             availableOffers = {
#                 'Link': '',
#                 'Discount Percentage' : '', 
#                 'Discount Price' : '',
#                 'Discount Price Currency' : '',
#                 'Coupon Code' : '',	
#                 'Learn Type' : '',
#                 'Applicability' : '',
#                 'Discount Type' : '',
#                 'Course Specific' : '',
#                 'Course Link': '',
#                 'Instruction Type' : '',
#                 'User Type' : '',               # New User/ All Users
#                 'Category': '',
#                 'Skills' : '',	
#                 'Card' : '',
#                 'Validity' : '',                # Expiry Date
#                 'Price Condition' : '',
#                 'Price Limit' : '',
#                 'Condition' : '',
#                 'Description': ''
#             }
    
#             availableOffers['Coupon Code'] = coupons.xpath("./div/span[@class='popu']/text()").get()

#             for text in coupons.xpath("./div/text()").getall():
#                 if re.search("(off.+)|(free)",text,re.IGNORECASE):
#                     desc = text
            
#             availableOffers['Description'] = desc

#             availableOffers['Link'] = coupons.xpath("./div/span[@class='popu']/@data-tab").get()

#             if re.search("\d{1,}%", desc):
#                 availableOffers['Discount Percentage'] = re.search("\d{1,}%", desc)[0]
#             elif re.search("\$\d{1,}", desc):
#                 availableOffers['Discount Price'] = re.search("$\d{1,}", desc)[0]
            
          
#             if re.search("(store([ -]?)wide)|(site([ -]?)wide)|((All|Next|First|any) (Order|course)(s?))",desc, re.IGNORECASE):
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
#                         availableOffers['Course Specific'] = re.sub("\)$", "" ,re.sub("(off|OFF|Off) (\()?","",re.search("off.*\)",desc,re.IGNORECASE)[0]))

#                     else:
#                         availableOffers['Applicability'] = 'Instruction Type'
#                 else:
#                     if re.search("(certification|certified|course|Program)", desc, re.IGNORECASE):
#                         availableOffers['Applicability'] = 'Course Specific'
#                         availableOffers['Course Specific'] = re.sub("\)$", "" ,re.sub("(off|OFF|Off) (\()?","",re.search("off.*\)",desc,re.IGNORECASE)[0]))
#                     else:
#                         availableOffers['Applicability'] = 'Category'
#                         availableOffers['Category'] = re.sub("\)$", "" ,re.sub("(off|OFF|Off) (\()?","",re.search("off.*(\)|courses|certifications)",desc,re.IGNORECASE)[0]))
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
        
#         yield scrapy.Request('https://www.retailmenot.com/view/blockchain-council.org', self.parse_retailmenot, headers = {"Host": "www.retailmenot.com","User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0"})


#     def parse_retailmenot(self, response):

#         jsonData = json.loads(re.sub("<\/script>","",re.sub("<script.*(type=\"application\/json\")>","",response.xpath("//script[@id='__NEXT_DATA__']").get())))

#         offersId = response.xpath("//div[@class='sc-AxjAm fRQtxW']/li/div/div/div/@data-qa-offer-uuid").getall()

#         offersData = jsonData["props"]["pageProps"]["serverState"]["apollo"]["data"]

#         for id in offersId:
#             if offersData[f"OfferCard:{id}.redemption.0"]["type"] == "CODE" and offersData[f"$OfferCard:{id}.validation"]["validity"] == "VALID":
#                 availableOffers = {
#                     'Link': '',
#                     'Discount Percentage' : '', 
#                     'Discount Price' : '',
#                     'Discount Price Currency' : '',
#                     'Coupon Code' : '',	
#                     'Learn Type' : '',
#                     'Applicability' : '',
#                     'Discount Type' : '',
#                     'Course Specific' : '',
#                     'Course Link': '',
#                     'Instruction Type' : '',
#                     'User Type' : '',               # New User/ All Users
#                     'Category': '',
#                     'Skills' : '',	
#                     'Card' : '',
#                     'Validity' : '',                # Expiry Date
#                     'Price Condition' : '',
#                     'Price Limit' : '',
#                     'Condition' : '',
#                     'Description': ''
#                 }

#                 availableOffers['Link'] = response.url + f'?u={id}'

#                 desc = offersData[f"OfferCard:{id}"]['title']

#                 availableOffers['Description'] = desc

#                 if re.search("\d{1,}%", desc):
#                     availableOffers['Discount Percentage'] = re.search("\d{1,}%", desc)[0]
#                 elif re.search("$\d{1,}", desc):
#                         availableOffers['Discount Price'] = re.search("$\d{1,}", desc)[0]
                    
#                 if re.search("(store([ -]?)wide)|(site([ -]?)wide)|((any|all|next|first|your) (order|course)(s?))",desc, re.IGNORECASE):
#                     availableOffers['Applicability'] = 'Sitewide'

#                 elif re.search("(off \(certifications\))|(.* or more certification)", desc, re.IGNORECASE):
#                     availableOffers['Applicability'] = 'Learn Type'
#                     availableOffers['Learn Type'] = 'Certification'

#                 elif re.search("membership|subscription",desc,re.IGNORECASE):
#                     availableOffers['Applicability'] = 'Subscription'

#                 elif re.search("(Master\'s)|(Post Grad)", desc, re.IGNORECASE):
#                     availableOffers['Applicability'] = "Learn Type"
#                     availableOffers['Learn Type'] = 'Masters'

#                 else:
#                     if re.search("(Live|Instructor).*? Training", desc,re.IGNORECASE):
#                         if re.search("(certified|certification)", desc, re.IGNORECASE):
#                             availableOffers['Applicability'] = 'Course Specific'
#                             availableOffers['Course Specific'] = re.sub("(off|OFF|Off)","",re.search("off.*",desc,re.IGNORECASE)[0])

#                         else:
#                             availableOffers['Applicability'] = 'Instruction Type'
#                     else:
#                         if re.search("(certification|certified|course|Program)", desc, re.IGNORECASE):
#                             availableOffers['Applicability'] = 'Course Specific'
#                             availableOffers['Course Specific'] = re.sub("(off|OFF|Off)","",re.search("off.*",desc,re.IGNORECASE)[0])
#                         else:
#                             availableOffers['Applicability'] = 'Category'
#                             availableOffers['Category'] = re.sub("(off|OFF|Off)","",re.search("off.*",desc,re.IGNORECASE)[0])
#                     availableOffers['Learn Type'] = 'Certification'


#                 if re.search("(Live|Instructor)?.*Training",desc, re.IGNORECASE):
#                     availableOffers['Instruction Type'] = 'Instructor Paced'
#                 else:
#                     availableOffers['Instruction Type'] = 'Self Paced'
                    
#                 if re.search("Up To", desc, re.IGNORECASE):
#                     availableOffers['Discount Type'] = 'Up To'
#                 else:
#                     availableOffers['Discount Type'] = 'Flat'

    
#                 availableOffers['Coupon Code'] = offersData[f"OfferCard:{id}.redemption.0"]['code']

#                 expireDate = re.sub("End ", "", offersData[f"OfferCard:{id}.redemption.0"]['expirationText'])
#                 if expireDate:
#                     availableOffers['Validity'] = datetime.strptime(expireDate, '%m/%d/%Y').strftime('%Y-%m-%d')

#                 self.df_coupons = self.df_coupons.append(availableOffers,ignore_index = True)

#         self.df_coupons.drop_duplicates(subset=['Discount Percentage', 'Coupon Code','Learn Type', 'Applicability', 'Discount Type', 'Course Specific'],inplace=True, ignore_index=True)
#         self.df_coupons = self.df_coupons.sort_values(by=['Discount Percentage'], ascending=False, ignore_index=True)
#         yield self.df_coupons.to_csv("BlockChainCouncil.csv",sep=",")
        