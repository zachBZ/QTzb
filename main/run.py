import sys
import json
from rules import *
from utils.builder import build_rules, build_datatypes



def main(args):
    # 获取股票数据
    data_list = build_datatypes(args)
    # 获取过滤策略
    rules = build_rules(args)
    
    for rule in rules:
        print(">>>>>>>>", rule.name)
        ret = rule(data_list)
        print("-------- pass", ret['pass_rate'])

if __name__ == "__main__":
    cfg_path = sys.argv[1]
    args = json.load(open(cfg_path, "r"))
    main(args)