from bs4 import BeautifulSoup
import requests
import traceback
import pandas as pd
import datetime
from tqdm import tqdm

class financeCralwer:
    def __init__(self, from_, to_, code_list=[], debug=False):
        '''
        from_ = "2020-01-01"
        to_ = "2020-01-01"
        code_list = [("Naver",'035420')]  (종목명, 종목코드)
        '''
        self.DEBUG = debug
        self.url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format
        # 날짜형식 초기화
        self.init_date(from_, to_)
        self.code_list = code_list
        # return값 초기화
        self.init_result()

    def init_date(self, from_, to_):
        split_from = list(map(int, from_.split("-")))
        split_to = list(map(int, to_.split("-")))
        self.datetime_from = datetime.datetime(year=split_from[0], month=split_from[1], day=split_from[2])
        self.datetime_to = datetime.datetime(year=split_to[0], month=split_to[1], day=split_to[2])
        self.from_ = datetime.datetime.strftime(datetime.datetime(year=split_from[0], month=split_from[1], day=split_from[2]), '%Y.%m.%d')
        self.to_ = datetime.datetime.strftime(datetime.datetime(year=split_to[0], month=split_to[1], day=split_to[2]), '%Y.%m.%d')

    def init_base_dict(self):
        '''
        {"name": "Naver", "code:code, "data":df, "from":from_, "to_":to_ ,"url":url}
        '''
        self.base_dict = {"name":None, "code":None, "data":None, "from":self.from_, "to":self.to_, "url":None, "last_page":None}

    def init_result(self):
        self.result_list = []
        for code_tup in self.code_list:
            self.init_base_dict()
            self.base_dict['name'] = code_tup[0]
            self.base_dict['code'] = code_tup[1]
            self.base_dict['url'] = self.url(code=code_tup[1])
            self.result_list.append(self.base_dict)
        
        if self.DEBUG : print(self.result_list)

    def main(self):
        for dic in tqdm(self.result_list):
            dic['last_page'] = self.get_last_page(dic['url'])
            dic['data'] = self.get_data(dic['url'], dic['last_page'])
        if self.DEBUG : print(self.result_list)
        return self.result_list
    
    # 마지막 페이지 읽어오기
    def get_last_page(self, code_url):
        res = requests.get(code_url)
        res.encoding = 'utf-8'
        if res.status_code != 200:
            print("URL 접근실패")
            raise Exception
            
        soap = BeautifulSoup(res.text, 'lxml')
        el_table_navi = soap.find("table", class_="Nnavi")
        el_td_last = el_table_navi.find("td", class_="pgRR")
        pg_last = el_td_last.a.get('href').rsplit('&')[1]
        pg_last = pg_last.split('=')[1]
        pg_last = int(pg_last)
        return pg_last

    def get_data(self, code_url, last_page):
        df = None
        for page in range(1, last_page+1):
            _df = self.parse_page(code_url, page)
            df = pd.concat([df, _df])
            if self.filter_check(df):
                df = self.filter_df(df)
                return df
            else:
                continue
    
    def filter_df(self, df):
        df['날짜'] = pd.to_datetime(df['날짜'], format="%Y.%m.%d")
        df = df[(df['날짜'] > self.datetime_from) & (df['날짜'] < self.datetime_to)]
        if self.DEBUG:print(df)
        return df
    
    def filter_check(self, df):
        check = False
        if self.DEBUG : print(df['날짜'].values)
        for val in df['날짜'].values:
            val = datetime.datetime.strptime(val, '%Y.%m.%d')

            if val <= self.datetime_from:
                check=True
        return check
        
                
    def parse_page(self, code_url, page):
        try:
            url = code_url + "&page={page}".format(page=page)
            res = requests.get(url)
            _soap = BeautifulSoup(res.text, 'lxml')
            _df = pd.read_html(str(_soap.find("table")), header=0)[0]
            _df = _df.dropna()
            return _df
        except Exception as e:
            traceback.print_exc()
        return None

# str_datefrom = datetime.datetime.strftime(datetime.datetime(year=2018, month=1, day=1), '%Y.%m.%d')
# str_dateto = datetime.datetime.strftime(datetime.datetime.today(), '%Y.%m.%d')


if __name__ == "__main__":
    code_list = [("Naver",'035420'),
                 ("삼성전자", "005930")
                    ] 
    t = financeCralwer(from_="2020-01-01", to_="2020-01-31", code_list=code_list,debug=False).main()
    print(t)
    #print(financeCralwer(from_="2020-01-01", to_="2020-01-31", code_list=code_list,debug=True).result_list[0]['data'])
    # t = list(map(int, "2020-01-01".split("-")))
    # print(t)