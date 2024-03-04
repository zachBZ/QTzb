from .rule_base import Rule
from utils.builder import RULES

@RULES.register_module()
class RuleTotalInfo(Rule):
    def __init__(self, name="RuleTotalInfo", args={}):
        super().__init__(name, args)
        
    def is_valid(self, data):
        pass