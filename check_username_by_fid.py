import requests
import json

def get_username_by_fid(fid):
    url = f"https://client.farcaster.xyz/v2/user?fid={fid}"
    headers = {
        "accept": "*/*",
        "user-agent": "Mozilla/5.0",
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        
        data = response.json()
        username = data.get("result", {}).get("user", {}).get("username")
        display_name = data.get("result", {}).get("user", {}).get("displayName")
        follower_count = data.get("result", {}).get("user", {}).get("followerCount")

        if username:
            return username, display_name, follower_count
        else:
            return None, None, None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for FID {fid}: {e}")
        return None, None, None

if __name__ == "__main__":
    print("Bot untuk memeriksa username dan jumlah follower Farcaster berdasarkan FID.")
    while True:
        fid_input = input("Masukkan FID (atau 'exit' untuk keluar): ")
        if fid_input.lower() == 'exit':
            break
        
        try:
            fid = int(fid_input)
            username, display_name, follower_count = get_username_by_fid(fid)
            if username:
                print(f"FID: {fid}\n  Username: {username}\n  Display Name: {display_name}\n  Follower Count: {follower_count}")
            else:
                print(f"Tidak dapat menemukan informasi untuk FID {fid}. Mungkin FID tidak valid atau terjadi kesalahan API.")
        except ValueError:
            print("Input tidak valid. FID harus berupa angka.")
        print("\n")

