import requests
import json
import os
from datetime import datetime

# ============================================================
# CẤU HÌNH & LẤY DỮ LIỆU TỪ LAST.FM (DỰA TRÊN NHACCUATUI)
# ============================================================
LASTFM_API_KEY = "1d3859b87ffb2793f01200613e64bda5"

# Đường dẫn đến file Nhaccuatui đã lưu trước đó
thu_muc_luu = r'C:\Users\hongq\OneDrive\Desktop\Python\ADY201m\lab\trending music in data science\data'
file_nct = os.path.join(thu_muc_luu, 'du_lieu_nct.json')
file_lastfm = os.path.join(thu_muc_luu, 'du_lieu_lastfm.json')

# 1. Đọc danh sách mục tiêu từ file Nhaccuatui
danh_sach_nct = []
try:
    with open(file_nct, 'r', encoding='utf-8') as f:
        danh_sach_nct = json.load(f)
except FileNotFoundError:
    print("Không tìm thấy file Nhaccuatui! Vui lòng chạy file webcrawling_nhaccuatui.py trước.")
    exit()

list_top_trending = []
gio_co_dinh = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

print(f"Bắt đầu tra cứu {len(danh_sach_nct)} bài hát từ Nhaccuatui trên hệ thống Last.fm...")

# 2. Dùng vòng lặp đem từng bài đi hỏi Last.fm
for bai in danh_sach_nct:
    song_name = bai['title']
    artist = bai['artist']
    
    try:
        # Gọi API lấy thông tin đích danh bài hát (Có bật autocorrect để tự sửa lỗi chính tả)
        res = requests.get(
            "http://ws.audioscrobbler.com/2.0/",
            params={
                "method": "track.getInfo",
                "api_key": LASTFM_API_KEY,
                "artist": artist,
                "track": song_name,
                "autocorrect": 1, 
                "format": "json"
            },
            timeout=10
        )
        data = res.json()
        
        listeners = 0
        song_url_lastfm = "N/A"
        
        # Kiểm tra xem Last.fm có bài này không
        if "track" in data and "listeners" in data["track"]:
            listeners = int(data["track"]["listeners"])
            song_url_lastfm = data["track"].get("url", "N/A")
            
        # Chỉ lưu vào danh sách nếu Last.fm thực sự có người nghe bài này
        if listeners > 0:
            song_dict = {
                "title": song_name,                     
                "artist": artist,                       
                "platform": "Last.fm",                  
                "trending_date": gio_co_dinh,           
                "song_url": song_url_lastfm,                   
                "lastfm_listeners": listeners,
                "nct_hearts": 0,
                "nct_shares": 0
            }
            list_top_trending.append(song_dict)
            print(f" -> Đã tìm thấy: {song_name} ({listeners} lượt nghe)")
        else:
            print(f" -> Bỏ qua: {song_name} (Không có trên Last.fm)")
            
    except Exception as e:
        print(f" -> Lỗi mạng khi tìm bài {song_name}")
        continue

# ============================================================
# LƯU DỮ LIỆU RA FILE JSON 
# ============================================================
print("\n--- ĐANG LƯU DỮ LIỆU TỪ LAST.FM ---")
os.makedirs(thu_muc_luu, exist_ok=True)

with open(file_lastfm, 'w', encoding='utf-8') as f:
    json.dump(list_top_trending, f, ensure_ascii=False, indent=4)
    
print(f"Hoàn tất! Đã tra cứu thành công và lưu {len(list_top_trending)} bài hát vào '{file_lastfm}'")