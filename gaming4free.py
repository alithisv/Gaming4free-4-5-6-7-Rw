import time
import os
import random
import requests

if "DISPLAY" not in os.environ:
    os.environ["DISPLAY"] = ":1"
    
if "XAUTHORITY" not in os.environ:
    if os.path.exists("/home/headless/.Xauthority"):
        os.environ["XAUTHORITY"] = "/home/headless/.Xauthority"

from seleniumbase import SB
from selenium.webdriver.common.action_chains import ActionChains

# ================= 配置区域 =================
PROXY_URL = os.getenv("PROXY", "")  
TG_TOKEN = os.getenv("TG_TOKEN")  
TG_CHAT_ID = os.getenv("TG_CHAT_ID")  
SERVERS = os.getenv("SERVERS", "").strip()  

SERVER_LIST = []
if SERVERS:
    for item in SERVERS.split("|"):
        try:
            num, region = item.split(",", 1)
            SERVER_LIST.append({"num": num.strip(), "region": region.strip()})
        except:
            print(f"⚠️ SERVERS 配置格式错误: {item}")
# ===========================================

class Game4FreeRenewal:
    def __init__(self):
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.screenshot_dir = os.path.join(self.BASE_DIR, "artifacts")
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)

    def log(self, msg):
        timestamp = time.strftime('%H:%M:%S')
        print(f"[{timestamp}] [INFO] {msg}", flush=True)

    def human_wait(self, min_s=6, max_s=10):
        time.sleep(random.uniform(min_s, max_s))

    def time_to_seconds(self, t_str):
        if not t_str or "EXPIRED" in t_str.upper() or "未知" in t_str:
            return 0
        try:
            h, m, s = map(int, t_str.strip().split(':'))
            return h * 3600 + m * 60 + s
        except:
            return 0

    def send_telegram_notify(self, message, photo_path=None, force=False):
        if not TG_TOKEN or not TG_CHAT_ID:
            self.log("⚠️ 未配置 TG_TOKEN，跳过推送。")
            return

        try:
            if photo_path and os.path.exists(photo_path):
                url = f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto"
                with open(photo_path, 'rb') as f:
                    requests.post(url, data={'chat_id': TG_CHAT_ID, 'caption': message}, files={'photo': f})
            else:
                url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
                requests.post(url, data={'chat_id': TG_CHAT_ID, 'text': message})
            self.log("✅ TG 推送已发送")
        except Exception as e:
            self.log(f"❌ TG 推送失败: {e}")

    def run_single_server(self, server_num, region):
        URL_APP_PANEL = f"https://gaming4free.net/servers/{server_num}"

        self.log("=" * 40)
        self.log(f"🚀 开始续期 [{region}] ({server_num})")
        
        CHROMIUM_ARGS = "--no-sandbox,--disable-dev-shm-usage,--disable-gpu,--window-position=0,0,--window-size=1280,720,--disable-blink-features=AutomationControlled,--disable-infobars,--disable-popup-blocking,--disable-features=OptimizationGuideModelDownloading,OptimizationHintsFetching,OptimizationTargetPrediction"

        with SB(
            uc=True,
            test=True,
            headed=True,
            headless=False,
            xvfb=False, 
            chromium_arg=CHROMIUM_ARGS,
            proxy=PROXY_URL if PROXY_URL else None
        ) as sb:
            try:
                self.log("✅ 浏览器已启动！")

                try:
                    proxies = {"http": PROXY_URL, "https": PROXY_URL} if PROXY_URL else None
                    ip_val = requests.get("https://api.ipify.org?format=json", proxies=proxies, timeout=10).json().get('ip', 'Unknown')
                    self.log(f"✅ 当前出口 IP: {ip_val}")
                except Exception:
                    self.log("⚠️ 无法获取出口 IP，跳过。")

                self.log(f"📂 正在进入续期面板 [{region}] ...")
                sb.uc_open_with_reconnect(URL_APP_PANEL, reconnect_time=5)
                self.human_wait(8, 12)

                if "login" in sb.get_current_url().lower():
                    raise Exception("登录状态失效或权限被拒绝。")

                # 点击同意 Cookies
                cookie_btns = ['//button[contains(., "Continue with Recommended Cookies")]', '//button[contains(., "Accept")]', '//button[contains(., "I Agree")]', '//button[contains(., "Consent")]']
                for btn in cookie_btns:
                    if sb.is_element_present(btn):
                        try:
                            sb.click(btn)
                            break
                        except:
                            pass

                # 获取时间
                timestamp_before = "未知"
                try:
                    sb.wait_for_element_visible('#sd-timer', timeout=15)
                    timestamp_before = sb.get_text('#sd-timer').strip()
                except:
                    pass
                self.log(f"🕒 续期前剩余运行时间: {timestamp_before}")

                ActionChains(sb.driver).scroll_by_amount(0, 600).perform()
                self.human_wait(2, 4)
                
                try:
                    self.log("🖱️ 正在点击 'VOTE + ADD 90 MIN'...")
                    sb.wait_for_element_visible("#sd-vote-btn", timeout=10)
                    sb.click('#sd-vote-btn')
                except Exception as e:
                    raise Exception(f"未找到打开模态框的按钮: {e}")

                self.log("⏳ 等待 15 秒，确保模态框加载...")
                time.sleep(15)  
                
                token = ""
                for attempt in range(5):
                    self.log(f"⚡ 尝试定位并物理破解 Cloudflare (尝试 {attempt+1}/5)...")
                    
                    try:
                        sb.uc_gui_click_captcha()
                    except Exception:
                        pass

                    try:
                        iframes = sb.driver.find_elements("tag name", "iframe")
                        for f in iframes:
                            src = f.get_attribute("src") or ""
                            if "cloudflare" in src.lower() or "turnstile" in src.lower() or "challenges" in src.lower():
                                ac = ActionChains(sb.driver)
                                ac.move_to_element(f).click().perform()
                                break
                    except Exception as e:
                        self.log(f"   -> ⚠️ 寻找/点击 iframe 异常: {e}")
                    
                    self.log("   -> ⏳ 等待验证回调 (5 秒)...")
                    time.sleep(5)
                    
                    try:
                        temp_token = sb.execute_script("return document.querySelector('[name=\"cf-turnstile-response\"]') ? document.querySelector('[name=\"cf-turnstile-response\"]').value : ''")
                        if temp_token and len(temp_token.strip()) > 50:
                            token = temp_token.strip()
                            self.log(f"✅ 成功！获取到有效 Cloudflare 凭证 (Token 长度: {len(token)})")
                            break
                        else:
                            self.log("   -> ⚠️ 未检测到有效 Token，继续尝试...")
                    except Exception as e:
                        self.log(f"   -> ⚠️ 读取 Token 异常: {e}")
                
                if not token:
                    self.log("⚠️ 未能获取到有效的 Cloudflare 凭证，尝试直接点击提交...")

                self.human_wait(2, 4)

                try:
                    self.log("🖱️ 正在点击最终提交按钮 'VOTE — ADDS 90 MINUTES'...")
                    sb.wait_for_element_visible("#vm-submit", timeout=15)
                    sb.uc_click('#vm-submit') 
                    self.human_wait(8, 12)
                except Exception as e:
                    raise Exception("未能点击最终的确认提交按钮")

                time.sleep(10)
                
                timestamp_after = "未知"
                try:
                    timestamp_after = sb.get_text('#sd-timer').strip()
                except:
                    pass
                self.log(f"🕒 续期后剩余运行时间: {timestamp_after}")

                sec_before = self.time_to_seconds(timestamp_before)
                sec_after = self.time_to_seconds(timestamp_after)
                
                if sec_after <= sec_before + 60 and sec_before != 0:  
                    raise Exception(f"❌ 时间未增加！(前: {timestamp_before}, 后: {timestamp_after})。")

                final_screenshot = f"{self.screenshot_dir}/final_success_{server_num}.png"
                sb.save_screenshot(final_screenshot)

                msg = f"✅ [{region}] 续期成功\n🖥️ 编号: {server_num}\n🕒 续期前时间: {timestamp_before}\n🎉 续期后时间: {timestamp_after}"
                self.send_telegram_notify(msg, final_screenshot)

            except Exception as e:
                self.log(f"❌ 运行异常: {e}")
                error_shot = f"{self.screenshot_dir}/error_{server_num}.png"
                try: sb.save_screenshot(error_shot)
                except: pass
                self.send_telegram_notify(f"❌ [{region}] 执行失败: {e}\n🖥️ 编号: {server_num}", error_shot, force=True)

    def run(self):
        if not SERVER_LIST:
            self.log("❌ 未配置 SERVERS")
            return
        for i, server in enumerate(SERVER_LIST):
            if i > 0:
                self.log("⏳ 为防止同 IP 被频繁请求限制，暂停 15 秒后继续下一个服务器...")
                time.sleep(15)  # 已修改为 15 秒间隔
            self.run_single_server(server["num"], server["region"])

if __name__ == "__main__":
    Game4FreeRenewal().run()
