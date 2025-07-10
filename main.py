import requests
import uuid
import re
import json
import time
import random
import csv

# --- Daftar User-Agent yang realistis ---
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
]

# --- Daftar Accept-Language yang realistis ---
ACCEPT_LANGUAGES = [
    "en-US,en;q=0.9",
    "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    "fr-FR,fr;q=0.9,en;q=0.8",
    "es-ES,es;q=0.9,en;q=0.8",
]

class FarcasterBot:
    def __init__(self, bearer_token):
        self.bearer_token = bearer_token
        self.base_url = "https://client.farcaster.xyz"

        # --- Variasikan header saat inisialisasi bot ---
        self.headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "*/*",
            "User-Agent": random.choice(USER_AGENTS), # Pilih User-Agent acak
            "Accept-Language": random.choice(ACCEPT_LANGUAGES), # Pilih Accept-Language acak
            "Accept-Encoding": "gzip, deflate, br, zstd", # Bisa divariasikan juga
            "Origin": "https://farcaster.xyz",
            "Referer": "https://farcaster.xyz/",
            "Connection": "keep-alive",
        }

    def _make_request(self, method, url, json_data=None, params=None):
        headers = self.headers.copy() # Salin header untuk setiap permintaan
        headers["Idempotency-Key"] = str(uuid.uuid4()) # Idempotency-Key harus unik per permintaan

        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=json_data, timeout=10)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=json_data, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, json=json_data, timeout=10)
            else:
                raise ValueError(f"Metode HTTP tidak didukung: {method}")

            response.raise_for_status() # Angkat HTTPError untuk respons buruk (4xx atau 5xx)
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error saat membuat permintaan ke {url}: {e}")
            return None

    def follow_user(self, fid):
        url = f"{self.base_url}/v2/follows"
        payload = {"targetFid": fid}
        response = self._make_request("PUT", url, json_data=payload)
        return response and response.status_code == 200

    def unfollow_user(self, fid):
        url = f"{self.base_url}/v2/follows"
        payload = {"targetFid": fid}
        response = self._make_request("DELETE", url, json_data=payload)
        return response and response.status_code == 200

    def post_cast(self, text, embeds=None):
        url = f"{self.base_url}/v2/casts"
        payload = {"text": text, "embeds": embeds or []}
        response = self._make_request("POST", url, json_data=payload)
        return response and response.status_code in [200, 201]

    def recast_cast(self, cast_hash):
        url = f"{self.base_url}/v2/recasts"
        payload = {"castHash": cast_hash}
        response = self._make_request("PUT", url, json_data=payload)
        return response and response.status_code == 200

    def unrecast_cast(self, cast_hash):
        url = f"{self.base_url}/v2/recasts"
        payload = {"castHash": cast_hash}
        response = self._make_request("DELETE", url, json_data=payload)
        return response and response.status_code == 200

    def like_cast_by_url(self, url):
        try:
            username, prefix = self._extract_username_and_prefix(url)
            full_hash = self._get_full_cast_hash(username, prefix)
            return self._like_cast(full_hash)
        except Exception:
            return False

    def unlike_cast_by_url(self, url):
        try:
            username, prefix = self._extract_username_and_prefix(url)
            full_hash = self._get_full_cast_hash(username, prefix)
            return self._unlike_cast(full_hash)
        except Exception:
            return False

    def _like_cast(self, cast_hash):
        url = f"{self.base_url}/v2/cast-likes"
        payload = {"castHash": cast_hash}
        response = self._make_request("PUT", url, json_data=payload)
        return response and response.status_code == 200

    def _unlike_cast(self, cast_hash):
        url = f"{self.base_url}/v2/cast-likes"
        payload = {"castHash": cast_hash}
        response = self._make_request("DELETE", url, json_data=payload)
        return response and response.status_code == 200

    def _extract_username_and_prefix(self, url):
        match = re.search(r"farcaster\.xyz/([^/]+)/(0x[0-9a-fA-F]+)", url)
        if not match:
            raise ValueError("URL tidak valid.")
        return match.group(1), match.group(2)

    def _get_full_cast_hash(self, username, cast_hash_prefix):
        url = f"{self.base_url}/v2/user-thread-casts"
        params = {
            "username": username,
            "castHashPrefix": cast_hash_prefix,
            "limit": 15
        }
        response = self._make_request("GET", url, params=params)
        if response and response.status_code == 200:
            data = response.json()
            casts = data.get("result", {}).get("casts", [])
            if not casts:
                raise Exception("Tidak ada cast ditemukan.")
            return casts[0]["hash"]
        raise Exception("Gagal mengambil hash lengkap.")

    def get_latest_cast_hash(self, fid):
        url = f"{self.base_url}/v2/profile-casts"
        params = {
            "fid": fid,
            "limit": 1
        }
        response = self._make_request("GET", url, params=params)
        if response and response.status_code == 200:
            data = response.json()
            casts = data.get("result", {}).get("casts", [])
            if casts:
                return casts[0]["hash"]
        return None

    def is_following(self, target_fid):
        url = f"{self.base_url}/v2/user?fid={target_fid}"
        response = self._make_request("GET", url)
        if response and response.ok:
            data = response.json()
            return data.get("result", {}).get("user", {}).get("viewerContext", {}).get("following", False)
        return False

    def is_liked(self, cast_hash):
        url = f"{self.base_url}/v2/casts?hash={cast_hash}"
        response = self._make_request("GET", url)
        if response and response.ok:
            data = response.json()
            return data.get("result", {}).get("cast", {}).get("viewerContext", {}).get("reacted", False)
        return False

    def is_recasted(self, cast_hash):
        url = f"{self.base_url}/v2/casts?hash={cast_hash}"
        response = self._make_request("GET", url)
        if response and response.ok:
            data = response.json()
            return data.get("result", {}).get("cast", {}).get("viewerContext", {}).get("recast", False)
        return False

def post_casts_from_users(user_info_path="user_info.json", posts_file_path="post.txt", max_retries=3, retry_delay=10):
    try:
        with open(user_info_path, 'r') as f:
            users = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{user_info_path}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{user_info_path}'.")
        return

    if not users:
        print("No users found in user_info.json.")
        return

    print(f"Found {len(users)} users. Starting cast posting process...")

    try:
        with open(posts_file_path, 'r', encoding='utf-8') as f:
            posts = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: Post file '{posts_file_path}' not found. Please create it with one post per line.")
        return
    except Exception as e:
        print(f"Error reading posts from '{posts_file_path}': {e}")
        return

    if not posts:
        print(f"No posts found in '{posts_file_path}'.")
        return

    print(f"Found {len(posts)} posts in '{posts_file_path}'.")

    while True:
        try:
            min_delay_action = float(input("Masukkan delay minimum (detik) antara postingan (misal: 5): "))
            max_delay_action = float(input("Masukkan delay maksimum (detik) antara postingan (misal: 15): "))
            if min_delay_action < 0 or max_delay_action < min_delay_action:
                raise ValueError("Delay tidak valid.")
            break
        except ValueError as e:
            print(f"Input tidak valid: {e}. Mohon masukkan angka yang benar.")

    for i, user in enumerate(users):
        user_fid = user.get("fid")
        user_bearer = user.get("bearer")
        user_username = user.get("username", "Unknown")

        if not user_fid or not user_bearer:
            print(f"Skipping user {user_username}: Missing FID or bearer token.")
            continue

        if i >= len(posts):
            print(f"No more posts available for user {user_username}. Skipping.")
            continue

        cast_text = posts[i]
        print(f"User '{user_username}' (FID: {user_fid}) is preparing to post a cast.")
        bot = FarcasterBot(user_bearer)

        retries = 0
        success = False
        while retries < max_retries and not success:
            print(f"  Attempt {retries + 1}/{max_retries} to post: \"{cast_text}\"")
            try:
                success = bot.post_cast(cast_text)
                if success:
                    print(f"  Successfully posted cast for '{user_username}'.")
                else:
                    print(f"  Failed to post cast for '{user_username}'. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
            except Exception as e:
                print(f"  An error occurred while '{user_username}' tried to post a cast: {e}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            retries += 1
        
        if not success:
            print(f"  Failed to post cast for '{user_username}' after {max_retries} attempts.")
        
        time.sleep(random.uniform(min_delay_action, max_delay_action)) # Random delay between posts

def post_single_cast_per_user(user_info_path="user_info.json", max_retries=3, retry_delay=10):
    try:
        with open(user_info_path, 'r') as f:
            users = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{user_info_path}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{user_info_path}'.")
        return

    if not users:
        print("No users found in user_info.json.")
        return

    print(f"Found {len(users)} users. Starting single cast posting process...")

    while True:
        try:
            min_delay_action = float(input("Masukkan delay minimum (detik) antara postingan (misal: 5): "))
            max_delay_action = float(input("Masukkan delay maksimum (detik) antara postingan (misal: 15): "))
            if min_delay_action < 0 or max_delay_action < min_delay_action:
                raise ValueError("Delay tidak valid.")
            break
        except ValueError as e:
            print(f"Input tidak valid: {e}. Mohon masukkan angka yang benar.")

    for user in users:
        user_fid = user.get("fid")
        user_bearer = user.get("bearer")
        user_username = user.get("username", "Unknown")

        if not user_fid or not user_bearer:
            print(f"Skipping user {user_username}: Missing FID or bearer token.")
            continue

        cast_text = input(f"Masukkan teks postingan untuk '{user_username}' (FID: {user_fid}): ")
        if not cast_text.strip():
            print(f"Teks postingan kosong untuk '{user_username}'. Melewatkan.")
            continue

        print(f"User '{user_username}' (FID: {user_fid}) is preparing to post: \"{cast_text}\"")
        bot = FarcasterBot(user_bearer)

        retries = 0
        success = False
        while retries < max_retries and not success:
            print(f"  Attempt {retries + 1}/{max_retries} to post...")
            try:
                success = bot.post_cast(cast_text)
                if success:
                    print(f"  Successfully posted cast for '{user_username}'.")
                else:
                    print(f"  Failed to post cast for '{user_username}'. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
            except Exception as e:
                print(f"  An error occurred while '{user_username}' tried to post a cast: {e}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            retries += 1
        
        if not success:
            print(f"  Failed to post cast for '{user_username}' after {max_retries} attempts.")
        
        time.sleep(random.uniform(min_delay_action, max_delay_action)) # Random delay between posts

def auto_like_and_recast_posts(user_info_path="user_info.json"):
    try:
        with open(user_info_path, 'r') as f:
            users = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{user_info_path}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{user_info_path}'.")
        return

    if not users:
        print("No users found in user_info.json.")
        return

    print(f"Found {len(users)} users. Starting auto-like and recast process...")

    while True:
        try:
            min_delay_likes_recasts = float(input("Masukkan delay minimum (detik) antara like/recast (misal: 1): "))
            max_delay_likes_recasts = float(input("Masukkan delay maksimum (detik) antara like/recast (misal: 5): "))
            if min_delay_likes_recasts < 0 or max_delay_likes_recasts < min_delay_likes_recasts:
                raise ValueError("Delay tidak valid.")
            break
        except ValueError as e:
            print(f"Input tidak valid: {e}. Mohon masukkan angka yang benar.")

    while True:
        try:
            min_delay_between_users = float(input("Masukkan delay minimum (detik) antara pengguna (misal: 15): "))
            max_delay_between_users = float(input("Masukkan delay maksimum (detik) antara pengguna (misal: 25): "))
            if min_delay_between_users < 0 or max_delay_between_users < min_delay_between_users:
                raise ValueError("Delay tidak valid.")
            break
        except ValueError as e:
            print(f"Input tidak valid: {e}. Mohon masukkan angka yang benar.")

    # Optimization: Fetch all latest cast hashes once
    all_latest_casts = {}
    for user in users:
        target_fid = user.get("fid")
        target_username = user.get("username", "Unknown")
        if target_fid:
            # Use a temporary bot instance to fetch public cast info
            # This assumes any bearer token can fetch public cast info
            temp_bot = FarcasterBot(user.get("bearer")) 
            latest_cast_hash = temp_bot.get_latest_cast_hash(target_fid)
            if latest_cast_hash:
                all_latest_casts[target_fid] = latest_cast_hash
                print(f"Fetched latest cast for {target_username} (FID: {target_fid}): {latest_cast_hash[:8]}...")
            else:
                print(f"No recent posts found for {target_username} (FID: {target_fid}).")

    for liker_user in users:
        liker_fid = liker_user.get("fid")
        liker_bearer = liker_user.get("bearer")
        liker_username = liker_user.get("username", "Unknown")

        if not liker_fid or not liker_bearer:
            print(f"Skipping liker user {liker_username}: Missing FID or bearer token.")
            continue

        print(f"\nUser '{liker_username}' (FID: {liker_fid}) is starting to like and recast posts.")
        liker_bot = FarcasterBot(liker_bearer)

        for target_user in users:
            if liker_fid == target_user.get("fid"):
                continue # Skip liking/recasting own posts

            target_fid = target_user.get("fid")
            target_username = target_user.get("username", "Unknown")

            if not target_fid:
                continue

            latest_cast_hash = all_latest_casts.get(target_fid)

            if latest_cast_hash:
                print(f"  {liker_username} is trying to like and recast {target_username}'s latest post...")
                
                # Cek apakah sudah disukai
                if liker_bot.is_liked(latest_cast_hash):
                    print(f"    Postingan {target_username} (Hash: {latest_cast_hash[:8]}...) sudah disukai oleh {liker_username}. Melewatkan like.")
                else:
                    try:
                        success_like = liker_bot._like_cast(latest_cast_hash)
                        if success_like:
                            print(f"    Successfully liked {target_username}'s post (Hash: {latest_cast_hash[:8]}...).")
                        else:
                            print(f"    Failed to like {target_username}'s post.")
                    except Exception as e:
                        print(f"    An error occurred while {liker_username} tried to like {target_username}'s post: {e}")

                # Cek apakah sudah di-recast
                if liker_bot.is_recasted(latest_cast_hash):
                    print(f"    Postingan {target_username} (Hash: {latest_cast_hash[:8]}...) sudah di-recast oleh {liker_username}. Melewatkan recast.")
                else:
                    try:
                        success_recast = liker_bot.recast_cast(latest_cast_hash)
                        if success_recast:
                            print(f"    Successfully recast {target_username}'s post (Hash: {latest_cast_hash[:8]}...).")
                        else:
                            print(f"    Failed to recast {target_username}'s post.")
                    except Exception as e:
                        print(f"    An error occurred while {liker_username} tried to recast {target_username}'s post: {e}")
            else:
                print(f"    No latest post found for {target_username} to like/recast.")
            
            time.sleep(random.uniform(min_delay_likes_recasts, max_delay_likes_recasts)) # Random delay between likes/recasts
        
        print(f"User '{liker_username}' finished liking and recasting posts. Waiting before next user...")
        time.sleep(random.uniform(min_delay_between_users, max_delay_between_users)) # Random delay between users

    print("Auto-like and recast process completed.")

def auto_like_recast_for_single_user(user_info_path="user_info.json"):
    try:
        with open(user_info_path, 'r') as f:
            users = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{user_info_path}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{user_info_path}'.")
        return

    if not users:
        print("No users found in user_info.json.")
        return

    print("\nPilih akun Anda untuk melakukan like/recast:")
    for i, user in enumerate(users):
        print(f"{i+1}. {user.get("username", "Unknown")} (FID: {user.get("fid")})")
    
    user_choice = input("Masukkan nomor akun: ")
    try:
        selected_user_index = int(user_choice) - 1
        if not (0 <= selected_user_index < len(users)):
            print("Pilihan akun tidak valid.")
            return
        selected_user = users[selected_user_index]
    except ValueError:
        print("Input tidak valid. Masukkan nomor.")
        return

    liker_fid = selected_user.get("fid")
    liker_bearer = selected_user.get("bearer")
    liker_username = selected_user.get("username", "Unknown")

    if not liker_fid or not liker_bearer:
        print(f"Skipping selected user {liker_username}: Missing FID or bearer token.")
        return

    print(f"\nUser '{liker_username}' (FID: {liker_fid}) is starting to like and recast posts.")
    liker_bot = FarcasterBot(liker_bearer)

    while True:
        try:
            min_delay_likes_recasts = float(input("Masukkan delay minimum (detik) antara like/recast (misal: 1): "))
            max_delay_likes_recasts = float(input("Masukkan delay maksimum (detik) antara like/recast (misal: 5): "))
            if min_delay_likes_recasts < 0 or max_delay_likes_recasts < min_delay_likes_recasts:
                raise ValueError("Delay tidak valid.")
            break
        except ValueError as e:
            print(f"Input tidak valid: {e}. Mohon masukkan angka yang benar.")

    # Optimization: Fetch all latest cast hashes once
    all_latest_casts = {}
    for user in users:
        target_fid = user.get("fid")
        target_username = user.get("username", "Unknown")
        if target_fid:
            temp_bot = FarcasterBot(user.get("bearer")) 
            latest_cast_hash = temp_bot.get_latest_cast_hash(target_fid)
            if latest_cast_hash:
                all_latest_casts[target_fid] = latest_cast_hash
                print(f"Fetched latest cast for {target_username} (FID: {target_fid}): {latest_cast_hash[:8]}...")
            else:
                print(f"No recent posts found for {target_username} (FID: {target_fid}).")

    for target_user in users:
        if liker_fid == target_user.get("fid"):
            continue # Skip liking/recasting own posts

        target_fid = target_user.get("fid")
        target_username = target_user.get("username", "Unknown")

        if not target_fid:
            continue

        latest_cast_hash = all_latest_casts.get(target_fid)

        if latest_cast_hash:
            print(f"  {liker_username} is trying to like and recast {target_username}'s latest post...")
            
            # Cek apakah sudah disukai
            if liker_bot.is_liked(latest_cast_hash):
                print(f"    Postingan {target_username} (Hash: {latest_cast_hash[:8]}...) sudah disukai oleh {liker_username}. Melewatkan like.")
            else:
                try:
                    success_like = liker_bot._like_cast(latest_cast_hash)
                    if success_like:
                        print(f"    Successfully liked {target_username}'s post (Hash: {latest_cast_hash[:8]}...).")
                    else:
                        print(f"    Failed to like {target_username}'s post.")
                except Exception as e:
                    print(f"    An error occurred while {liker_username} tried to like {target_username}'s post: {e}")

            # Cek apakah sudah di-recast
            if liker_bot.is_recasted(latest_cast_hash):
                print(f"    Postingan {target_username} (Hash: {latest_cast_hash[:8]}...) sudah di-recast oleh {liker_username}. Melewatkan recast.")
            else:
                try:
                    success_recast = liker_bot.recast_cast(latest_cast_hash)
                    if success_recast:
                        print(f"    Successfully recast {target_username}'s post (Hash: {latest_cast_hash[:8]}...).")
                    else:
                        print(f"    Failed to recast {target_username}'s post.")
                except Exception as e:
                    print(f"    An error occurred while {liker_username} tried to recast {target_username}'s post: {e}")
        else:
            print(f"    No latest post found for {target_username} to like/recast.")
        
        time.sleep(random.uniform(min_delay_likes_recasts, max_delay_likes_recasts)) # Random delay between likes/recasts
    
    print("Auto-like and recast process completed for selected user.")

def follow_all_users(user_info_path="user_info.json"):
    try:
        with open(user_info_path, 'r') as f:
            users = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{user_info_path}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{user_info_path}'.")
        return

    if not users:
        print("No users found in user_info.json.")
        return

    print(f"Found {len(users)} users. Starting follow process...")

    while True:
        try:
            min_delay_follow = float(input("Masukkan delay minimum (detik) antara follow (misal: 1): "))
            max_delay_follow = float(input("Masukkan delay maksimum (detik) antara follow (misal: 5): "))
            if min_delay_follow < 0 or max_delay_follow < min_delay_follow:
                raise ValueError("Delay tidak valid.")
            break
        except ValueError as e:
            print(f"Input tidak valid: {e}. Mohon masukkan angka yang benar.")

    for follower_user in users:
        follower_fid = follower_user.get("fid")
        follower_bearer = follower_user.get("bearer")
        follower_username = follower_user.get("username", "Unknown")

        if not follower_fid or not follower_bearer:
            print(f"Skipping user {follower_username}: Missing FID or bearer token.")
            continue

        print(f"User '{follower_username}' (FID: {follower_fid}) will now follow others.")
        bot = FarcasterBot(follower_bearer)

        for target_user in users:
            target_fid = target_user.get("fid")
            target_username = target_user.get("username", "Unknown")

            if not target_fid:
                print(f"Skipping target user {target_username}: Missing FID.")
                continue

            if follower_fid == target_fid:
                continue

            # Cek apakah sudah di-follow
            if bot.is_following(target_fid):
                print(f"  '{follower_username}' (FID: {follower_fid}) sudah mengikuti '{target_username}' (FID: {target_fid}). Melewatkan.")
                continue

            print(f"  '{follower_username}' (FID: {follower_fid}) attempting to follow '{target_username}' (FID: {target_fid})...")
            try:
                success = bot.follow_user(target_fid)
                if success:
                    print(f"  Successfully followed '{target_username}'.")
                else:
                    print(f"  Failed to follow '{target_username}'.")
            except Exception as e:
                print(f"  An error occurred while '{follower_user}' tried to follow '{target_user}': {e}")
            
            time.sleep(random.uniform(min_delay_follow, max_delay_follow)) # Random delay between follows

    print("Follow process completed.")

def follow_unfollow_single_target_for_all_users(user_info_path="user_info.json"):
    try:
        with open(user_info_path, 'r') as f:
            users = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{user_info_path}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{user_info_path}'.")
        return

    if not users:
        print("No users found in user_info.json.")
        return

    target_fid_str = input("Masukkan FID target (yang ingin di-follow/unfollow oleh semua akun): ")
    try:
        target_fid = int(target_fid_str)
    except ValueError:
        print("FID tidak valid. Harus berupa angka.")
        return

    action_choice = input("Pilih aksi (follow/unfollow): ").lower()
    if action_choice not in ['follow', 'unfollow']:
        print("Aksi tidak valid. Pilih 'follow' atau 'unfollow'.")
        return

    print(f"Semua akun akan mencoba {action_choice} FID {target_fid}...")

    while True:
        try:
            min_delay_action = float(input("Masukkan delay minimum (detik) antara aksi (misal: 1): "))
            max_delay_action = float(input("Masukkan delay maksimum (detik) antara aksi (misal: 5): "))
            if min_delay_action < 0 or max_delay_action < min_delay_action:
                raise ValueError("Delay tidak valid.")
            break
        except ValueError as e:
            print(f"Input tidak valid: {e}. Mohon masukkan angka yang benar.")

    for user in users:
        user_fid = user.get("fid")
        user_bearer = user.get("bearer")
        user_username = user.get("username", "Unknown")

        if not user_fid or not user_bearer:
            print(f"Skipping user {user_username}: Missing FID or bearer token.")
            continue

        print(f"\nUser '{user_username}' (FID: {user_fid}) sedang memproses...")
        bot = FarcasterBot(user_bearer)

        if action_choice == 'follow':
            if bot.is_following(target_fid):
                print(f"  '{user_username}' sudah mengikuti FID {target_fid}. Melewatkan.")
            else:
                if bot.follow_user(target_fid):
                    print(f"  Berhasil follow FID {target_fid}.")
                else:
                    print(f"  Gagal follow FID {target_fid}.")
        elif action_choice == 'unfollow':
            if not bot.is_following(target_fid):
                print(f"  '{user_username}' tidak mengikuti FID {target_fid}. Melewatkan unfollow.")
            else:
                if bot.unfollow_user(target_fid):
                    print(f"  Berhasil unfollow FID {target_fid}.")
                else:
                    print(f"  Gagal unfollow FID {target_fid}.")
        
        time.sleep(random.uniform(min_delay_action, max_delay_action)) # Random delay between actions

    print("Proses follow/unfollow selesai.")

BEARER_FILE = "bearer.txt"
CSV_FILE = "user_info.csv"
JSON_FILE = "user_info.json"

def get_user_info_from_token(bearer_token):
    # Pastikan token memiliki awalan "Bearer "
    if not bearer_token.lower().startswith("bearer "):
        formatted_bearer_token = f"Bearer {bearer_token}"
    else:
        formatted_bearer_token = bearer_token

    url = "https://client.farcaster.xyz/v2/onboarding-state"
    headers = {
        "authorization": formatted_bearer_token,
        "accept": "*/*"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.ok:
            data = response.json()["result"]["state"]
            email = data.get("email", "-")
            user = data.get("user", {})
            display_name = user.get("displayName", "-")
            username = user.get("username", "-")
            fid = user.get("fid", "-") # Extract fid

            spam_label = "-"
            if fid != "-":
                user_url = f"https://client.farcaster.xyz/v2/user?fid={fid}"
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        user_response = requests.get(user_url, headers=headers, timeout=10)
                        if user_response.ok:
                            user_data = user_response.json()
                            spam_label = user_data.get("result", {}).get("extras", {}).get("publicSpamLabel", "-")
                            break  # Exit loop if successful
                        else:
                            print(f"[!] Attempt {attempt + 1}/{max_retries}: Failed to fetch spam label for FID {fid}. Status: {user_response.status_code}")
                    except requests.exceptions.Timeout:
                        print(f"[!] Attempt {attempt + 1}/{max_retries}: Timeout fetching spam label for FID {fid}. Retrying...")
                    except Exception as e:
                        print(f"[!] Attempt {attempt + 1}/{max_retries}: Error fetching spam label for FID {fid}: {e}. Retrying...")
                    time.sleep(2) # Wait for 2 seconds before retrying
                else:
                    print(f"[✘] Failed to fetch spam label for FID {fid} after {max_retries} attempts.")

            return {
                "bearer": bearer_token,
                "email": email,
                "displayName": display_name,
                "username": username,
                "fid": fid,
                "spamLabel": spam_label
            }
        else:
            print(f"[✘] Gagal akses token: {bearer_token[:36]}... | Status: {response.status_code}")
    except Exception as e:
        print(f"[✘] Error: {e}")
    return None

def load_bearer_tokens(filename):
    try:
        with open(filename, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[!] File {filename} tidak ditemukan.")
        return []

def save_as_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Data disimpan ke {filename} (format JSON)")

def save_as_csv(data, filename):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["bearer", "email", "displayName", "username", "fid", "spamLabel"])
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print(f"✅ Data disimpan ke {filename} (format CSV)")

def process_onboarding_info():
    bearer_tokens = load_bearer_tokens(BEARER_FILE)
    all_data = []

    for i, token in enumerate(bearer_tokens):
        print(f"[{i+1}/{len(bearer_tokens)}] Memproses token...")
        result = get_user_info_from_token(token)
        if result:
            print(f"   ✅ {result['email']} | {result['displayName']} | {result['username']} | FID: {result['fid']} | Spam Label: {result['spamLabel']}")
            all_data.append(result)
        else:
            print("   ⚠️  Token tidak valid atau data tidak ditemukan.")

    if all_data:
        save_as_json(all_data, JSON_FILE)
        save_as_csv(all_data, CSV_FILE)
    else:
        print("❌ Tidak ada data yang berhasil diproses.")

if __name__ == "__main__":
    print("Pilih mode operasi:")
    print("1. Post Casts dari post.txt")
    print("2. Auto Like dan Recast")
    print("3. Follow/Unfollow User")
    print("4. Follow All Users")
    print("5. Ambil Info User (dari bearer.txt)")
    choice = input("Masukkan pilihan (1/2/3/4/5): ")

    if choice == '1':
        print("\nPilih opsi Post Casts:")
        print("1. Post Casts untuk semua akun (dari post.txt)")
        print("2. Post Casts per akun (masukkan teks manual)")
        sub_choice = input("Masukkan pilihan (1/2): ")

        if sub_choice == '1':
            post_casts_from_users()
        elif sub_choice == '2':
            post_single_cast_per_user()
        else:
            print("Pilihan tidak valid.")
    elif choice == '2':
        print("\nPilih opsi Auto Like dan Recast:")
        print("1. Auto Like dan Recast untuk semua akun")
        print("2. Auto Like dan Recast untuk akun terpilih")
        sub_choice = input("Masukkan pilihan (1/2): ")

        if sub_choice == '1':
            auto_like_and_recast_posts()
        elif sub_choice == '2':
            auto_like_recast_for_single_user()
        else:
            print("Pilihan tidak valid.")
    elif choice == '3':
        print("\nPilih opsi Follow/Unfollow:")
        print("1. Follow/Unfollow satu akun (pilih akun Anda)")
        print("2. Follow/Unfollow satu target untuk semua akun Anda")
        sub_choice = input("Masukkan pilihan (1/2): ")

        if sub_choice == '1':
            try:
                with open("user_info.json", 'r') as f:
                    users = json.load(f)
            except FileNotFoundError:
                print(f"Error: File 'user_info.json' not found.")
                import sys; sys.exit()
            except json.JSONDecodeError:
                print(f"Error: Could not decode JSON from 'user_info.json'.")
                import sys; sys.exit()

            if not users:
                print("No users found in user_info.json.")
                import sys; sys.exit()

            print("\nPilih akun Anda untuk melakukan follow/unfollow:")
            for i, user in enumerate(users):
                print(f"{i+1}. {user.get("username", "Unknown")} (FID: {user.get("fid")})")
            
            user_choice = input("Masukkan nomor akun: ")
            try:
                selected_user_index = int(user_choice) - 1
                if 0 <= selected_user_index < len(users):
                    selected_user = users[selected_user_index]
                    liker_bearer = selected_user.get("bearer")
                    if not liker_bearer:
                        print("Bearer token tidak ditemukan untuk akun ini.")
                        # return removed because it's not inside a function
                    bot = FarcasterBot(liker_bearer)

                    target_fid_str = input("Masukkan FID target (yang ingin di-follow/unfollow): ")
                    try:
                        target_fid = int(target_fid_str)
                    except ValueError:
                        print("FID tidak valid. Harus berupa angka.")
                        # return removed because it's not inside a function

                    action_choice = input("Pilih aksi (follow/unfollow): ").lower()
                    if action_choice == 'follow':
                        if bot.follow_user(target_fid):
                            print(f"Berhasil follow FID {target_fid}.")
                        else:
                            print(f"Gagal follow FID {target_fid}.")
                    elif action_choice == 'unfollow':
                        if bot.unfollow_user(target_fid):
                            print(f"Berhasil unfollow FID {target_fid}.")
                        else:
                            print(f"Gagal unfollow FID {target_fid}.")
                    else:
                        print("Aksi tidak valid. Pilih 'follow' atau 'unfollow'.")

                else:
                    print("Pilihan akun tidak valid.")
            except ValueError:
                print("Input tidak valid. Masukkan nomor.")

            while True:
                try:
                    min_delay_action = float(input("Masukkan delay minimum (detik) antara aksi (misal: 1): "))
                    max_delay_action = float(input("Masukkan delay maksimum (detik) antara aksi (misal: 5): "))
                    if min_delay_action < 0 or max_delay_action < min_delay_action:
                        raise ValueError("Delay tidak valid.")
                    break
                except ValueError as e:
                    print(f"Input tidak valid: {e}. Mohon masukkan angka yang benar.")

            # Apply delay after the action
            time.sleep(random.uniform(min_delay_action, max_delay_action))

        elif sub_choice == '2':
            follow_unfollow_single_target_for_all_users()
        else:
            print("Pilihan tidak valid.")
    elif choice == '4':
        follow_all_users()
    elif choice == '5':
        process_onboarding_info()
    else:
        print("Pilihan tidak valid.")