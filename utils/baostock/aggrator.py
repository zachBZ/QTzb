from utils.baostock.base import Aggrator


class SaleAggrator(Aggrator):
    def __init__(self):
        super().__init__("卖出评估")
        
    def format_info(self, status):
        info = "\n"
        flag = True
        score = 0
        status = sorted([(k, v) for k, v in status.items()], reverse=True, key=lambda x: x[1])
        for k, v in status:
            sub_flag, sub_score, sub_info = v
            sub_info = "".join([("         + "+i+"\n") for i in sub_info.split("/")])
            info += "     + %s[%.4f]:\n%s" % (k, sub_score, sub_info)
            score += sub_score
            flag = flag or sub_flag
        info = self.color_info(info)
        return flag, info, score
        
    def aggrate(self, status):
        return self.format_info(status)
    
    
class BuyAggrator(Aggrator):
    def __init__(self):
        super().__init__("购买评估")
        
    def format_info(self, status):
        info = "\n"
        flag = True
        status = sorted([(k, v) for k, v in status.items()], reverse=True, key=lambda x: x[1])
        score = 0
        for k, v in status:
            sub_flag, sub_score, sub_info = v
            sub_info = "".join([("         - "+i+"\n") for i in sub_info[:-1].split("/")])
            info += "     + %s[%.4f]:\n%s" % (k, sub_score, sub_info)
            score += sub_score
            flag = flag and sub_flag
        info = self.color_info(info)
        return flag, info, score
        
    def aggrate(self, status):
        return self.format_info(status)
        