# 引用文件
from tools.tools import read_yaml, check_dir_create, prepare_nfo_content, get_os, replace_illegal_filename
from config.config import CONFIG_YAML_PATH, AUDIO_STREAM_INFO, VIDEO_STREAM_INFO, VIDEO_QN_INFO, BILIBILI_PATH, \
    FFMPEG_PATH, LOGO_PATH, FM_PATH
# 自带库
import os
from urllib.parse import urlparse
import datetime
import shutil
import subprocess
import copy
import time
# 三方库
import requests as req
from tqdm import tqdm


# 按照user_info创建class对象
class UserInfo:
    """
    UP主的信息对象
    """

    def __init__(self, name: str, mid: int, sex: str, img: str) -> None:
        """
        name: UP名称
        mid: UP mid
        sex: UP性别
        img: UP头像
        """
        self.name = name
        self.mid = mid
        self.sex = sex
        self.img = img


# 集对象
class PageData:
    def __init__(self, title: str, desc: str, start_year: str, start_time: str, pic: str, season: int, episode: int,
                 aid: int, bvid: str, cid: int, name: str) -> None:
        """
        :param title: 集标题
        :param desc: 简介
        :param start_year: 开始时间
        :param start_time: 开始年份
        :param pic: 集封面
        :param season: 集序号
        :param episode: 集序号
        :param aid: 当前集aid
        :param bvid: 当前集bvid
        :param cid: 当前集cid
        :param name: 合集名
        :return: None
        """
        self.title = title
        self.desc = desc
        self.start_year = start_year
        self.start_time = start_time
        self.pic = pic
        self.season = season
        self.episode = episode
        self.aid = aid
        self.bvid = bvid
        self.cid = cid
        self.name = name


# 按照season_data创建class对象
class SeasonData:
    def __init__(self, season_id: str, title: str, pic: str, start_year: str, start_time: str, desc: str,
                 seasonnumber: int, pages: list[PageData], name: str) -> None:
        """
        :param season_id: 季id
        :param title: 季标题
        :param pic: 季封面
        :param start_year: 季始号
        :param start_time: 季始号
        :param desc: 季简介
        :param seasonnumber: 季序号
        :param pages: 集对象
        :param name: 合集名
        :return: None
        """
        self.season_id = season_id
        self.title = title
        self.pic = pic
        self.start_year = start_year
        self.start_time = start_time
        self.desc = desc
        self.seasonnumber = seasonnumber
        self.pages = pages
        self.name = name


# 按照video_info创建class对象
class VideoInfo:
    def __init__(self, bvid: str, aid: str, title: str, dir_name: str, start_time: str, start_year: str, desc: str,
                 user: UserInfo, tags: list, videos: int, is_season: bool, season_data: list[SeasonData],
                 pic: str) -> None:
        """
        :param bvid: 当前链接bvid
        :param aid: 当前链接aid
        :param title: 当前链接title
        :param dir_name: 下载目录名称
        :param start_time: 开始投稿时间
        :param start_year: 开始投稿年份
        :param desc: 简介
        :param user: UP信息，UserInfo对象
        :param tags: 视频tag
        :param videos: 分P数
        :param is_season: 是否为季
        :param  season_data: 季信息,SeasonData对象的列表
        :param pic: 封面图片
        :return:  None
        """
        self.bvid = bvid
        self.aid = aid
        self.title = title
        self.dir_name = dir_name
        self.start_time = start_time
        self.start_year = start_year
        self.desc = desc
        self.user = user
        self.tags = tags
        self.videos = videos
        self.is_season = is_season
        self.season_data = season_data
        self.pic = pic


# 通过输入链接获取ID信息
def get_url_id(url: str) -> str:
    id_list = urlparse(url).path
    if "video" in id_list:
        return id_list.split('/')[-2]
    if "bangumi" in id_list:
        return id_list.split('/')[-1]
    return ""


# 链接判断，判断是否是www.bilibili.con的链接
def is_bilibili_url(url: str) -> bool:
    return "bilibili.com" in urlparse(url).netloc


class Bilibili:
    def __init__(self) -> None:
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67',
            'Origin': 'https://www.bilibili.com',
            'Referer': 'https://www.bilibili.com/',
            'Accept': '*/*'
        }
        self.config = read_yaml(CONFIG_YAML_PATH)
        self.user_info = self.get_user_info()
        check_dir_create(BILIBILI_PATH)

    # 获取B站api
    def get_api(self, url: str):
        headers = self.headers
        headers['Referer'] = url
        headers['Cookie'] = f'SESSDATA={self.config["BILIBILI"]["SESSDATA"]};'
        return req.get(url, headers=headers).json()

    # 检测COOKIE是否过期
    def check_cookie(self) -> bool:
        return self.user_info['code'] == 0

    # 获取B站个人信息
    def get_user_info(self) -> dict:
        url = self.config["BILIBILI"]['API_URL']['USER_INFO']
        return self.get_api(url)

    # 打印个人信息
    def bilibili_user_info_print(self) -> None:
        if self.check_cookie():
            mid = self.user_info["data"]["mid"]
            name = self.user_info["data"]["uname"]
            vipstatus = self.user_info["data"]["vipStatus"]
            current_level = self.user_info["data"]["level_info"]["current_level"]

            os.system("cls")
            print("\t" + "\033[94m=\033[0m" * 100)
            print('\t\033[94m|\033[0m{:^94}\033[94m|\033[0m'.format("B站下载器"))
            print("\t" + "\033[94m=\033[0m" * 100)
            print('\t\033[94m|\033[0m', end="")
            print('{:^19}'.format("ID:" + str(mid)), end="")
            print('\033[94m|\033[0m', end="")
            print('{:^20}'.format("昵称:" + name), end="")
            print('\033[94m|\033[0m', end="")
            print('{:^20}'.format("用户等级:" + str(current_level)), end="")
            print('\033[94m|\033[0m', end="")
            print('{:^20}'.format("会员状态:" + "会员" if vipstatus else "普通"), end="")
            print('\033[94m|\033[0m', end="\n")
            print("\t" + "\033[94m=\033[0m" * 100)
        else:
            os.system("cls")
            print("\t" + "\033[94m=\033[0m" * 100)
            print('\t\033[94m|\033[0m{:^94}\033[94m|\033[0m'.format("B站下载器"))
            print("\t" + "\033[94m=\033[0m" * 100)
            print('\t\033[94m|\033[0m{:^84}\033[94m|\033[0m'.format("用户未登录，仅能下载基础视频"))
            print("\t" + "\033[94m=\033[0m" * 100)

    # 获取视频基本信息
    def get_video_info(self, v_id: str) -> dict:
        video_info_url = f"https://api.bilibili.com/x/web-interface/view/detail?bvid={v_id}"
        if "BV" in v_id:
            video_info_url = f"https://api.bilibili.com/x/web-interface/view/detail?bvid={v_id}"
        if "av" in v_id:
            video_info_url = f"https://api.bilibili.com/x/web-interface/view/detail?aid={v_id}"
        if "ep" in v_id:
            """等待更改url"""
            video_info_url = f"https://api.bilibili.com/x/web-interface/view?ep_id={v_id}"
        return self.get_api(video_info_url)

    # 获取视频tag信息
    def get_video_tag(self, bvid: str, aid: str) -> list:
        """
        https://github.com/498330580/bilibili-API-collect/blob/master/docs/video/tags.md
        """
        url = f"https://api.bilibili.com/x/tag/archive/tags?aid={aid}&bvid={bvid}"
        data = self.get_api(url)['data']
        data_list = []
        for i in data:
            data_list.append(i['tag_name'])
        return data_list

    # 获取视频简介
    def get_video_desc(self, bvid: str, aid: str) -> str:
        url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}&aid={aid}"
        return self.get_api(url)['data']['desc']

    # 整理视频数据
    def video_data_format(self, data: dict) -> VideoInfo:
        """
        文档地址： https://github.com/498330580/bilibili-API-collect/blob/master/docs/video/info.md
        """
        card = data['Card']  # 视频UP主信息 obj
        tags = data['Tags']  # 视频TAG信息 array
        view = data['View']  # 视频基本信息 obj

        "获取用户合集信息： https://api.bilibili.com/x/polymer/web-space/seasons_series_list?mid=370283072&page_num=1" \
        "&page_size=20"
        "合集详情： https://api.bilibili.com/x/polymer/web-space/seasons_archives_list?mid=370283072&season_id=1187255" \
        "&sort_reverse=false&page_num=1&page_size=30"

        tags_list = []  # 创建tag空列表

        # 获取投稿时间
        start_time = datetime.datetime.fromtimestamp(view['ctime']).strftime("%Y-%m-%d")
        start_year = datetime.datetime.fromtimestamp(view['ctime']).strftime("%Y")

        # 视频up信息
        user_info = UserInfo(card['card']['name'], card['card']['mid'], card['card']['sex'], card['card']['face'])

        # 创建空page数据对象
        page_data = PageData(replace_illegal_filename(view['title']), view['desc'], start_year, start_time, view['pic'],
                             1, 1, view['aid'], view['bvid'], view['cid'], replace_illegal_filename(view['title']))

        # 创建空season数据对象
        season_data = SeasonData(view['bvid'], replace_illegal_filename(view['title']), view['pic'], start_year,
                                 start_time, view['desc'], 1, [], replace_illegal_filename(view['title']))

        # 创建基本视频数据
        video_info = VideoInfo(view['bvid'], view['aid'], replace_illegal_filename(view['title']),
                               replace_illegal_filename(view['title']), start_time, start_year, view['desc'], user_info,
                               tags_list, view['videos'], False, [], view['pic'])

        if 'season_id' in view.keys():
            """
            有合集的情况
            """
            season_data.season_id = str(view['season_id'])

            # 获取投稿时间
            start_time = view['ugc_season']['sections'][0]['episodes'][0]['arc']['ctime']
            ctime = datetime.datetime.fromtimestamp(start_time).strftime("%Y-%m-%d")
            yaer = datetime.datetime.fromtimestamp(start_time).strftime("%Y")

            video_info.is_season = True
            # 获取所有视频tag信息
            for i in view['ugc_season']['sections'][0]['episodes']:
                for tag in self.get_video_tag(bvid=i['bvid'], aid=i['aid']):
                    if tag not in tags_list:
                        tags_list.append(tag)
            video_info.tags = tags_list
            video_info.dir_name = replace_illegal_filename(f"{card['card']['name']}_{view['ugc_season']['title']}")
            video_info.start_time = ctime
            video_info.start_year = yaer
            video_info.desc = view['ugc_season']['intro']
            video_info.pic = view['ugc_season']['cover']

            season_data.pic = view['ugc_season']['cover']
            for index_s, season in enumerate(view['ugc_season']['sections']):
                season_data.season_id = season['season_id']
                season_data.title = replace_illegal_filename(season['title'])
                season_data.seasonnumber = index_s + 1
                season_data.desc = replace_illegal_filename(season['title'])
                for index_e, page in enumerate(season['episodes']):
                    page_data.desc = self.get_video_desc(bvid=page['bvid'], aid=page['aid'])
                    page_data.aid = page['aid']
                    page_data.bvid = page['bvid']
                    page_data.cid = page['cid']
                    page_data.season = index_s + 1
                    page_data.episode = index_e + 1

                    page_data.title = replace_illegal_filename(page['title'])
                    page_data.pic = page['arc']['pic']

                    season_data.pages.append(copy.deepcopy(page_data))
                video_info.season_data.append(copy.deepcopy(season_data))

        else:
            """
            没有合集的情况，包括有分p
            """
            # 获取当前视频tag
            for i in tags:
                video_info.tags.append(i['tag_name'])

            if view['videos'] > 1:
                for index, page in enumerate(view['pages']):
                    page_data.episode = page['page']
                    page_data.title = page['part']
                    page_data.pic = page['first_frame']
                    season_data.pages.append(copy.deepcopy(page_data))
                video_info.season_data.append(season_data)
            else:
                page_data.title = "P01"
                page_data.episode = 1
                page_data.pic = view['pages'][0]['first_frame']
                season_data.pages.append(copy.deepcopy(page_data))
                video_info.season_data.append(copy.deepcopy(season_data))

        return video_info

    # 识别视频下载链接
    def video_stream(self, data: dict) -> str:
        """
        文档地处：https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/video/videostream_url.md
        """
        video_qn = self.config["BILIBILI"]["VIDEO_QN"]
        video_bm = self.config["BILIBILI"]["VIDEO_BM"]

        video_bm_list = list(VIDEO_STREAM_INFO.keys())
        video_bm_list = video_bm_list[:video_bm_list.index(str(video_bm)) + 1]
        video_bm_list.reverse()

        video_qn_list = list(VIDEO_QN_INFO.keys())
        video_qn_list = video_qn_list[:video_qn_list.index(str(video_qn)) + 1]
        video_qn_list.reverse()

        if video_qn in data['accept_quality']:
            for stream in data['dash']['video']:
                for bm in video_bm_list:
                    if bm == str(stream['codecid']):
                        return stream['baseUrl']
        else:
            stream_data = []
            for qn in video_qn_list:
                for stream in data['dash']['video']:
                    if qn == str(stream['id']):
                        stream_data.append(stream)
                if stream_data:
                    break
            for bm in video_bm_list:
                for stream in data['dash']['video']:
                    if bm == str(stream['codecid']):
                        return stream['baseUrl']

    # 识别音频下载信息
    def audio_stream(self, data: dict) -> str:
        """
        文档地处：https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/video/videostream_url.md
        """
        audio_ml = self.config["BILIBILI"]["AUDIO_ML"]

        audio_stream_list = list(AUDIO_STREAM_INFO.keys())
        audio_stream_list = audio_stream_list[:audio_stream_list.index(str(audio_ml)) + 1]
        audio_stream_list.reverse()

        for audio_stream in audio_stream_list:
            for audio in data['dash']['audio']:
                if str(audio['id']) == audio_stream:
                    return audio['baseUrl']

        return data['dash']['audio'][0]['baseUrl']

    # 获取视频流信息
    def get_video_stream(self, aid, bvid, cid) -> dict:
        """
        文档：https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/video/videostream_url.md
        """
        url = "https://api.bilibili.com/x/player/playurl?fnver=0&qn=120&fnval=4048&fourk=1&"
        url = url + f"avid={aid}&bvid={bvid}&cid={cid}"
        stream_data = self.get_api(url)['data']
        video_stream = dict(
            清晰度列表=stream_data['accept_description'],
            清晰度id列表=stream_data['accept_quality'],
            音频流=self.audio_stream(stream_data),
            视频流=self.video_stream(stream_data)
        )
        return video_stream

    # 创建视频目录与基础文件
    def create_video_dir(self, data_video: VideoInfo) -> str:
        """
        data_video: 视频数据对象
        """
        print(f"正在创建下载目录与文件：{data_video.dir_name} ({data_video.start_year})")

        # 创建目录
        title_name = f"{data_video.dir_name} ({data_video.start_year})"
        dow_dir_path = os.path.join(BILIBILI_PATH, title_name)
        check_dir_create(dow_dir_path)

        # 整理nfo
        tvshow_path = os.path.join(dow_dir_path, 'tvshow.nfo')
        data_nfo = dict(
            plot=data_video.desc,
            outline=data_video.desc,
            title=data_video.dir_name,
            originaltitle=data_video.dir_name,
            sorttitle=data_video.dir_name,
            premiered=data_video.start_time,
            releasedate=data_video.start_time,
            year=data_video.start_year,
            director=data_video.user.name,
            trailer=f"https://www.bilibili.com/video/{data_video.bvid}",
            genre=data_video.tags,
            mid=data_video.user.mid,
            upimg=data_video.user.img
        )

        # 下载背景
        fanart_path = os.path.join(dow_dir_path, 'fanart.jpg')
        self.download_save(data_video.pic, fanart_path)

        # 处理封面
        poster_path = os.path.join(dow_dir_path, 'poster.jpg')
        shutil.copy(fanart_path, poster_path)

        # 处理季封面
        season_specials_poster = os.path.join(dow_dir_path, 'season_specials-poster.jpg')
        shutil.copy(FM_PATH, season_specials_poster)
        for index, value in enumerate(data_video.season_data):
            season_poster_path = os.path.join(dow_dir_path, f'season{index + 1:02d}-poster.jpg')
            shutil.copy(FM_PATH, season_poster_path)

        # 处理主题图
        thumb_path = os.path.join(dow_dir_path, 'thumb.jpg')
        shutil.copy(fanart_path, thumb_path)

        # 处理logo
        clearlogo_path = os.path.join(dow_dir_path, 'clearlogo.png')
        shutil.copy(LOGO_PATH, clearlogo_path)

        # 保存nfo文件
        prepare_nfo_content('tvshow', data_nfo, tvshow_path)

        return dow_dir_path

    # 处理集文件
    def create_episode_dir(self, episode_data: list[PageData], path: str) -> None:
        """
        episode_data: 集对象
        path: 当前季路径
        """
        # 创廻集目录
        for index, value in enumerate(episode_data):
            # print(f'{value.name} - S{value.season:02d}E{value.episode:02d}                正在下载', end='\r')
            # 处理thumb.jpg
            thumb_path = os.path.join(
                path,
                f'{value.name} - S{value.season:02d}E{value.episode:02d} - {value.title}-thumb.jpg'
            )
            self.download_save(value.pic, thumb_path)

            # 获取视频、音频流信息
            data = self.get_video_stream(value.aid, value.bvid, value.cid)

            # 下载视频流
            video_path = os.path.join(
                path,
                f'{value.name} - S{value.season:02d}E{value.episode:02d} - {value.title}_video') + ".m4s"
            self.download_save(data['视频流'], video_path)

            # 下载音频流
            audio_path = os.path.join(
                path,
                f'{value.name} - S{value.season:02d}E{value.episode:02d} - {value.title}_audio') + ".m4s"
            self.download_save(data['音频流'], audio_path)

            # 输出视频
            video_mp4_path = os.path.join(
                path,
                f'{value.name} - S{value.season:02d}E{value.episode:02d} - {value.title}') + ".mp4"
            # 混流音频与视频并删除未混流文件
            if subprocess.call(
                    [FFMPEG_PATH[get_os()], "-y", "-i", video_path, "-i", audio_path, "-c:v", "copy", "-c:a", "copy",
                     "-f", "mp4", video_mp4_path, "-loglevel", "quiet"]) == 0:
                os.remove(video_path)
                os.remove(audio_path)

            # 整理集nfo文件
            episode_nfo_path = os.path.join(
                path,
                f'{value.name} - S{value.season:02d}E{value.episode:02d} - {value.title}.nfo')
            esisode_nfo_data = dict(
                title=value.title,
                plot=value.desc,
                outline=value.desc,
                aired=value.start_time,
                year=value.start_year,
                season=value.season,
                episode=value.episode,
                aid=value.aid,
                bvid=value.bvid,
                cid=value.cid
            )
            prepare_nfo_content("episodedetails", esisode_nfo_data, episode_nfo_path)
            # print(f'{value.name} - S{value.season:02d}E{value.episode:02d}                下载完成')

    # 创建季目录与文件
    def create_season_dir(self, season_data: list[SeasonData], path: str) -> str:
        """
        seasom_data: 季数据对象
        path: 上级路径
        """
        season_dir_path = path
        # 检查季下载目录
        for index, value in enumerate(season_data):
            print(f"正在处理 Season {index + 1:02d} 信息")
            season_dir_path = os.path.join(path, f'Season {index + 1:02d}')
            check_dir_create(season_dir_path)

            # 处理logo
            logo_path = os.path.join(season_dir_path, 'logo.png')
            shutil.copy(LOGO_PATH, logo_path)

            # 处理thumb
            thumb_path = os.path.join(season_dir_path, 'thumb.jpg')
            self.download_save(value.pic, thumb_path)

            # 处理show
            show_path = os.path.join(season_dir_path, 'show.jpg')
            shutil.copy(thumb_path, show_path)

            # 处理nfo
            nfo_path = os.path.join(season_dir_path, 'season.nfo')
            season_ofo_data = dict(
                plot=value.desc,
                outline=value.desc,
                title=value.title,
                year=value.start_year,
                premiered=value.start_time,
                releasedate=value.start_time,
                sorttitle=value.title,
                seasonnumber=value.seasonnumber
            )
            prepare_nfo_content("season", season_ofo_data, nfo_path)

            # 处理集信息
            self.create_episode_dir(value.pages, season_dir_path)

        return season_dir_path

    # 下载并保存文件
    def download_save(self, url: str, path: str) -> None:
        # 等待1秒 防反扒
        time.sleep(1)
        # 设置下载headers
        headers = self.headers
        headers['Range'] = 'bytes=0-'
        # data = req.get(url, headers=headers, stream=True).content
        name = os.path.basename(path)
        data = req.get(url, headers=headers, stream=True)
        with open(path, 'wb') as f:
            if "m4s" in name:
                for chunk in tqdm(data.iter_content(chunk_size=1024),
                                  total=int(int(data.headers['Content-Length']) / 1024), unit='kb', leave=True,
                                  desc=f'{name} download-->'):
                    if chunk:
                        f.write(chunk)
            else:
                for chunk in data.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            f.close()

    # 下载视频
    def download_video(self, data_video: VideoInfo) -> None:

        # 处理下载目录
        download_video_dir = self.create_video_dir(data_video)

        # 处理季与集
        self.create_season_dir(data_video.season_data, download_video_dir)


# CMD运行下载
def main_cmd():
    b = Bilibili()
    while True:
        b.bilibili_user_info_print()
        print("请输入要下載的视频链接，需要包含BV、AV或EP号(输入0退出)：")
        url = input("").strip()
        if url == "0":
            break
        if is_bilibili_url(url):
            v_id = get_url_id(url)
            if v_id:
                v_data = b.get_video_info(v_id)
                if v_data['code'] == 0:
                    data_video = b.video_data_format(v_data['data'])
                    print(f"{data_video.title}   开始下载")
                    if data_video.is_season:
                        print(
                            f"该视频存在合集:{data_video.dir_name},将下载整个合集视频，如果想下载单一视频请使用GUI模式或者使用油猴脚本。")
                        dy = input('视频存在合集信息，是否订阅合集(y-订阅 n-不订阅)：')
                        if dy == 'y':
                            print(f"订阅合集: {data_video.dir_name} 成功")
                    b.download_video(data_video)
                    print(f"{data_video.title}   下载完成")
                else:
                    print("请求错误")
                    print(v_data['message'])
            else:
                print("链接错误，只能下载链接中包含video、bangumi的视频")
        else:
            print("请输入bilibili.com的地址！")
        input("按任意键后继续...")
        continue


if __name__ == '__main__':
    main_cmd()
