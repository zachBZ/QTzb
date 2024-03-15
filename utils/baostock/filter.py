import requests
import json
import datetime
import matplotlib.pyplot as plt
from utils.baostock.base import Filter


class GuXiFilter(Filter):
    def __init__(self, sale_rate=0.03, buy_rate=0.04):
        super().__init__("股息因子")
        self.sale_rate = sale_rate
        self.buy_rate = buy_rate
        
    def vis(self, guxi_his, date_his, name):
        save = "/Users/zhubin/Desktop/workspace/SPIRE/QTzb/data/vis/" + name + ".png"
        valid_groups = []
        unvalid_groups = []
        date_his_valid, guxi_his_valid = [], []
        date_his_unvalid, guxi_his_unvalid = [], []
        for a, b in zip(date_his, guxi_his):
            if b > self.buy_rate:
                if len(date_his_unvalid):
                    unvalid_groups.append([date_his_unvalid, guxi_his_unvalid])
                    date_his_unvalid, guxi_his_unvalid = [], []
                date_his_valid.append(a)
                guxi_his_valid.append(b)
                continue
            else:
                if len(date_his_valid):
                    valid_groups.append([date_his_valid, guxi_his_valid])
                    date_his_valid, guxi_his_valid = [], []
            if b < self.sale_rate:
                if len(date_his_valid):
                    valid_groups.append([date_his_valid, guxi_his_valid])
                    date_his_valid, guxi_his_valid = [], []
                date_his_unvalid.append(a)
                guxi_his_unvalid.append(b)
                continue
            else:
                if len(date_his_unvalid):
                    unvalid_groups.append([date_his_unvalid, guxi_his_unvalid])
                    date_his_unvalid, guxi_his_unvalid = [], []
        if len(date_his_valid):
            valid_groups.append([date_his_valid, guxi_his_valid])
            date_his_valid, guxi_his_valid = [], []
        if len(date_his_unvalid):
            unvalid_groups.append([date_his_unvalid, guxi_his_unvalid])
            date_his_unvalid, guxi_his_unvalid = [], []
                    
        plt.plot(date_his, guxi_his, color='black')
        for (date_his_valid, guxi_his_valid) in valid_groups:
            plt.plot(date_his_valid, guxi_his_valid, color='red')
        for (date_his_unvalid, guxi_his_unvalid) in unvalid_groups:
            plt.plot(date_his_unvalid, guxi_his_unvalid, color='green')
        plt.title("chart - guxi")
        plt.xlabel("time")
        plt.ylabel("guxi")
        plt.savefig(save)
        plt.close()
        
    def get_season_profit(self, stock, ratio):
        net_profit_aft_deduct = stock.his[-1].net_profit_aft_deduct
        latest_second, latest_first = net_profit_aft_deduct[-2:]
        last_first_season, last_first_profit = net_profit_aft_deduct[-5].split("#") 
        latest_second_season, latest_second_profit = latest_second.split("#") 
        latest_first_season, latest_first_profit = latest_first.split("#") 
        latest_second_profit = float(latest_second_profit)
        latest_first_profit = float(latest_first_profit)
        last_first_profit = float(last_first_profit)
        increase_ratio_huanbi = (latest_first_profit - latest_second_profit) / latest_second_profit
        increase_ratio_tongbi = (latest_first_profit - last_first_profit) / last_first_profit
        self.info += '净利润(%s->%s)同比增长:%.2f' % (last_first_season, latest_first_season, 100 * increase_ratio_tongbi) + "%"
        if increase_ratio_tongbi < -0.1:
            self.info += ",建议卖出." if self.target == "S" else ",建议不买."
            self.score += ratio if self.target == "S" else 0
            self.info += "/"
            return True if self.target == "S" else False
        else:
            self.info += ",建议买入." if self.target == "B" else ",建议不卖."
            self.score += (ratio * (increase_ratio_tongbi + 0.11) / 0.8)  if self.target == "B" else 0
            self.info += "/"
            return True if self.target == "B" else False
    
    def get_guxi_profit(self, stock, ratio=0.5):
        guxi = float(stock.his[-1].dv_ratio) / 100
        self.info += "今日股息:%.2f" % (guxi*100) + "%"
        if self.target == "B":
            if guxi > self.buy_rate:
                self.info += ",建议买入."
                self.score += ratio * (guxi-self.buy_rate) / 0.03
                self.info += "/"
                return True
            else:
                if guxi > self.sale_rate:
                    self.info += ",建议持有."
                else:
                    self.info += ",建议不买."
                self.info += "/"
                return False
        else:
            if guxi < self.sale_rate:
                self.info += ",建议卖出."
                self.score += ratio * (self.sale_rate-guxi) / 0.005
                self.info += "/"
                return True
            else:
                if guxi > self.buy_rate:
                    self.info += ",建议不卖."
                else:
                    self.info += ",建议持有."
                self.info += "/"
                return False
            
    def add_jibao_score(self, stock, ratio):
        jibao_release_lst = stock.jibao_release.split('/')
        cur_time = datetime.datetime.today()
        days = 365
        for jibao_release in jibao_release_lst:
            jibao_time = datetime.datetime.strptime(jibao_release.split(":")[-1], "%Y-%m-%d")
            days = min(days, (jibao_time - cur_time).days)
        self.score += ratio * days / 30
            
            
    def is_pass(self, stock):
        if False:
            guxi_his = []
            date_his = []
            for stock_his_info in stock.his:
                if stock_his_info.dv_ratio:
                    guxi_his.append(float(stock_his_info.dv_ratio) / 100)
                else:
                    guxi_his.append(0)
                date_his.append(stock_his_info.date)
            self.vis(guxi_his, date_his, stock.name)
        self.add_jibao_score(stock, 0)
        guxi_flag = self.get_guxi_profit(stock, 0.6)
        season_profit_flag = self.get_season_profit(stock, 0.4)
        
        if self.target == "B":
            return guxi_flag and season_profit_flag
        else:
            return guxi_flag or season_profit_flag
        
        
class JiBenMianFilter(Filter):
    def __init__(self):
        super().__init__("基本面因子")
        
    def watch_pe(self, stock, ratio):
        thr = 0.8
        low_pe_date, low_pe_ttm_date = None, None
        his_pe, his_pe_ttm = 10000, 10000
        for his in stock.his[-365:]:
            if his.pe < his_pe:
                his_pe = his.pe
                low_pe_date = his.date
            if his.pe_ttm < his_pe_ttm:
                his_pe_ttm = his.pe_ttm
                low_pe_ttm_date = his.date
        delta = 1 - ((stock.his[-1].pe_ttm - his_pe_ttm) / stock.his[-1].pe_ttm)
        self.score += ratio * delta
        self.info += "市盈率TTM最低(%s):%.2f,市盈率TTM当前(%s):%.2f," % (low_pe_ttm_date, his_pe_ttm, stock.his[-1].date, stock.his[-1].pe_ttm)
        if self.target == "B":
            flag = delta > thr
            self.info += "建议买入." if flag else "建议不买."
            self.info += "/"
            return flag
        else:
            flag = delta < thr
            self.info += "建议卖出." if flag else "建议不卖."
            self.info += "/"
            return flag
        
    def is_pass(self, stock):
        return self.watch_pe(stock, 0.5)
    

class ZTFilter(Filter):
    def __init__(self):
        super().__init__("涨停因子")
        self.zt_thr = 9.99
        
    def cal_zt(self, stock, ratio):
        close_his = None
        for his in stock.his[-30:]:
            if float(his.pctChg) >= self.zt_thr:
                close_his = his
                continue
            if close_his is not None:
                max_close_open = max(his.close, his.open)
                max_zt_close_open = max(close_his.close, close_his.open)
                if his.low < close_his.low or max_close_open / max_zt_close_open  > 1.02:
                    close_his = None
        flag = close_his is not None
        if flag:
            cur_day = datetime.datetime.strptime(stock.his[-1].date , "%Y-%m-%d")
            zt_day = datetime.datetime.strptime(close_his.date , "%Y-%m-%d")
            days = (cur_day - zt_day).days
            self.info += "涨停日(%s)至今震荡%s日,期间收盘价未超过2个点," % (close_his.date, days)
            self.score += ratio * days / 7
            flag = days >= 2
        self.info += "建议买入." if flag else "建议不买."
        return flag
    
    def is_pass(self, stock):
        return self.cal_zt(stock, 1)