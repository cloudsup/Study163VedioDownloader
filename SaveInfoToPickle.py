import pickle

def save_info(file_name, info):
    try:
        with open(file_name, 'wb') as f:
            pickle.dump(info, f)
    except:
        print("保存文件：" + file_name + "失败！")

