# encoding=utf-8
# python3

import requests
import json
import os
from tools import (download_music_file, download_album_pic, modify_mp3)


class Sonimei(object):
    def download_song(self, song_title, song_author, song_album, music_folder, pic_folder, type):
        search_result = self.search(song_title, song_author, type)
        del search_result['lrc']
        print(search_result)

        artists = search_result['author'].split(',')
        print(artists)
        file_name = ''
        for artist in search_result['author'].split(','):
            file_name = file_name + artist + ','
        file_name = file_name[:-1]
        if len(file_name) > 50:
            # 如果艺术家过多导致文件名过长，则文件名的作者则为第一个艺术家的名字
            print('Song: %s\'s name too long, cut' % search_result['title'])
            file_name = artists[0] + ' - ' + search_result['title']
        else:
            file_name = file_name + ' - ' + search_result['title']
        print(file_name)
        file_path = os.path.join(music_folder, file_name + '.mp3')
        download_music_file(search_result['url'], file_path)
        pic_path = os.path.join(pic_folder, file_name + '.jpg')
        download_album_pic(search_result['pic'], pic_path)

        music_info = {
            'title': search_result['title'],
            'artists': search_result['author'].replace(',', ';'),
            'pic_path': pic_path
        }
        if song_album:
            music_info['album'] = song_album
        modify_mp3(file_path, music_info)

    def search(self, song_title, song_author, type, retrytimes=3):
        target_url = 'http://music.sonimei.cn/'
        fake_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'max-age=0',
            'user-agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                           ' (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36'),
            'Referer': 'http://music.sonimei.cn/?name=%s%s&type=%s' % (song_title.encode('utf-8'), song_author.encode('utf-8'), type),
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'http://music.sonimei.cn',
            'X-Requested-With': 'XMLHttpRequest',
            'Host': 'music.sonimei.cn'
        }
        json_ret = None
        data = {
            'input': song_title + ' ' + song_author,
            'filter': 'name',
            'type': type,
            'page': 1
        }
        while retrytimes > 0:
            try:
                response = requests.post(target_url, data=data, headers=fake_headers)
                response.encoding = 'utf-8'
                json_ret = json.loads(response.text)
                if json_ret['code'] == 200:
                    return json_ret['data'][0]
            except IndexError:
                retrytimes = retrytimes - 1
        return None


def xiami_search(song_title, song_author, retrytimes=3):
    # TODO
    # 暂时不知道怎么把虾米的api本地化，没有找到可行的Python参考项目
    target_url = 'http://music-api-jwzcyzizya.now.sh/api/search/song/xiami?&limit=1&page=1&key=%s-%s/' % (song_title, song_author)

    fake_headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'max-age=0',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    json_ret = None
    while retrytimes > 0:
        try:
            json_ret = json.loads(requests.get(target_url, headers=fake_headers).text)
            break
        except:
            retrytimes = retrytimes - 1
    print(json_ret)
    if json_ret and json_ret['success']:
        return json_ret['songList'][0]['file']
    else:
        return ''