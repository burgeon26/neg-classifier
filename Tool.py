def read_from_file(path):
    with open(path,'r') as f:
        return f.readlines()
def foreach(function,iterator):
    for item in iterator:
        function(item)
def get_negative_list():
    lines = read_from_file('negative.txt')
    lines = map(lambda x: x.replace('\n', '').replace('\ufeff', ''), lines)
    return list(lines)
def get_positive_list():
    lines = read_from_file('positive.txt')
    lines = map(lambda x: x.replace('\n', '').replace('\ufeff', ''), lines)
    return list(lines)
def clear(ori_str:str):
    return ori_str.replace('(','').replace(')','').replace('［','').replace('］','').replace(' ','')