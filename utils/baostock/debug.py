import datetime
import json
from tqdm import tqdm
from utils.baostock.filter import *
from utils.baostock.aggrator import SaleAggrator, BuyAggrator
from utils.baostock.stock import *
import akshare as ak
from multiprocessing import Pool


period = 365
filter_groups_for_buy = [
        # JiBenMianFilter,
        # GuXiFilter,
        ZTFilter,
    ]  

def filter_stocks(stock):
    stock.init_his(period)
    for filter_class in filter_groups_for_buy:
        filter_func = filter_class()
        filter_func.set_target("B")
        stock(filter_func)
    return stock

if __name__ == "__main__":
    agg_buy = BuyAggrator()
    # agg_sale = SaleAggrator()
    
    # 所有5年+股票代码
    stock_groups_all = get_all_5y_stocks()
    # stock_groups_all = get_hangye_stocks("银行")
    # stock_groups_all = get_stock_by_code("002920")
    # 所有持仓代码
    # stock_groups_have = []
    
    # 购买准入条件
      
    
    # 卖出准出条件
    # filter_groups_for_sale = [
    # ] 
    stock_groups = []
    for i in range(len(stock_groups_all)):
        print(i)
        if i ==0 or i % 100 != 0: 
            stock_groups.append(stock_groups_all[i])
            continue
        print(i, "running ... ")
        stock_groups_all_ret = []
        with Pool(processes=5) as pool:
            for stock in tqdm(pool.imap_unordered(filter_stocks, stock_groups),total=len(stock_groups)):
                stock_groups_all_ret.append(stock)
        stock_groups = []
                
        # for stock in stock_groups_all:
        #     stock_groups_all_ret.append(filter_stocks(stock))
            
                
        agg_buy(stock_groups_all_ret)
        # for stock in stock_groups_have:
        #     for filter_class in filter_groups_for_sale:
        #         filter_func = filter_class()
        #         filter_func.set_target("S")
        #         stock(filter_func)
        # agg_sale(stock_groups_have)
        
        print(">>>>>> 每日看板: %s <<<<<<< " % datetime.date.today().strftime("%y-%m-%d"))
        print("")
        print("+ 候选股[买入建议]")
        for info in agg_buy.release:
            print(" |-", info)
        # print("")
        # print("+ 持有股[卖出建议]")
        # for info in agg_sale.release:
        #     print(" |-", info)