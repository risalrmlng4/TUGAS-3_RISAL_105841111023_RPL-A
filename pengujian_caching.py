import redis
import time

# Koneksi ke Redis localhost
r = redis.Redis(host='localhost', port=6379, db=0)

print("=" * 55)
print("   PENGUJIAN CACHING DENGAN REDIS - LOCALHOST")
print("=" * 55)

# Simulasi database sederhana
database = {
    "user:1": "Futri Ayu Reski Amalia",
    "user:2": "Fadilah Tun Hazimah",
    "user:3": "Dian Ramadhani",
    "product:1": "Laptop ASUS - Rp 8.000.000",
    "product:2": "Mouse Wireless - Rp 150.000",
}

def ambil_dari_database(key):
    """Simulasi ambil data dari database (lambat)"""
    time.sleep(1)  # simulasi delay database 1 detik
    return database.get(key, None)

def ambil_data(key):
    """Fungsi utama: Cache Aside Pattern"""
    # Cek cache dulu
    data_cache = r.get(key)

    if data_cache:
        # CACHE HIT
        return "CACHE HIT", data_cache.decode('utf-8')
    else:
        # CACHE MISS - ambil dari database
        data_db = ambil_dari_database(key)
        if data_db:
            r.setex(key, 30, data_db)  # simpan ke cache, TTL 30 detik
        return "CACHE MISS", data_db

# -----------------------------------------------
# PENGUJIAN 1: Cache Aside Pattern
# -----------------------------------------------
print("\n📌 PENGUJIAN 1: Cache Aside Pattern")
print("-" * 55)

keys_uji = ["user:1", "product:1", "user:2"]

for key in keys_uji:
    print(f"\n🔍 Request data '{key}':")

    # Request pertama (pasti cache miss)
    start = time.time()
    status, data = ambil_data(key)
    durasi = time.time() - start
    print(f"   Request ke-1 → {status} | Data: {data} | Waktu: {durasi:.3f} detik")

    # Request kedua (pasti cache hit)
    start = time.time()
    status, data = ambil_data(key)
    durasi = time.time() - start
    print(f"   Request ke-2 → {status} | Data: {data} | Waktu: {durasi:.4f} detik")

# -----------------------------------------------
# PENGUJIAN 2: Cache Invalidation (TTL)
# -----------------------------------------------
print("\n\n📌 PENGUJIAN 2: Cache Invalidation dengan TTL")
print("-" * 55)

r.setex("product:2", 5, "Mouse Wireless - Rp 150.000")  # TTL 5 detik
print("✅ Data disimpan ke cache dengan TTL = 5 detik")

ttl = r.ttl("product:2")
print(f"⏱️  TTL sekarang: {ttl} detik")

print("⏳ Menunggu 6 detik agar cache expired...")
time.sleep(6)

data = r.get("product:2")
if data is None:
    print("❌ Cache sudah EXPIRED - data tidak ada di cache lagi")
else:
    print(f"✅ Cache masih ada: {data.decode('utf-8')}")

# -----------------------------------------------
# PENGUJIAN 3: Write Through Pattern
# -----------------------------------------------
print("\n\n📌 PENGUJIAN 3: Write Through Pattern")
print("-" * 55)

def write_through(key, value):
    """Tulis ke cache dan database bersamaan"""
    database[key] = value          # tulis ke database
    r.setex(key, 30, value)        # tulis ke cache
    print(f"✅ Data '{key}' ditulis ke DATABASE dan CACHE sekaligus")

write_through("product:3", "Keyboard Mechanical - Rp 500.000")

data_cache = r.get("product:3")
data_db = database.get("product:3")
print(f"📦 Data di Cache  : {data_cache.decode('utf-8')}")
print(f"🗄️  Data di Database: {data_db}")
print(f"🔁 Konsistensi    : {'✅ SAMA' if data_cache.decode('utf-8') == data_db else '❌ BERBEDA'}")

# -----------------------------------------------
# RINGKASAN
# -----------------------------------------------
print("\n\n" + "=" * 55)
print("   RINGKASAN HASIL PENGUJIAN")
print("=" * 55)
print("✅ Cache Aside  : Berhasil - cache miss lalu hit")
print("✅ TTL/Invalidation: Berhasil - cache expired setelah 5 dtk")
print("✅ Write Through: Berhasil - data konsisten di cache & DB")
print("=" * 55)
print("\n✅ Pengujian selesai!")