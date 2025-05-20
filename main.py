
import requests
import json
import time
import itertools

# 从文件中加载 token
def load_tokens(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

# 从文件中加载代理（格式：ip:port）
def load_proxies(proxy_file):
    with open(proxy_file, "r", encoding="utf-8") as f:
        proxies = [line.strip() for line in f if line.strip()]
    return itertools.cycle(proxies)  # 无限循环代理列表

# 将数据保存到文件
def save_to_file(filename, token, user_data):
    with open(filename, "a", encoding="utf-8") as f:
        f.write(json.dumps({"token": token, **user_data}, ensure_ascii=False) + "\n")

# 检查 token 的信息
def check_token(token, proxy):
    proxies = {
        "http": f"http://{proxy}",
        "https": f"http://{proxy}"
    }

    headers = {
        "Authorization": token,
        "User-Agent": "Mozilla/5.0"
    }

    try:
        res = requests.get("https://discord.com/api/v6/users/@me", headers=headers, proxies=proxies, timeout=15)
        if res.status_code != 200:
            return None
        user = res.json()

        # 检查是否手机号锁
        res2 = requests.get("https://discord.com/api/v6/users/@me/library", headers=headers, proxies=proxies, timeout=15)
        phone_locked = res2.status_code != 200

        return {
            "email": user.get("email"),
            "verified": user.get("verified"),
            "phone": user.get("phone"),
            "phone_locked": phone_locked,
            "username": user.get("username"),
            "discriminator": user.get("discriminator"),
            "id": user.get("id"),
        }

    except Exception as e:
        print(f"[ERROR] Token {token[:10]}...: {e}")
        return None

# 主逻辑
def main():
    token_file = "tokens.txt"
    proxy_file = "proxies.txt"

    verified_file = "verified_and_phone.txt"
    verified_no_phone_file = "verified_no_phone.txt"
    unverified_file = "unverified_email.txt"

    tokens = load_tokens(token_file)
    proxy_pool = load_proxies(proxy_file)

    print(f"共载入 {len(tokens)} 个 token")

    for i, token in enumerate(tokens):
        print(f"\n[{i+1}/{len(tokens)}] 正在处理 token：{token[:10]}...")

        proxy = next(proxy_pool)

        user_data = check_token(token, proxy)
        if not user_data:
            print("无效 token 或请求失败")
            continue

        if not user_data["verified"]:
            save_to_file(unverified_file, token, user_data)
            print("➡️ 未验证邮箱，已保存")
        elif user_data["verified"] and not user_data["phone"]:
            save_to_file(verified_no_phone_file, token, user_data)
            print("➡️ 已验证邮箱，无手机号，已保存")
        elif user_data["verified"] and user_data["phone"]:
            save_to_file(verified_file, token, user_data)
            print("✅ 邮箱+手机号均验证，已保存")

        time.sleep(2)

if __name__ == "__main__":
    main()
