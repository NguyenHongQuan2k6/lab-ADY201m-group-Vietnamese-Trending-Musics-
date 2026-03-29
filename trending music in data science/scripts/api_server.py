"""
api_server.py — Flask API cho Vietnam Trending Music Dashboard
=============================================================
Cách chạy:
  1. pip install flask flask-cors pymongo
  2. Đặt dashboard.html cùng thư mục với file này
  3. python api_server.py
  4. Mở trình duyệt → http://localhost:5000
"""

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
import statistics
import math
import os

# ─────────────────────────────────────────
# KHỞI TẠO APP  (phải đứng trước @app.route)
# ─────────────────────────────────────────
app = Flask(__name__)
CORS(app)

# ─────────────────────────────────────────
# KẾT NỐI MONGODB
# ─────────────────────────────────────────
try:
    client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=3000)
    client.server_info()
    db  = client['trending_music_in_Vietnam_db']
    col = db['bang_xep_hang_giao_thoa']
    print("Kết nối MongoDB thành công!")
except Exception as e:
    print(f"Lỗi kết nối MongoDB: {e}")
    print("   Hãy đảm bảo MongoDB đang chạy trên localhost:27017")
    exit(1)


# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────
def calc_skewness(vals):
    n = len(vals)
    if n < 3:
        return 0
    m = sum(vals) / n
    s = statistics.stdev(vals)
    if s == 0:
        return 0
    return round((n / ((n - 1) * (n - 2))) * sum(((v - m) / s) ** 3 for v in vals), 2)


def pearson(xs, ys):
    n = len(xs)
    if n == 0:
        return 0
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    dx  = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy  = math.sqrt(sum((y - my) ** 2 for y in ys))
    return round(num / (dx * dy), 3) if dx * dy != 0 else 0


# ─────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────

@app.route('/')
def serve_dashboard():
    """Serve dashboard.html tại http://localhost:5000"""
    folder = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(folder, 'dashboard.html')


@app.route('/health')
def health():
    count = col.count_documents({})
    return jsonify({'status': 'ok', 'documents': count})


@app.route('/api/data')
def get_data():
    docs = list(col.find({}, {'_id': 0}))
    return jsonify(docs)


@app.route('/api/stats')
def get_stats():
    docs = list(col.find({}, {'_id': 0}))

    if not docs:
        return jsonify({'error': 'Không có dữ liệu trong MongoDB'}), 404

    listeners_vals = [d.get('lastfm_listeners', 0) for d in docs]
    hearts_vals    = [d.get('nct_hearts', 0)        for d in docs]
    shares_vals    = [d.get('nct_shares', 0)         for d in docs]
    eng_vals       = [d.get('engagement_rate', 0)    for d in docs]
    score_vals     = [d.get('total_score', 0)         for d in docs]
    n = len(docs)

    unique_artists = len(set(d.get('artist', '').split(',')[0].strip() for d in docs))
    stats = {
        'total_songs'    : n,
        'unique_artists' : unique_artists,
        'total_hearts'   : sum(hearts_vals),
        'total_shares'   : sum(shares_vals),
        'total_listeners': sum(listeners_vals),
        'avg_hearts'     : int(sum(hearts_vals) / n),
        'avg_listeners'  : int(sum(listeners_vals) / n),
        'avg_engagement' : round(sum(eng_vals) / n * 100, 1),
    }

    artist_listeners, artist_hearts = {}, {}
    for d in docs:
        first = d.get('artist', 'N/A').split(',')[0].strip()
        artist_listeners[first] = artist_listeners.get(first, 0) + d.get('lastfm_listeners', 0)
        artist_hearts[first]    = artist_hearts.get(first, 0)    + d.get('nct_hearts', 0)

    top5_listeners = sorted(artist_listeners.items(), key=lambda x: x[1], reverse=True)[:5]
    top5_hearts    = sorted(artist_hearts.items(),    key=lambda x: x[1], reverse=True)[:5]

    bins_labels = ['0-500K', '500K-1M', '1M-2M', '2M-4M', '4M-7M', '7M-12M', '12M+']
    bins_count  = [0] * 7
    for sc in score_vals:
        if   sc < 500000:    bins_count[0] += 1
        elif sc < 1000000:   bins_count[1] += 1
        elif sc < 2000000:   bins_count[2] += 1
        elif sc < 4000000:   bins_count[3] += 1
        elif sc < 7000000:   bins_count[4] += 1
        elif sc < 12000000:  bins_count[5] += 1
        else:                bins_count[6] += 1

    skewness = {
        'listeners' : calc_skewness(listeners_vals),
        'hearts'    : calc_skewness(hearts_vals),
        'shares'    : calc_skewness(shares_vals),
        'engagement': calc_skewness(eng_vals),
    }

    corr = {
        'lh': pearson(listeners_vals, hearts_vals),
        'ls': pearson(listeners_vals, shares_vals),
        'le': pearson(listeners_vals, eng_vals),
        'hs': pearson(hearts_vals,    shares_vals),
        'he': pearson(hearts_vals,    eng_vals),
        'se': pearson(shares_vals,    eng_vals),
    }

    sorted_hearts = sorted(hearts_vals)
    Q1    = sorted_hearts[int(n * 0.25)]
    Q3    = sorted_hearts[int(n * 0.75)]
    IQR   = Q3 - Q1
    upper = Q3 + 1.5 * IQR

    outliers   = sorted([d for d in docs if d.get('nct_hearts', 0) > upper],
                        key=lambda x: x.get('nct_hearts', 0), reverse=True)
    top_growth = sorted(docs, key=lambda x: x.get('score_growth', 0), reverse=True)[:6]

    return jsonify({
        'stats'         : stats,
        'top5_listeners': top5_listeners,
        'top5_hearts'   : top5_hearts,
        'bins_labels'   : bins_labels,
        'bins_count'    : bins_count,
        'skewness'      : skewness,
        'corr'          : corr,
        'outliers'      : outliers,
        'top_growth'    : top_growth,
        'iqr'           : {'Q1': Q1, 'Q3': Q3, 'IQR': IQR, 'upper': upper},
    })


# ─────────────────────────────────────────
# CHẠY SERVER
# ─────────────────────────────────────────
if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("  Vietnam Music Dashboard API")
    print("=" * 50)
    print("  Dashboard : http://localhost:5000")
    print("  API data  : http://localhost:5000/api/data")
    print("  API stats : http://localhost:5000/api/stats")
    print("  Health    : http://localhost:5000/health")
    print("=" * 50)
    print("  Nhan Ctrl+C de dung\n")
    app.run(debug=False, port=5000)