import pandas as pd
import numpy as np
import os

# ==========================================
# 1. ĐỌC DỮ LIỆU
# ==========================================
thu_muc_data = '../data'
file_giao_thoa = os.path.join(thu_muc_data, 'du_lieu_giao_thoa.json')

print("--- ĐANG ĐỌC DỮ LIỆU ---")
try:
    df = pd.read_json(file_giao_thoa)
    print(f"Thành công! Dữ liệu có {df.shape[0]} dòng (bài hát) và {df.shape[1]} cột.")
except FileNotFoundError:
    print("Lỗi: Không tìm thấy file dữ liệu.")
    exit()

# ==========================================
# 2. KIỂM TRA CHẤT LƯỢNG DỮ LIỆU (DATA PROFILING)
# ==========================================
print("\n--- KIỂM TRA CHẤT LƯỢNG DỮ LIỆU ---")
# Kiểm tra giá trị rỗng (Missing values)
missing_values = df.isnull().sum()
print("Số lượng giá trị rỗng trong mỗi cột:")
print(missing_values[missing_values > 0] if missing_values.any() else "Dữ liệu hoàn hảo, không có giá trị rỗng!")

# Kiểm tra dữ liệu trùng lặp
duplicates = df.duplicated(subset=['title', 'artist']).sum()
print(f"Số lượng bài hát bị trùng lặp: {duplicates}")

# ==========================================
# 3. FEATURE ENGINEERING (TẠO BIẾN MỚI)
# ==========================================
# Tạo biến Engagement Rate (Tỷ lệ chia sẻ / thả tim)
df['engagement_rate'] = df['nct_shares'] / df['nct_hearts'].replace(0, 1)

# ==========================================
# 4. THỐNG KÊ MÔ TẢ & ĐỘ LỆCH (DESCRIPTIVE STATS & SKEWNESS)
# ==========================================
print("\n--- THỐNG KÊ MÔ TẢ (CÁC BIẾN SỐ) ---")
numeric_cols = ['lastfm_listeners', 'nct_hearts', 'nct_shares', 'engagement_rate']
print(df[numeric_cols].describe().round(2))

print("\n--- ĐỘ LỆCH PHÂN PHỐI (SKEWNESS) ---")
# Skewness > 1 hoặc < -1 cho thấy dữ liệu bị lệch rất nhiều (đặc trưng của trending)
print(df[numeric_cols].skew().round(2))

# ==========================================
# 5. BẢNG MA TRẬN TƯƠNG QUAN (CORRELATION MATRIX)
# ==========================================
print("\n--- MA TRẬN TƯƠNG QUAN PEARSON ---")
# Đo lường sự tương quan tuyến tính giữa các biến (-1 đến 1)
corr_matrix = df[numeric_cols].corr(method='pearson')
print(corr_matrix.round(3))

# ==========================================
# 6. TỔNG HỢP THEO NHÓM (GROUPBY & AGGREGATION)
# ==========================================
print("\n--- TOP 5 CA SĨ THỐNG TRỊ (THEO TỔNG LƯỢT NGHE LAST.FM) ---")
top_artists_lastfm = df.groupby('artist')['lastfm_listeners'].sum().sort_values(ascending=False).head(5)
print(top_artists_lastfm)

print("\n--- TOP 5 CA SĨ ĐƯỢC YÊU THÍCH NHẤT (THEO TỔNG LƯỢT TIM NCT) ---")
top_artists_nct = df.groupby('artist')['nct_hearts'].sum().sort_values(ascending=False).head(5)
print(top_artists_nct)

# ==========================================
# 7. PHÁT HIỆN NGOẠI LAI (OUTLIER DETECTION BẰNG IQR)
# ==========================================
print("\n--- PHÁT HIỆN CÁC SIÊU HIT (OUTLIERS) BẰNG PHƯƠNG PHÁP IQR ---")
# Tìm các bài hát có lượt tim trên NCT cao đột biến
Q1 = df['nct_hearts'].quantile(0.25)
Q3 = df['nct_hearts'].quantile(0.75)
IQR = Q3 - Q1
upper_bound = Q3 + 1.5 * IQR

outliers_nct = df[df['nct_hearts'] > upper_bound]
print(f"Ngưỡng ngoại lai trên của nct_hearts là: {upper_bound:.2f}")
print(f"Tìm thấy {len(outliers_nct)} bài hát 'siêu hit' phá vỡ giới hạn bình thường:")
print(outliers_nct[['title', 'artist', 'nct_hearts']].sort_values(by='nct_hearts', ascending=False))