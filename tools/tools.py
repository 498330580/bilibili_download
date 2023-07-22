import yaml
import os
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import datetime
import platform

# 读取yaml文件
def read_yaml(filename):
    with open(filename,"r",encoding="utf-8") as f:
        return yaml.load(f, Loader=yaml.FullLoader)


# 写入yaml文件
def write_yaml(filename,data):
    with open(filename,"w",encoding="utf-8") as f:
        return yaml.dump(data,f)
    

# 检测文件夹是否存在，不存在则创建
def check_dir_create(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    return True

# 检测config.yaml文件是否存在，如消息不存在则创建
def check_file(filename):
    if not os.path.exists(filename):
        data = {
            'COOKIE': {'SESSDATA': ''},
            'API_URL':{
                'USER_INFO': 'https://api.bilibili.com/nav',
            }
        }
        write_yaml(filename, data)
        return False
    return True

# 保存nfo文件内容
def prepare_nfo_content(nfo_name: str, data: dict, path: str):
    """
    nfo_name: nfo文件主标签名
    data: nfo文件数据内容
    path: nfo文件保存路径
    """
    e_season = ET.Element(nfo_name)

    for key, value in data.items():
        if key == 'genre':
            for genre in value:
                ET.SubElement(e_season, 'genre').text = genre
        else:
            ET.SubElement(e_season, key).text = str(value)

    if nfo_name == 'tvshow':
        ET.SubElement(e_season, 'studio').text = 'Bilibili'
        ET.SubElement(e_season, 'displayorder').text = 'aired'
        ET.SubElement(e_season, 'season').text = '-1'
        ET.SubElement(e_season, 'episode').text = '-1'
    
    ET.SubElement(e_season, 'lockdata').text = 'false'
    ET.SubElement(e_season, 'dateadded').text = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    data_nfo = BeautifulSoup(ET.tostring(e_season), 'xml').prettify()

    with open(path, 'wb') as f:
            f.write(data_nfo.encode('utf-8'))

# 识别操作系统
def get_os():
    sys_platform = platform.platform().lower()
    if "windows" in sys_platform:
        return "Windows"
    elif "macos" in sys_platform:
        return "Mac"
    elif "linux" in sys_platform:
        return "Linux"
    else:
        print("Windows")

# 替换不合规文件名
def replace_illegal_filename(filename: str) -> str:
    return filename.replace("/", "_").replace("\\", "_").replace("?", "_").replace("*", "_").replace(":", "_").replace("\"", "_").replace("<", "_").replace(">", "_").replace("|", "_").replace(" ", "")

if __name__ == "__main__":
    print(read_yaml("./data/config.yaml"))
