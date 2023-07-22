import os, sys


# 当前文件目录
_PATH = os.path.abspath(os.path.dirname(sys.argv[0]))

# 拼接config目录路径
DATA_PATH = os.path.join(_PATH, "config")

# 拼接下载目录
DOW_PATH = os.path.join(_PATH, "download")

# 拼接bilibili下载目录
BILIBILI_PATH = os.path.join(DOW_PATH, "bilibili")

# 拼接config.yaml文件路径
CONFIG_YAML_PATH = os.path.join(DATA_PATH, "config.yaml")

# ffmpeg路径
FFMPEG_PATH = dict(
    Windows = os.path.join(_PATH, "tools", "ffmpeg.exe"),
    Linux = os.path.join(_PATH, "tools", "ffmpeg"),
    Mac = os.path.join(_PATH, "tools", "ffmpeg_mac"),
)

# bilibili_logo文件路径
LOGO_PATH = os.path.join(_PATH, "data", "BILIBILI_LOGO.png")

# bilibili_fm文件路径
FM_PATH = os.path.join(_PATH, "data", "bilibili_fm.jpg")

# 视频伴音音质代码
AUDIO_STREAM_INFO = {
    "30216": "64k",
    "30232": "132k",
    "30280": "192k",
    "30250": "杜比",
    "30251": "Hi-Res无损"
}

# 视频编码代码
VIDEO_STREAM_INFO = {
    "7": "AVC 编码",
    "12": "HEVC 编码",
    "13": "AV1 编码"
}

# 视频清晰度标识
VIDEO_QN_INFO = {
    "6": "240P 极速",
    "16": "360P 流畅",
    "32": "480P 清晰",
    "64": "720P 高清",
    "74": "720P60 高帧率",
    "80": "1080P 高清",
    "112": "1080P+ 高码率",
    "116": "1080P60 高帧率",
    "120": "4K 超清",
    "125": "HDR 真彩色",
    "126": "杜比视界",
    "127": "8K 超高清",
}
