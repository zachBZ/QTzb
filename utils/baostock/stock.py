import json
import datetime
import akshare as ak

from utils.baostock.base import Stock


code_map_5y = json.load(open("/Users/zhubin/Desktop/workspace/SPIRE/QTzb/utils/baostock/code_map_5y.json", "r", encoding="utf8"))
code_list_bodong = [
    
]
code_list_guxi = [
    "600873",
    # "600066",
    # "601668",
    # "600803",
    # "601033",
    # "600256",
    # "601328",
    # "002533",
    # "000513",
    # "000048",
    # "000333",
    # "000651",
]

code_list_etf = [
    
]

code_list_chiyou = [
    ["600803", 10000]
]

hangye_lst = [
    ''
]

def get_head_code(code):
    if 'sz.' + code in code_map_5y:
        code = 'sz.' + code
    elif 'sh.' + code in code_map_5y:
        code = 'sh.' + code
    else:
        print(code, "is unvalid")
        return None
    return code

def get_jibao():
    year, month, _ = datetime.date.today().strftime("%Y-%m-%d").split("-")
    tail_lst = {
        '04': ['年报', '一季'],
        '05': ['半年报'],
        '06': ['半年报'],
        '07': ['半年报'],
        '08': ['半年报', '三季'],
        '09': ['半年报', '三季'], 
        '10': ['三季'],
        '11': ['年报'],
        '12': ['年报'],
        '01': ['年报'],
        '02': ['年报'],
        '03': ['年报', '一季'],
    }[month]
    jibao = {}
    for tail in tail_lst:
        period = str(int(year)-1 if tail == '年报' else year) + tail
        try:
            stock_report_disclosure_df = ak.stock_report_disclosure(market="沪深京", period=period)
        except:
            continue
        for code, time1, time2, time3, time4, time5 in zip(
            stock_report_disclosure_df['股票代码'], 
            stock_report_disclosure_df['首次预约'],
            stock_report_disclosure_df['初次变更'],
            stock_report_disclosure_df['二次变更'],
            stock_report_disclosure_df['三次变更'],
            stock_report_disclosure_df['实际披露']
            ):
            for time in [time5, time4, time3, time2, time1]:
                if isinstance(time, datetime.date):
                    try:
                        time = time.strftime("%Y-%m-%d")
                        break 
                    except:
                        continue
            if code in jibao:
                jibao[code] += "/%s:%s" % (period, time)
            else:
                jibao[code] = "%s:%s" % (period, time)
    return jibao

def get_stock_by_code(code):
    jibao = get_jibao()
    jibao_release = jibao[code]
    code = get_head_code(code)
    S = Stock(code, code_map_5y[code])
    S.jibao_release = jibao_release
    return [S]

def get_all_5y_stocks():
    ret = []
    jibao = get_jibao()
    for code, name in code_map_5y.items():
        try:
            jibao_release = jibao[code.split(".")[-1]]
        except:
            jibao_release = None
        S = Stock(code, name)
        if jibao_release:
            S.jibao_release = jibao_release
        ret.append(S)
    return ret

def get_hangye_stocks(hangye="半导体及元件"):
    ret = []
    jibao = get_jibao()
    stock_board_industry_cons_ths_df = ak.stock_board_industry_cons_ths(symbol=hangye)
    for code, name in zip(stock_board_industry_cons_ths_df['代码'], stock_board_industry_cons_ths_df['名称']):
        jibao_release = jibao[code]
        code = get_head_code(code)
        if code is None: continue
        S = Stock(code, code_map_5y[code])
        S.jibao_release = jibao_release
        ret.append(S)
    return ret

def get_chiyou_stocks():
    ret = []
    jibao = get_jibao()
    for code, chiyou_money in code_list_chiyou:
        jibao_release = jibao[code]
        code = get_head_code(code)
        if code is None: continue
        S = Stock(code, code_map_5y[code])
        S.set_cangwei(chiyou_money)
        S.jibao_release = jibao_release
        ret.append(S)
    return ret

def get_bodong_stocks():
    ret = []
    jibao = get_jibao()
    for code in code_list_bodong:
        jibao_release = jibao[code]
        code = get_head_code(code)
        if code is None: continue
        S = Stock(code, code_map_5y[code])
        S.jibao_release = jibao_release
        ret.append(S)
    return ret

def get_guxi_stocks():
    ret = []
    jibao = get_jibao()
    for code in code_list_guxi:
        jibao_release = jibao[code]
        code = get_head_code(code)
        if code is None: continue
        S = Stock(code, code_map_5y[code])
        S.jibao_release = jibao_release
        ret.append(S)
    return ret

def get_etf_stocks():
    ret = []
    jibao = get_jibao()
    for code in code_list_etf:
        jibao_release = jibao[code]
        code = get_head_code(code)
        if code is None: continue
        S.jibao_release = jibao_release
        ret.append(S)
    return ret
    
    