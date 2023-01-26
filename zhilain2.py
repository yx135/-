# -*- coding:utf8 -*-
import requests
from threading import Thread
from queue import Queue
import time
from lxml import etree
import csv
from threading import Lock
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class zhilianSpider(object):
    def __init__(self):
        self.jobnamekw='python'
        self.jobaddress='兰州'
        self.url ='https://sou.zhaopin.com/?jl='+self.jobaddress+'&kw='+self.jobnamekw+'&p='
        # 存放所有URL地址的队列
        self.q = Queue()
        self.count=0
        self.i = 0
        # 存放第一层URL解析结果的的空列表
        self.list = []
        self.p=[]
        self.page=0
        self.f = open('zhilian_'+self.jobaddress+'_'+self.jobnamekw+'.csv', mode='a',encoding='utf-8',newline='')
        self.csv_writer= csv.DictWriter(self.f,fieldnames=['title','money','context','address','compay', 'url'])
        # 创建锁
        self.lock = Lock()
        self.Cookie='''urlfrom=121113803; urlfrom2=121113803; adfbid=0; adfbid2=0; x-zp-client-id=8fc84594-d214-41cf-a629-7d208fcd3c94; sajssdk_2015_cross_new_user=1; sts_deviceid=185dcdb576b1ad-04fd33f8d32fd6-26021051-921600-185dcdb576c295; ZP_OLD_FLAG=false; Hm_lvt_38ba284938d5eddca645bb5e02a02006=1674447642; sts_sg=1; sts_chnlsid=121113803; zp_src_url=https://landing.zhaopin.com/; zp_passport_deepknow_sessionId=32691306s1dec64aa5b928c741b108830492; at=addbdf1758ee43d18d30367a38b3eeb5; rt=4473fac6f36741cbb7796e9de051e601; selectCity_search=864; Hm_lpvt_38ba284938d5eddca645bb5e02a02006=1674458241; sensorsdata2015jssdkcross={"distinct_id":"1140513343","first_id":"185dcdace9852d-05bbdfb156bced8-26021051-921600-185dcdace99430","props":{"$latest_traffic_source_type":"直接流量","$latest_search_keyword":"未取到值_直接打开","$latest_referrer":"","$latest_utm_source":"baidupcpz","$latest_utm_medium":"cpt"},"identities":"eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTg1ZGNkYWNlOTg1MmQtMDViYmRmYjE1NmJjZWQ4LTI2MDIxMDUxLTkyMTYwMC0xODVkY2RhY2U5OTQzMCIsIiRpZGVudGl0eV9sb2dpbl9pZCI6IjExNDA1MTMzNDMifQ==","history_login_id":{"name":"$identity_login_id","value":"1140513343"},"$device_id":"185dcdace9852d-05bbdfb156bced8-26021051-921600-185dcdace99430"}; ssxmod_itna=eqUxBQDQGQG=NAKGHD8KRrwiE6xYvNqGOY/0UKDBk74iNDnD8x7YDvmmEQbmF7Gm0Dxax5hOxNae/23O++eY46y4oDU4i8DCkmaqbDem=D5xGoDPxDeDADYE6DAqiOD7qDdfhTXtkDbxi3fxiaDGeDeEKODY5DhxDC0mPDwx0Cfc0Nf17Fdtym2=RhqQG8D7HpDlPeEIG8Nf3Lomyh+b3GfiKDXEdDvayCS6cmDBbkMO5G/ih3diheZmhei0RYq705Wm0Y=lCdi7Des0ZusmeY+j0rHe=nDDp4iwhDD=; ssxmod_itna2=eqUxBQDQGQG=NAKGHD8KRrwiE6xYvNqGOY/0KD8dp3ODGX53GaKFIkhx82AU2VpUNuFQfKhGnKFYB6sO48Cob1KoCla+OiDfkDtjzozQPG2bl408DedhD===; ZL_REPORT_GLOBAL={"/resume/new":{"actionid":"5aa04c91-9381-4242-8097-2db7f4e8b921","funczone":"addrsm_ok_rcm"},"jobs":{"funczoneShare":"dtl_best_for_you","recommandActionidShare":"7bf00d3a-569b-4d55-abed-fc5258d16574-job"}}; acw_tc=ac11000116744642634128158e00d6f09e09e0ca972bd7a9e0ba4aa484d7fb'''
        self.Cookie=self.Cookie.encode("utf-8")
        self.headerss={
                    'cookie':self.Cookie,
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'}

    

  #
  # url入队函数，拼接url，并将url加入队列
    def url_in(self):
        for url in self.list:
            # 把URL地址入队列
            self.q.put(url)
    #解析第一层URL
    def getoneinfo (self,page):
        urls=self.url+str(page)
        html=requests.get(url=urls,headers=self.headerss).text
        parse_html=etree.HTML(html)
        path='//div[@class="joblist-box__item clearfix"]'
        path1='//div[@class="page-empty__tips"]/span/text()'
        l=parse_html.xpath(path)
        self.list.extend(l)
        self.p.extend(parse_html.xpath(path1))
      #解析第二层URL
    def gettwoinfo(self,urls):
        item={}
        urls=urls.xpath('.//a/@href')[0]
        pos_url=self.count-int(self.q.qsize())
        desired_capabilities = DesiredCapabilities.CHROME  # 设置这个选项，加载更快。
        desired_capabilities["pageLoadStrategy"] = "none"
        chrome_options = webdriver.ChromeOptions()  # 无界面模式的选项设置
        chrome_options.add_argument('--headless')
        browser = webdriver.Chrome(executable_path = './venv/Scripts/chromedriver.exe', chrome_options=chrome_options)
        self.lock.acquire()
        print(str(pos_url)+'获得锁')
        browser.get(urls)  # 访问网页
        print('当前访问的网址是：', pos_url)

        # 等待网页加载
        wait = WebDriverWait(browser, 5)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.job-summary')))
        self.lock.release()
        print(str(pos_url)+'释放锁')
        response_text = browser.page_source  # 获得加载后的网页源代码
        two_html=etree.HTML(response_text)
        item={}
        item["title"]=two_html.xpath('//div[@class="summary-plane__content"]/h3[@class="summary-plane__title"]/text()')
        item["money"]=two_html.xpath('//div[@class="summary-plane__left"]/span[@class="summary-plane__salary"]/text()')
        item['context']=two_html.xpath('//div[@class="describtion__detail-content"]/descendant::*/text()|//div[@class="describtion__detail-content"]/text()')
        item['address']=two_html.xpath('//span[@class="job-address__content-text"]/text()')
        item['compay']=two_html.xpath('//a[@class="company__title"]/text()')
        item['url']=urls
        
        self.csv_writer.writerow(item) 
       
  # 获取第一层解析后的列表
    def get_list(self):
       if(len(self.p))!=0:
          print("无查询结果")
       while len(self.p)==0:
          self.page=self.page+1
          self.getoneinfo(self.page)
  #获取第二层解析后的字典
    def get_csv(self):
      while True:
         if not self.q.empty():
            url = self.q.get()
            self.gettwoinfo(url)
         else:
            break
  
    # 入口函数
    def main(self):
      # URL入队列
      self.get_list()
      self.url_in()
      self.count=int(self.q.qsize())
      print('队列个数：'+str(self.count))

      t_list = []
      self.csv_writer.writeheader()
      # 创建多线程
      for i in range(5):
        t = Thread(target=self.get_csv)
        t_list.append(t)
        # 启动线程
        t.start()

      for t in t_list:
          # 回收线程   
          t.join()

      self.f.close()
      print('数量:',self.count)

if __name__ == '__main__':
    start = time.time()
    spider = zhilianSpider()
    spider.main()
    end = time.time()
    print('执行时间:%.1f' % (end-start))