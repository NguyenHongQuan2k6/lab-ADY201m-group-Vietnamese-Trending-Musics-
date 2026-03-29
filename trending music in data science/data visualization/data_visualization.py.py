import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ==========================================
# 1. CẤU HÌNH VÀ ĐỌC DỮ LIỆU
# ==========================================
thu_muc_data = '../data'
thu_muc_chart = '../charts' # Thư mục lưu biểu đồ
file_giao_thoa = os.path.join(thu_muc_data, 'du_lieu_giao_thoa.json')

# Tạo thư mục lưu ảnh nếu chưa có
if not os.path.exists(thu_muc_chart):
    os.makedirs(thu_muc_chart)

print("--- ĐANG ĐỌC DỮ LIỆU ĐỂ TRỰC QUAN HÓA ---")
try:
    df = pd.read_json(file_giao_thoa)
    print(f"Thành công! Bắt đầu vẽ biểu đồ cho {df.shape[0]} bài hát...")
except FileNotFoundError:
    print("Lỗi: Không tìm thấy file dữ liệu giao thoa.")
    exit()

# Thiết lập style cho biểu đồ đẹp hơn
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({'font.size': 12}) # Cỡ chữ dễ nhìn cho slide

# ==========================================
# BIỂU ĐỒ 1: TOP 10 BÀI HÁT THỊNH HÀNH NHẤT (THEO TOTAL SCORE)
# Ý nghĩa: Chỉ ra Bảng xếp hạng Top bài hát đình đám nhất hiện tại.
# ==========================================
plt.figure(figsize=(12, 6))
top_10_songs = df.sort_values('total_score', ascending=False).head(10)

# Tạo nhãn gộp Tên bài hát + Ca sĩ để dễ nhìn
top_10_songs['song_label'] = top_10_songs['title'] + " - " + top_10_songs['artist']

sns.barplot(data=top_10_songs, x='total_score', y='song_label', hue='song_label', legend=False, palette='viridis')
plt.title('Top 10 Bài Hát Trending Có Điểm Tổng (Total Score) Cao Nhất', fontsize=16, fontweight='bold')
plt.xlabel('Tổng Điểm (Listeners + 50*Hearts + 500*Shares)', fontsize=12)
plt.ylabel('Bài Hát', fontsize=12)
plt.tight_layout()
plt.savefig(os.path.join(thu_muc_chart, '1_top_10_songs.png'), dpi=300)
plt.close()

# ==========================================
# BIỂU ĐỒ 2: TOP 5 CA SĨ THỐNG TRỊ LƯỢT NGHE LAST.FM & TYM NCT
# Ý nghĩa: Ai đang là người dẫn dắt xu hướng âm nhạc?
# ==========================================
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Top 5 Last.fm
top_artists_lastfm = df.groupby('artist')['lastfm_listeners'].sum().sort_values(ascending=False).head(5).reset_index()
sns.barplot(data=top_artists_lastfm, x='lastfm_listeners', y='artist', hue='artist', legend=False, ax=axes[0], palette='Blues_r')
axes[0].set_title('Top 5 Ca Sĩ Kéo Tương Tác Khủng (Last.fm Listeners)', fontsize=14, fontweight='bold')
axes[0].set_xlabel('Tổng Lượt Nghe', fontsize=12)
axes[0].set_ylabel('')

# Top 5 Nhaccuatui Hearts
top_artists_nct = df.groupby('artist')['nct_hearts'].sum().sort_values(ascending=False).head(5).reset_index()
sns.barplot(data=top_artists_nct, x='nct_hearts', y='artist', hue='artist', legend=False, ax=axes[1], palette='Reds_r')
axes[1].set_title('Top 5 Ca Sĩ Sở Hữu Fandom Mạnh Nhất (NCT Hearts)', fontsize=14, fontweight='bold')
axes[1].set_xlabel('Tổng Lượt Thả Tim', fontsize=12)
axes[1].set_ylabel('')

plt.tight_layout()
plt.savefig(os.path.join(thu_muc_chart, '2_top_artists.png'), dpi=300)
plt.close()

# ==========================================
# BIỂU ĐỒ 3: PHÁT HIỆN "SIÊU HIT" BẰNG BOXPLOT (OUTLIERS CỦA NCT HEARTS)
# Ý nghĩa: Khẳng định sự tồn tại của các bài hát viral đột biến so với mặt bằng chung
# ==========================================
plt.figure(figsize=(10, 4))
sns.boxplot(x=df['nct_hearts'], color='coral', flierprops=dict(markerfacecolor='r', marker='o', markersize=8))
plt.title('Phân Bố Lượt Thả Tim NCT: Phát Hiện Cực Trị (Siêu Hit)', fontsize=16, fontweight='bold')
plt.xlabel('Số Lượt Thả Tim (NCT Hearts)', fontsize=12)

# Chú thích thêm thông tin về Outlier (đường ranh giới IQR)
Q1 = df['nct_hearts'].quantile(0.25)
Q3 = df['nct_hearts'].quantile(0.75)
IQR = Q3 - Q1
upper_bound = Q3 + 1.5 * IQR
plt.axvline(upper_bound, color='red', linestyle='--', linewidth=2, label=f'Ngưỡng Siêu Hit: {upper_bound:.0f}')
plt.legend()

plt.tight_layout()
plt.savefig(os.path.join(thu_muc_chart, '3_super_hits_outliers.png'), dpi=300)
plt.close()

# ==========================================
# BIỂU ĐỒ 4: SỰ TƯƠNG QUAN GIỮA CÁC CHỈ SỐ (HEATMAP)
# Ý nghĩa: Tim nhiều có đồng nghĩa với việc Share nhiều hay Nghe nhiều không?
# ==========================================
plt.figure(figsize=(8, 6))
numeric_cols = ['lastfm_listeners', 'nct_hearts', 'nct_shares', 'total_score', 'engagement_rate']
corr_matrix = df[numeric_cols].corr(method='pearson')

sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5)
plt.title('Ma Trận Tương Quan Các Chỉ Số Âm Nhạc', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(thu_muc_chart, '4_correlation_heatmap.png'), dpi=300)
plt.close()

# ==========================================
# BIỂU ĐỒ 5: TỶ LỆ TƯƠNG TÁC (ENGAGEMENT RATE) SO VỚI TỔNG ĐIỂM
# Ý nghĩa: Những bài hát điểm cao nhất có phải là những bài có tỷ lệ chia sẻ/tim cao nhất?
# ==========================================
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='total_score', y='engagement_rate', 
                size='nct_shares', sizes=(20, 500), alpha=0.7, color='purple')

plt.title('Total Score vs Engagement Rate (Độ Lớn Của Điểm = Lượt Share)', fontsize=16, fontweight='bold')
plt.xlabel('Tổng Điểm (Total Score)', fontsize=12)
plt.ylabel('Tỷ Lệ Tương Tác (Share / Heart)', fontsize=12)

# Gắn nhãn cho top 3 bài hát có Total Score cao nhất để minh họa trên scatter
top_3 = df.nlargest(3, 'total_score')
for idx, row in top_3.iterrows():
    plt.text(row['total_score'], row['engagement_rate'] + 0.01, row['title'][:15]+'...', fontsize=9)

plt.tight_layout()
plt.savefig(os.path.join(thu_muc_chart, '5_engagement_vs_score.png'), dpi=300)
plt.close()

print(f"--- ĐÃ VẼ XONG 5 BIỂU ĐỒ! Hãy kiểm tra trong thư mục '{thu_muc_chart}' ---")