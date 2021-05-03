import json
import shutil
import os

def mkdir(reqs_path, _del = False):
    if os.path.exists(reqs_path):
        if _del:
            shutil.rmtree(reqs_path)
            os.mkdir(reqs_path)
    else:
        os.mkdir(reqs_path)

def my_timer(orig_func):
    @wraps(orig_func)
    def wrapper(*args, **kwargs):
        t1 = time.time()
        result = orig_func(*args, **kwargs)
        t2 = time.time() - t1
        print('{} ran in: {} sec'.format(orig_func.__name__, t2))
        return result
    return wrapper

# @my_timer
def addjson(dic, _key , elementToAdd):
    try:
        dic[_key].append(elementToAdd)
    except:
        dic[_key] = []
        dic[_key].append(elementToAdd)
    return dic

def loadJSON_Convert_to_DF(filepathHTML):

    with open(filepathHTML) as f:
        json_html = json.load(f)
    
    dic_json = {}
    for i in json_html['data']:
        for j in i.keys():
            dic_json = addjson(dic_json, j, i[j])
    
    return dic_json