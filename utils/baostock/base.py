import datetime
import baostock as bs
import datetime
import akshare as ak
import numpy as np

lg = bs.login()


def format_num(v):
    if isinstance(v, str):
        if v.isdigit():
            v = float(v)
        elif "亿" in v:
            v = float(v[:-1]) * 10000 * 10000
        elif "万" in v:
            v = float(v[:-1]) * 10000
        elif "." in v:
            v_list = v.split(".")
            if len(v_list) == 2 and v_list[0].isdigit() and v_list[1].isdigit():
                v = float(v)
    return v

class Data:
    def __init__(self):
        self.key_names = [] 
    
    def format_by_list(self, keys, values):
        for k, v in zip(keys, values):
            self.key_names.append(k)
            v = format_num(v)
            setattr(self, k, v)
        return self
    
    def keys(self):
        return self.key_names
    
    def convert(self, k):
        return {
            'date':'日期',
            'code':'股票代码',
            'open':'开盘价',
            'high':'高点',
            'low':'低点',
            'close':'收盘价',
            'preclose':'昨日收盘价',
            'volume':'成交数量',
            'amount':'成交金额',
            'adjustflag':'复权状态',
            'turn': '换手率',
            'tradestatus':'交易状态',
            'pctChg':'涨跌幅',
            'isST':'是否ST',
            'pe':'市盈率',
            'pe_ttm':'市盈率TTM',
            'pb':'市净率',
            'ps':'市销率',
            'ps_ttm':'市销率TTM',
            'dv_ratio':'股息率',
            'dv_ttm':'股息率_TTM',
            'total_mv': '总市值',
            'net_profit_aft_deduct': '扣除非经常性损益后的净利润',
        }[k]
    
    def __str__(self):
        s = ""
        for k in self.key_names:
            s += "%s:%s" % (self.convert(k) + "|" + k, getattr(self, k))
        return s
            

class Stock:
    def __init__(self, code, name):
        self.code = code if "." in code else "%s.%s" % (code[:2], code[2:])
        self.name = name
        self.valid = True
        self.status = {}
        self.his = []
        self.cangwei = 0
        self.jibao_release = ""
        
    def set_cangwei(self, cangwei):
        assert cangwei < 10000
        self.cangwei = cangwei
        
    def init_his_by_ths(self):
        add_keys = []
        symbol = self.code.split(".")[-1]
        # 资产负债表
        # stock_financial_debt_ths_df = ak.stock_financial_debt_ths(symbol=symbol, indicator="按单季度")
        # stock_financial_debt_ths_df.columns.values.tolist()
        
        # 利润表
        stock_financial_benefit_ths_df = ak.stock_financial_benefit_ths(symbol=symbol, indicator="按单季度")[:24]
        add_keys += ['net_profit_aft_deduct']
        
        # 现金流量表
        # stock_financial_cash_ths_df = ak.stock_financial_cash_ths(symbol=symbol, indicator="按单季度")
        # stock_financial_cash_ths_df.columns.values.tolist()
        return stock_financial_benefit_ths_df, add_keys

    
    def init_his(self, period):
        today = datetime.date.today().strftime("%Y-%m-%d")
        yesterday = (datetime.date.today()-datetime.timedelta(days=period)).strftime("%Y-%m-%d")
        add_data = bs.query_history_k_data_plus(self.code,
            "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
            start_date=yesterday, end_date=today,
            frequency="d", adjustflag="3")
        # add_data2 = ak.stock_zh_a_hist(symbol=self.code.split(".")[-1], period="daily", start_date=yesterday, end_date=today, adjust="")
        # for idx2 in range(len(add_data2)):
        #     add_data2_map[add_data2['日期'][idx].strftime("%Y-%m-%d")] = np.array(add_data2.iloc[idx]).tolist()[1:] + [[]]

        result_list = []
        
        # try:
        
        # except:
        #     self.valid = False
        #     print("%s[%s] init false !!" % (self.name, self.code))
        #     return 
        # base_data_financial = ak.stock_financial_analysis_indicator(symbol=self.code.split(".")[-1], start_year=start_year)
        try:
            base_data = ak.stock_a_indicator_lg(symbol=self.code.split(".")[-1])
            base_data_financial, add_keys = self.init_his_by_ths()
            base_data_map = {}
            base_length = len(np.array(base_data.iloc[0]).tolist())
            base_fields = base_data.columns.values.tolist()[1:]
            for idx in range(len(base_data)):
                base_data_map[base_data['trade_date'][idx].strftime("%Y-%m-%d")] = np.array(base_data.iloc[idx]).tolist()[1:] + [[]]
                
            base_fields += add_keys
            for idx in range(len(base_data_financial)-1, -1, -1):
                seasona_time = base_data_financial['报告期'][idx]
                latest_seasona_time = datetime.datetime.strptime(seasona_time , "%Y-%m-%d")
                for cur_day in base_data_map.keys():
                    cur_day_time = datetime.datetime.strptime(cur_day , "%Y-%m-%d")
                    if cur_day_time > latest_seasona_time:
                        base_data_map[cur_day][-1].append(seasona_time + "#" + str(format_num(base_data_financial['*扣除非经常性损益后的净利润'].iloc[idx])))
        except:
            base_length = 0
            base_fields = []
            base_data_map = {}

        while (add_data.error_code == '0') & add_data.next():
            row_data = add_data.get_row_data()
            date = row_data[0]
            row_data.extend(base_data_map.get(date, [None]*base_length))
            result_list.append(row_data)
        for result in result_list:
            data_per_day = Data().format_by_list(add_data.fields + base_fields, result)
            self.his.append(data_per_day)
        print("%s[%s] init done !!" % (self.name, self.code))
        
    def set_valid(self, flag):
        self.valid = flag
        
    def __call__(self, func):
        if not len(self.his): self.valid = False
        if self.valid:
            self.status.update(func(self))
        
class Filter:
    def __init__(self, name="default"):
        self.name = name
        self.code = None 
        self.info = ""
        self.target = "S" # S: sale, B: buy
        self.score = 0 # 体现置信度，越高越好
    
    def is_pass(self):
        pass
    
    def set_target(self, target):
        self.target = target
    
    def __call__(self, stock):
        if not stock.valid:
            return {self.name: [False, self.score, self.info]}
        self.code = stock.code
        if self.is_pass(stock):
            return {self.name: [True, self.score, self.info]}
        else:
            return {self.name: [False, self.score, self.info]}
        
class Aggrator:
    def __init__(self, name="default"):
        self.name = name
        self.release = []
        self.info = ""
        
    def aggrate(self, status):
        return True, self.info
    
    def color_info(self, info):
        info = info.replace("建议买入", "\033[33m建议买入\033[0m")
        info = info.replace("建议不买", "\033[33m建议不买\033[0m")
        info = info.replace("建议卖出", "\033[33m建议卖出\033[0m")
        info = info.replace("建议不卖", "\033[33m建议不卖\033[0m")
        info = info.replace("建议持有", "\033[33m建议持有\033[0m")
        return info
        
    def __call__(self, stock_groups):
        release_ok = []
        release_no = []
        for stock in stock_groups:
            aggrate_flag, info, score = self.aggrate(stock.status)
            try:
                gujia = stock.his[-1].close
                gufen_per_w = int(10000 / stock.his[-1].close / 100) * 100
            except:
                gujia, gufen_per_w = -1, -1
            if aggrate_flag:
                release_ok.append([score, "\033[31m[%s](%s)[%.4f][今日股价%.2f,万份持股%s][最新财报时间-%s]\033[0m" % (stock.name, stock.code, score, gujia, gufen_per_w, stock.jibao_release) \
                    + "\n" + info])
            else:
                release_no.append([score, "\033[33m[%s](%s)[%.4f][今日股价%.2f,万份持股%s][最新财报时间-%s]\033[0m" % (stock.name, stock.code, score, gujia, gufen_per_w, stock.jibao_release) \
                    + "\n" + info])
                
        release_ok = sorted(release_ok, reverse=True, key=lambda x: x[0])
        release_no = sorted(release_no, reverse=True, key=lambda x: x[0])
        release_ok = [k[1] for k in release_ok]
        release_no = [k[1] for k in release_no]
        self.release = release_ok + ["=" * 40 + " 下列排除 " + "=" * 40] + release_no
             
    
        



    