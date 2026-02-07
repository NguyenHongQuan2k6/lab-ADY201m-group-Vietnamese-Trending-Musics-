import csv
import requests
from bs4 import BeautifulSoup
import time 
import re 
import get_information_web
from datetime import datetime 
import filter_data_in_each_songs as code_in_each_songs

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
url_get = 'https://www.nhaccuatui.com/chart/1-1-d33-2026'

r_main_page = requests.get(url_get, headers=headers)

if r_main_page.status_code == 200:
    soup = BeautifulSoup(r_main_page.text, 'html.parser')
    
    # Lấy ngày cập nhật
    ngay_cap_nhat_bxh = "N/A"
    meta_tag = soup.find('meta', attrs={'name': 'description'})
    if meta_tag:
        tim_ngay = re.search(r'\d{2}/\d{2}/\d{4}', meta_tag.get('content', ''))
        if tim_ngay:
            ngay_cap_nhat_bxh = tim_ngay.group(0)

    list_top_trending = []
    music = soup.find_all('div', class_='song-item')
    list_links = code_in_each_songs.danh_sach_ket_qua

    gio_co_dinh = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"--> Bắt đầu quét lúc: {gio_co_dinh}")

    # =================================================================
    # THAY ĐỔI: Dùng vòng lặp theo số đếm (range) thay vì enumerate
    # =================================================================
    # range(len(music)): Tạo ra dãy số từ 0 đến hết danh sách (0, 1, 2...)
    for index in range(len(music)):
        song = music[index] # Tự lấy bài hát ra dựa vào số thứ tự
        
        try:
            song_name = song.find('div', class_='song-name').text.strip()
            
            # Xử lý hạng (rank)
            rank_tag = song.find('span', class_="idx")
            song_rank = rank_tag.text.strip() if rank_tag else str(index + 1)
            
            artist = song.find('span', class_="name-text").text.strip()
            
            # Lấy link dựa vào số thứ tự index
            url_song = "N/A"
            if index < len(list_links):
                url_song = list_links[index]

            # Biến chứa dữ liệu
            view_hien_thi = "0" 
            share_hien_thi = "0"
            
            if url_song != "N/A" and url_song.startswith("http"):
                try:
                    r_detail = requests.get(url_song, headers=headers, timeout=5)
                    if r_detail.status_code == 200:
                        # Regex lấy số liệu thực tế (52k, 1k)
                        
                        # 1. Lượt Nghe
                        tim_view = re.search(r'(\d+),"http://log4x', r_detail.text)
                        if tim_view:
                            view_hien_thi = tim_view.group(1)

                        # 2. Lượt Share
                        tim_share = re.search(r'flac.*?download=true".*?,\s*(\d+),\s*(\d+)(?:,\s*(\d+))?', r_detail.text)
                        if tim_share:
                            cac_so = [int(s) for s in tim_share.groups() if s is not None]
                            if cac_so:
                                share_hien_thi = str(max(cac_so))
                    
                except Exception as e:
                    print(f"Lỗi trang con: {e}")

            song_dict = {
                "Time": gio_co_dinh, 
                "Date Updated": ngay_cap_nhat_bxh,
                "Song name": song_name,
                "Song rank": song_rank,
                "Artist": artist,
                "Link of song": url_song,
                "Views (Real)": view_hien_thi,
                "Shares (Real)": share_hien_thi
            }            
            list_top_trending.append(song_dict)
            
            print(f"[{index+1}] {song_name} | View: {view_hien_thi} | Share: {share_hien_thi}")

        except AttributeError:
            continue

else:
    print("This site can't be reached.")

# --- GHI FILE ---
filename = "data_for_trending_song.csv"
if list_top_trending:
    fields = ["Time", "Date Updated", "Song name", "Song rank", "Artist", "Link of song", "Views (Real)", "Shares (Real)"] 
    with open(filename, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(list_top_trending)
    print(f"Lưu thành công vào file {filename}")
else:
    print("There is no data available to write to the file.")