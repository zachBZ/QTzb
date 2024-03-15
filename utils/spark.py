import requests
import time
import json
import pandas as pd

start_year = '2022'
market = 'sh' # sz代表深交所，sh代表上交所
code = '601328'
sheets = ['fzb','lrb','llb']
sheets = ['lrb']
tp = '4' # 0：全部，1：一季报，2：半年报，3：三季报，4：年报
page = '1'
num = '10'
search = "应付普通股股利"
shizhi = 473050000000
target = 0.059

hds = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134'
}

for tp in ["0", "1", "2", "3", "4"]:
    for sheet in sheets:
        com_url = 'https://quotes.sina.cn/cn/api/openapi.php/CompanyFinanceService.getFinanceReport' + start_year + '?paperCode=' + market + code + '&source=' + sheet + '&type=' + tp + '&page=' + page + '&num=' + num
        r = requests.get(com_url, headers = hds)
        rtext = r.text
        json_data = json.loads(rtext)
        projects = []; i = 0; result_dict = dict()
        for year in range(int(start_year), int(start_year) - int(num), -1):
            if str(year) + '1231' not in json_data['result']['data']['report_list']: continue
            year_data = json_data['result']['data']['report_list'][str(year) + '1231']['data']
            i = i + 1; year_result = []
            if i == 1:
                for dct in year_data:
                    if dct['item_title'] == search:
                        print(tp, year, float(dct['item_value']) / shizhi)
                    projects.append(dct['item_title'])
                result_dict['报表项目'] = projects
            for dct in year_data:
                if str(dct['item_value']) == 'None':
                    year_result.append(0)
                elif dct['item_value'] == '':
                    year_result.append('')
                else:
                    year_result.append(float(dct['item_value']))
            result_dict[str(year) + '年'] = year_result

        time.sleep(1)
        
        # sheet_data = pd.DataFrame(data = result_dict)
        # import pdb; pdb.set_trace()
        # sheet_data.to_excel("/Users/zhubin/Desktop/workspace/SPIRE/QTzb/data/financial_table/" + code + ' ' + sheet + "_"+ tp + '.xlsx',index = False)
        # print(code + ' ' + sheet + ' 数据已保存')