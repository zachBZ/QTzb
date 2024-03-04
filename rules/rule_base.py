
class Rule:
    def __init__(self, name= "default", args={}):
        self.name = name
        self.args = args
    
    def is_valid(self, data):
        pass
    
    def __call__(self, data_list):
        valid_flag = []
        pass_rate = 0
        for data in data_list:
            if self.is_valid(data):
                pass_rate += 1
                valid_flag.append(True)
            else:
                valid_flag.append(False)
        pass_rate = round(pass_rate / len(data_list), 4)
        return {self.name : valid_flag, "pass_rate": pass_rate}