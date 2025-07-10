# Farcaster Bot

Bot ini adalah alat serbaguna untuk berinteraksi dengan Farcaster API, mengkonsolidasikan berbagai fungsionalitas ke dalam satu skrip Python yang mudah digunakan.

## Fitur

Bot ini menawarkan beberapa mode operasi utama, masing-masing dengan opsi yang lebih spesifik:

1.  **Post Casts**
    *   **Post Casts untuk semua akun (dari `post.txt`)**: Memposting konten dari `post.txt` secara berurutan untuk setiap akun yang terdaftar di `user_info.json`. Anda akan diminta untuk memasukkan rentang delay acak (min-max) antara setiap postingan.
    *   **Post Casts per akun (masukkan teks manual)**: Memungkinkan Anda memasukkan teks postingan secara manual untuk setiap akun yang terdaftar di `user_info.json`. Anda akan diminta untuk memasukkan rentang delay acak (min-max) antara setiap postingan.

2.  **Auto Like dan Recast**
    *   **Auto Like dan Recast untuk semua akun**: Setiap akun di `user_info.json` akan secara otomatis menyukai dan me-recast postingan terakhir dari semua akun lain yang terdaftar di `user_info.json`. Anda akan diminta untuk memasukkan rentang delay acak (min-max) antara setiap like/recast, dan juga rentang delay acak (min-max) antara setiap pengguna.
    *   **Auto Like dan Recast untuk akun terpilih**: Memungkinkan Anda memilih satu akun dari `user_info.json` untuk melakukan like dan recast postingan terakhir dari semua akun lain yang terdaftar di `user_info.json`. Anda akan diminta untuk memasukkan rentang delay acak (min-max) antara setiap like/recast.

3.  **Follow/Unfollow User**
    *   **Follow/Unfollow satu akun (pilih akun Anda)**: Memungkinkan Anda memilih satu akun dari `user_info.json` untuk melakukan follow atau unfollow terhadap FID target tertentu. Anda akan diminta untuk memasukkan rentang delay acak (min-max) antara aksi follow/unfollow.
    *   **Follow/Unfollow satu target untuk semua akun Anda**: Membuat semua akun di `user_info.json` melakukan follow atau unfollow terhadap satu FID target yang ditentukan. Anda akan diminta untuk memasukkan rentang delay acak (min-max) antara setiap aksi follow/unfollow.

4.  **Follow All Users**
    *   Setiap akun di `user_info.json` akan secara otomatis mengikuti semua akun lain yang terdaftar di `user_info.json`. Anda akan diminta untuk memasukkan rentang delay acak (min-max) antara setiap aksi follow.

5.  **Ambil Info User (dari `bearer.txt`)**
    *   Mengambil token bearer dari `bearer.txt`.
    *   Menggunakan token tersebut untuk mendapatkan informasi detail pengguna (seperti email, nama tampilan, username, FID, dan label spam) dari Farcaster API.
    *   Menyimpan informasi yang diambil ke `user_info.json` dan `user_info.csv`.

### Peningkatan Utama

*   **Pemeriksaan Aksi Cerdas**: Sebelum melakukan aksi `follow`, `like`, atau `recast`, bot akan memeriksa apakah aksi tersebut sudah dilakukan (misalnya, apakah pengguna sudah diikuti, atau postingan sudah disukai/di-recast). Ini mengurangi permintaan yang tidak perlu ke API.
*   **Variasi Header HTTP**: Setiap instance bot sekarang menggunakan `User-Agent` dan `Accept-Language` yang dipilih secara acak dari daftar realistis. Ini membantu bot terlihat lebih seperti pengguna manusia dan mengurangi kemungkinan deteksi bot.

## Penggunaan

Untuk menjalankan bot, navigasikan ke direktori proyek di terminal Anda dan jalankan:

```bash
python main.py
```

Bot akan menampilkan menu opsi utama. Masukkan nomor yang sesuai dengan fitur yang ingin Anda gunakan. Jika fitur tersebut memiliki sub-opsi, Anda akan diminta untuk memilih lagi. Ikuti petunjuk di layar untuk memasukkan detail yang diperlukan, termasuk rentang delay acak (min-max) jika diminta.

## Penggunaan di Termux

Jika Anda menggunakan Termux di perangkat Android Anda, ikuti langkah-langkah berikut untuk menyiapkan dan menjalankan bot:

1.  **Instal Termux**: Unduh dan instal aplikasi Termux dari F-Droid atau Google Play Store.

2.  **Perbarui Paket Termux**: Setelah Termux terinstal, buka aplikasi dan perbarui paketnya:
    ```bash
    pkg update && pkg upgrade
    ```

3.  **Instal Python**: Instal Python di Termux:
    ```bash
    pkg install python
    ```

4.  **Instal Git (Opsional, jika Anda ingin mengkloning repo)**:
    ```bash
    pkg install git
    ```

5.  **Navigasi ke Direktori Proyek**: Pindahkan file bot Anda ke Termux atau kloning repositori jika Anda menggunakan Git. Misalnya, jika Anda menaruh file di folder `storage/shared/warpcast`:
    ```bash
    termux-setup-storage
    cd /sdcard/warpcast
    ```
    Atau jika Anda mengkloning repositori:
    ```bash
    git clone https://github.com/your-repo/warpcast.git # Ganti dengan URL repo Anda
    cd warpcast
    ```

6.  **Instal Dependensi Python**: Instal dependensi yang diperlukan menggunakan pip:
    ```bash
    pip install -r requirements.txt
    ```

7.  **Jalankan Bot**: Sekarang Anda dapat menjalankan bot:
    ```bash
    python main.py
    ```

Bot akan menampilkan menu opsi. Masukkan nomor yang sesuai dengan fitur yang ingin Anda gunakan dan ikuti petunjuk di layar.

## Pembersihan Proyek (Opsional)

Selama pengembangan, beberapa file lama mungkin tersisa. Anda dapat menghapus file-file berikut dengan aman untuk merapikan proyek Anda:

*   `.env`
*   `auto_like_bot.py`
*   `bearercore.py`
*   `cekneynar.py`
*   `convert_phrases.py`
*   `farcaster_bot.py`
*   `follow_all_users.py`
*   `getmail.py`
*   `getonboarding.py`
*   `link.txt`
*   `log.txt`
*   `mail.txt`
*   `main.py`
*   `package-lock.json`
*   `package.json`
*   `pharse.txt`
*   `pk.txt`
*   `post_ai_casts.py`
*   `session_manager.py`
*   `sessions.db`
*   `struktur.txt`
*   `user_info.csv3`
*   `warpcast_backup_20250710.zip`
*   `__pycache__/`
*   `node_modules/`

**Penting:** Pastikan Anda tidak menghapus `main.py`, `user_info.json`, `post.txt` (jika digunakan), `bearer.txt` (jika digunakan), atau `user_info.csv`.
