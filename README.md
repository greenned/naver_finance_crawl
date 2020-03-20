# naver_finance_crawl
네이버증권 일별 주식가격 크롤러

## How to Use
~~~python
code_list = [("Naver",'035420'),
                 ("삼성전자", "005930")
                    ] 
    t = financeCralwer(from_="2020-01-01", to_="2020-01-31", code_list=code_list,debug=False).main()
~~~


## Return Value

    [
    {
        "name": "Naver", # 종목명
        "code:code, # 종목코드
        "data":df, 
        # 날짜, 종가, 전일비, 시가, 고가, 저가, 거래량 데이터프레임
        "from":from_, # 시작날짜
        "to_":to_ , # 끝날짜
        "url":url # 크롤링주소
      }
      ]
