import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# 1. ĐỌC DỮ LIỆU
# ==========================================
thu_muc_data = '../data'
file_giao_thoa = os.path.join(thu_muc_data, 'du_lieu_giao_thoa.json')

print("--- ĐANG ĐỌC DỮ LIỆU ---")
try:
    df = pd.read_json(file_giao_thoa)
    print(f"Thành công! Dữ liệu có {df.shape[0]} dòng (bài hát).")
except FileNotFoundError:
    print("Lỗi: Không tìm thấy file dữ liệu.")
    exit()

# Đảm bảo có cột engagement_rate nếu chưa có
if 'engagement_rate' not in df.columns:
    df['engagement_rate'] = df['nct_shares'] / df['nct_hearts'].replace(0, 1)

# Cài đặt style chung cho biểu đồ
sns.set_theme(style="whitegrid")

# =====================================================================
#  BIỂU ĐỒ TOP 10 BÀI HÁT PHỔ BIẾN NHẤT (1_top_10_songs.png)
# - Dựa vào đâu: Dùng hàm sort_values() sắp xếp cột 'total_score' giảm dần và lấy 10 bài đầu tiên (head(10)).
# - Ý nghĩa: Trực quan hóa danh sách các bài hát đang có Tổng điểm cao nhất trên thị trường hiện tại bằng biểu đồ cột ngang (Barplot).
# =====================================================================
plt.figure(figsize=(12, 6))
top_10_songs = df.sort_values(by='total_score', ascending=False).head(10)
sns.barplot(data=top_10_songs, x='total_score', y='title', palette='viridis')
plt.title('Top 10 Bài Hát Phổ Biến Nhất (Dựa trên Tổng Điểm)', fontsize=14, fontweight='bold')
plt.xlabel('Tổng Điểm (Total Score)')
plt.ylabel('Tên Bài Hát')
plt.tight_layout()
plt.savefig('1_top_10_songs.png')
plt.close()


# =====================================================================
#  BIỂU ĐỒ TOP CA SĨ THỐNG TRỊ (2_top_artists.png)
# - Dựa vào đâu: Dùng hàm groupby('artist') để gộp tất cả các bài hát của cùng 1 ca sĩ lại, sau đó tính tổng (sum) điểm của họ.
# - Ý nghĩa: Giúp đánh giá sức mạnh tổng thể của một nghệ sĩ. Một ca sĩ có thể không có bài Top 1, nhưng có nhiều bài Top 10 thì tổng điểm vẫn rất cao.
# =====================================================================
plt.figure(figsize=(12, 6))
top_artists = df.groupby('artist')['total_score'].sum().sort_values(ascending=False).head(10).reset_index()
sns.barplot(data=top_artists, x='total_score', y='artist', palette='magma')
plt.title('Top 10 Ca Sĩ Thống Trị Bảng Xếp Hạng (Tổng Điểm Các Bài Hát)', fontsize=14, fontweight='bold')
plt.xlabel('Tổng Điểm Cộng Dồn')
plt.ylabel('Ca Sĩ')
plt.tight_layout()
plt.savefig('2_top_artists.png')
plt.close()


# =====================================================================
# PHÁT HIỆN SIÊU HIT / NGOẠI LAI (3_super_hits_outliers.png)
# - Dựa vào đâu: Sử dụng biểu đồ Hộp (Boxplot) để áp dụng phương pháp thống kê IQR.
# - Ý nghĩa: Các chấm tròn nằm ngoài "râu" của biểu đồ chính là các Outliers (Dữ liệu ngoại lai). Trong âm nhạc, đây không phải là lỗi dữ liệu, mà chính là những "Siêu Hit" có lượt tim/nghe cao đột biến so với mặt bằng chung.
# =====================================================================
plt.figure(figsize=(10, 5))
sns.boxplot(data=df, x='nct_hearts', color='lightcoral')
plt.title('Phân Bố Lượt Thả Tim (NCT Hearts) & Phát Hiện Siêu Hit', fontsize=14, fontweight='bold')
plt.xlabel('Lượt Thả Tim')
plt.tight_layout()
plt.savefig('3_super_hits_outliers.png')
plt.close()


# =====================================================================
# MA TRẬN TƯƠNG QUAN (4_correlation_heatmap.png)
# - Dựa vào đâu: Dùng hàm .corr() để tính hệ số tương quan Pearson giữa các biến số (lượt nghe, tim, share, tổng điểm).
# - Ý nghĩa: Biểu đồ Heatmap (Bản đồ nhiệt) giúp nhìn nhanh mối quan hệ. Ô màu càng sáng (tiến về 1) chứng tỏ 2 chỉ số đó càng liên quan mật thiết với nhau (ví dụ: bài nhiều tim thì thường cũng nhiều share).
# =====================================================================
plt.figure(figsize=(8, 6))
numeric_cols = ['lastfm_listeners', 'nct_hearts', 'nct_shares', 'total_score', 'engagement_rate']
corr_matrix = df[numeric_cols].corr()
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5)
plt.title('Ma Trận Tương Quan Giữa Các Chỉ Số', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('4_correlation_heatmap.png')
plt.close()


# =====================================================================
# TỶ LỆ TƯƠNG TÁC VÀ TỔNG ĐIỂM (5_engagement_vs_score.png)
# - Dựa vào đâu: Vẽ biểu đồ phân tán (Scatter Plot) với trục X là tỷ lệ tương tác (Share/Heart) và trục Y là Tổng điểm.
# - Ý nghĩa: Giúp trả lời câu hỏi: "Bài hát nổi tiếng nhất (điểm cao nhất) có phải là bài có fan nhiệt tình nhất (tỷ lệ share cao nhất) không?". Những chấm nằm ở góc trên bên phải là những bài hoàn hảo về cả độ hot lẫn sự lan truyền.
# =====================================================================
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='engagement_rate', y='total_score', alpha=0.7, color='teal', s=100)
plt.title('Mối Quan Hệ Giữa Tỷ Lệ Tương Tác Và Tổng Điểm', fontsize=14, fontweight='bold')
plt.xlabel('Tỷ Lệ Tương Tác (Engagement Rate)')
plt.ylabel('Tổng Điểm (Total Score)')
plt.tight_layout()
plt.savefig('5_engagement_vs_score.png')
plt.close()

print("Đã xuất thành công 5 biểu đồ ra file hình ảnh (PNG)!")
