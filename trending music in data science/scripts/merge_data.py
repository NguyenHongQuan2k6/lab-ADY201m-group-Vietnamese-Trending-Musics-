import json
import os
import pandas as pd  # Thư viện mới thêm vào để xếp hạng nhanh chóng
from pymongo import MongoClient

# ============================================================
# 1. CẤU HÌNH ĐƯỜNG DẪN FILE (Giữ nguyên)
# ============================================================
thu_muc_data = '../data'
file_lastfm = os.path.join(thu_muc_data, 'du_lieu_lastfm.json')
file_nct = os.path.join(thu_muc_data, 'du_lieu_nct.json')
file_giao_thoa = os.path.join(thu_muc_data, 'du_lieu_giao_thoa.json')

# ============================================================
# 2. ĐỌC DỮ LIỆU TỪ CÁC FILE JSON (Giữ nguyên)
# ============================================================
print("Đang đọc dữ liệu từ Last.fm và Nhaccuatui...")
try:
    with open(file_lastfm, 'r', encoding='utf-8') as f:
        data_lastfm = json.load(f)
        
    with open(file_nct, 'r', encoding='utf-8') as f:
        data_nct = json.load(f)
except FileNotFoundError:
    print(" Lỗi: Không tìm thấy file dữ liệu! Hãy đảm bảo bạn đã chạy 2 file quét web trước.")
    exit()

# --- Giữ mốc "Ban đầu" để tính score_growth ---
dict_diem_da_luu = {}
if os.path.exists(file_giao_thoa):
    try:
        with open(file_giao_thoa, 'r', encoding='utf-8') as f:
            du_lieu_cu = json.load(f)
            for item in du_lieu_cu:
                key = f"{item['title']} - {item['artist']}"
                dict_diem_da_luu[key] = item.get('initial_score', 0)
    except Exception:
        pass 

# ============================================================
# 3. TÌM PHẦN GIAO THOA VÀ TÍNH ĐIỂM SỐ (Giữ nguyên cấu trúc)
# ============================================================
print("\n--- ĐANG XỬ LÝ LỌC PHẦN GIAO THOA VÀ TÍNH TOÁN CHỈ SỐ ---")

dict_lastfm = {}
for bai in data_lastfm:
    khoa_id = f"{bai['title']} - {bai['artist']}"
    dict_lastfm[khoa_id] = bai

danh_sach_giao_thoa = []

for bai_nct in data_nct:
    khoa_id = f"{bai_nct['title']} - {bai_nct['artist']}"
    
    if khoa_id in dict_lastfm:
        bai_lastfm = dict_lastfm[khoa_id]
        
        # Bù đắp dữ liệu: Lấy giá trị lớn nhất
        listeners_chuan = max(bai_nct.get('lastfm_listeners', 0), bai_lastfm.get('lastfm_listeners', 0))
        hearts_chuan = max(bai_nct.get('nct_hearts', 0), bai_lastfm.get('nct_hearts', 0))
        shares_chuan = max(bai_nct.get('nct_shares', 0), bai_lastfm.get('nct_shares', 0))
        
        # Tính toán điểm số
        tong_diem_hien_tai = listeners_chuan + (50 * hearts_chuan) + (500 * shares_chuan)
        diem_ban_dau = dict_diem_da_luu.get(khoa_id, tong_diem_hien_tai) if dict_diem_da_luu.get(khoa_id, 0) > 0 else tong_diem_hien_tai
        diem_tang_them = tong_diem_hien_tai - diem_ban_dau
        
        # Lấy ý tưởng từ EDA: Tỷ lệ tương tác (Share / Heart)
        ty_le_tuong_tac = shares_chuan / hearts_chuan if hearts_chuan > 0 else 0
        
        link_chuan = bai_nct['song_url'] if bai_nct['song_url'] != "N/A" else bai_lastfm['song_url']
        
        # Tạo bản ghi hoàn chỉnh
        bai_hoan_chinh = {
            "title": bai_nct['title'],
            "artist": bai_nct['artist'],
            "platform": "Last.fm & Nhaccuatui",
            "trending_date": bai_nct['trending_date'],
            "song_url": link_chuan,
            "lastfm_listeners": listeners_chuan,
            "nct_hearts": hearts_chuan,
            "nct_shares": shares_chuan,
            "total_score": tong_diem_hien_tai,
            "initial_score": diem_ban_dau,
            "score_growth": diem_tang_them,
            "engagement_rate": ty_le_tuong_tac # Cột EDA
        }
        
        danh_sach_giao_thoa.append(bai_hoan_chinh)

# ============================================================
# 4. MỚI: TÍNH TOÁN THỨ HẠNG (RANK) TRƯỚC KHI LƯU
# ============================================================
if danh_sach_giao_thoa:
    print("\n--- ĐANG XẾP HẠNG BÀI HÁT DỰA TRÊN ĐIỂM SỐ VÀ EDA ---")
    df = pd.DataFrame(danh_sach_giao_thoa)
    
    # Xếp hạng theo độ phổ biến (Total Score)
    df = df.sort_values(by='total_score', ascending=False).reset_index(drop=True)
    df['rank_total'] = df.index + 1
    
    # Xếp hạng theo xu hướng tăng trưởng (Score Growth)
    df = df.sort_values(by='score_growth', ascending=False).reset_index(drop=True)
    df['rank_growth'] = df.index + 1
    
    # Chuyển đổi ngược lại thành danh sách để tiếp tục các bước lưu của bạn
    danh_sach_giao_thoa = df.to_dict('records')

print(f" Tìm thấy {len(danh_sach_giao_thoa)} bài hát chung và đã cập nhật điểm số cùng thứ hạng!")

# ============================================================
# 5. LƯU RA FILE JSON RIÊNG (Giữ nguyên)
# ============================================================
with open(file_giao_thoa, 'w', encoding='utf-8') as f:
    json.dump(danh_sach_giao_thoa, f, ensure_ascii=False, indent=4)
print(f" Đã lưu file giao thoa tại: {file_giao_thoa}")

# ============================================================
# 6. ĐƯA DỮ LIỆU SẠCH VÀO MONGODB (Giữ nguyên hoàn toàn code cũ)
# ============================================================
if danh_sach_giao_thoa:
    print("\n--- ĐANG ĐƯA DỮ LIỆU VÀO MONGODB ---")
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['trending_music_in_Vietnam_db']
        collection = db['bang_xep_hang_giao_thoa'] 
        
        # CODE CỦA BẠN: Xóa toàn bộ dữ liệu cũ và chèn dữ liệu mới
        collection.delete_many({})
        collection.insert_many(danh_sach_giao_thoa)
        print(" Hoàn tất!")
        
    except Exception as e:
        print(f" Có lỗi khi kết nối MongoDB: {e}")