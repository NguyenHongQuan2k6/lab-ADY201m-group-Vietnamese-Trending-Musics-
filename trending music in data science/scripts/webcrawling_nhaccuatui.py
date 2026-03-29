import requests
from bs4 import BeautifulSoup
import re 
from datetime import datetime 
import filter_data_in_each_songs as code_in_each_songs 
import json 
import os # Đã thêm thư viện os để quản lý thư mục

# ============================================================
# CẤU HÌNH & LẤY DỮ LIỆU CHỈ TỪ NHACCUATUI
# ============================================================
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
url_get = 'https://www.nhaccuatui.com/chart/1-5-d86-2026'
r_main_page = requests.get(url_get, headers=headers)

list_top_trending = []

if r_main_page.status_code == 200:
    soup = BeautifulSoup(r_main_page.text, 'html.parser')
    music = soup.find_all('div', class_='song-item')
    list_links = code_in_each_songs.danh_sach_ket_qua

    gio_co_dinh = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"Bắt đầu quét Nhaccuatui lúc: {gio_co_dinh}")
    print("Đang tìm kiếm dữ liệu chi tiết... (Sẽ mất khoảng vài giây)")

    for index in range(len(music)):
        song = music[index] 
        try:
            raw_song_name = song.find('div', class_='song-name').text.strip()
            raw_artist = song.find('span', class_="name-text").text.strip()
            
            song_name = re.sub(r'(\(|\[).*?(official|lyric|audio|video|mv|remix).*?(\)|\])', '', raw_song_name, flags=re.IGNORECASE)
            artist = str(raw_artist)
            
            song_name = song_name.lower()
            artist = artist.lower()

            song_name = re.sub(r'[^\w\s]', '', song_name)
            artist = re.sub(r'[^\w\s]', '', artist)

            song_name = re.sub(r'\s+', ' ', song_name).strip()
            artist = re.sub(r'\s+', ' ', artist).strip()

            the_a_chua_link = song.find('div', class_='song-name').find('a', href=True) if song.find('div', class_='song-name') else None
            if the_a_chua_link:
                url_song = the_a_chua_link['href']
            else:
                url_song = list_links[index] if index < len(list_links) else "N/A"

            heart_hien_thi = 0 
            share_hien_thi = 0
            
            if url_song != "N/A" and url_song.startswith("http"):
                try:
                    r_detail = requests.get(url_song, headers=headers, timeout=5)
                    if r_detail.status_code == 200:
                        tim_heart = re.search(r'(\d+),"http://log4x', r_detail.text)
                        if tim_heart:
                            heart_hien_thi = int(tim_heart.group(1))
                            
                        tim_share = re.search(r'(?i)("share"|"shares"|"share_count"|"total_share"|"shareCount")\s*:\s*"?(\d+)', r_detail.text)
                        if tim_share:
                            share_hien_thi = int(tim_share.group(2))
                        else:
                            soup_detail = BeautifulSoup(r_detail.text, 'html.parser')
                            share_tags = soup_detail.find_all(lambda t: t.has_attr('class') and any('share' in c.lower() for c in t.get('class', [])))
                            for tag in share_tags:
                                text_val = tag.text.strip().replace(',', '').replace('.', '')
                                if text_val.isdigit():
                                    share_hien_thi = int(text_val)
                                    break
                except: pass

            song_dict = {
                "title": song_name,                     
                "artist": artist,                       
                "platform": "Nhaccuatui",               
                "trending_date": gio_co_dinh,           
                "song_url": url_song,                   
                "lastfm_listeners": 0,
                "nct_hearts": heart_hien_thi,
                "nct_shares": share_hien_thi
            }            
            list_top_trending.append(song_dict)
        except AttributeError:
            continue

    # ============================================================
    # LƯU DỮ LIỆU RA FILE JSON ĐỂ TỔNG HỢP SAU
    # ============================================================
    print("\n--- ĐANG LƯU DỮ LIỆU TỪ NHACCUATUI ---")
    
    # Tạo thư mục 'data' nếu chưa có
    thu_muc_luu = r'C:\Users\hongq\OneDrive\Desktop\Python\ADY201m\lab\trending music in data science\data'
    os.makedirs(thu_muc_luu, exist_ok=True)

    # Gắn thư mục 'data' vào tên file
    ten_file = os.path.join(thu_muc_luu, 'du_lieu_nct.json')

    with open(ten_file, 'w', encoding='utf-8') as f:
        json.dump(list_top_trending, f, ensure_ascii=False, indent=4)
    print(f"Hoàn tất! Đã lưu {len(list_top_trending)} bài hát vào '{ten_file}'")