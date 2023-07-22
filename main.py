import os
import sys
from config.config import CONFIG_YAML_PATH, DATA_PATH, DOW_PATH
from tools.tools import check_file, check_dir_create
from bilibili import Bilibili

# 设定工作目录为当前脚本目录
jaoben_path = os.path.abspath(os.path.dirname(sys.argv[0])) # 当前脚本目录
os.chdir(jaoben_path)   # 设定工作目录为脚本目录


# 检测配置文件是否存在
def config_file_check():
    check_dir_create(DATA_PATH)
    check_dir_create(DOW_PATH)
    if not check_file(CONFIG_YAML_PATH):
        print("配置文件不存在，已创建空白配置文件")
        return False


def main():
    if not config_file_check():
        return
    
    b = Bilibili()

    # 验证cookie是否失效
    if not b.check_cookie():
        return


if __name__ == "__main__":
    main()
