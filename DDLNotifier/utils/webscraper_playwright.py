# webscraper_playwright.py

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from playwright_stealth import stealth_sync  # pip install playwright-stealth
import time
import random

class WebScraperStealth:
    def __init__(self,
                 headless: bool = True,   # ⚠️ 改成 True，就不会依赖 X Server
                 browser_type: str = "chromium",
                 viewport: dict = {"width": 1366, "height": 768},
                 user_agent: str = None):
        self.headless = headless
        self.browser_type = browser_type
        self.viewport = viewport
        self.user_agent = user_agent
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
        self._init_browser()

    def _init_browser(self):
        """初始化浏览器"""
        if self.playwright:
            self.close()
            
        self.playwright = sync_playwright().start()
        browser_launcher = {
            "chromium": self.playwright.chromium,
            "firefox": self.playwright.firefox,
            "webkit": self.playwright.webkit,
        }
        if self.browser_type not in browser_launcher:
            raise ValueError(f"Unsupported browser_type: {self.browser_type}")

        # 增强的启动参数，提高反检测能力
        launch_args = {
            "headless": self.headless,
            "args": [
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",  # 隐藏自动化控制特征
                "--disable-features=VizDisplayCompositor",
                "--disable-extensions-file-access-check",
                "--disable-extensions-http-throttling", 
                "--disable-extensions-except",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--disable-field-trial-config",
                "--disable-back-forward-cache",
                "--disable-ipc-flooding-protection",
                "--no-first-run",
                "--no-default-browser-check",
                "--no-pings",
                "--password-store=basic",
                "--use-mock-keychain",
                "--force-webrtc-ip-handling-policy=disable_non_proxied_udp",
                "--disable-web-security",
                "--disable-features=TranslateUI",
                "--disable-ipc-flooding-protection",
                "--enable-automation=false",  # 禁用自动化标识
            ]
        }
        
        # 如果是非headless模式，移除一些可能造成问题的参数
        if not self.headless:
            launch_args["args"] = [arg for arg in launch_args["args"] 
                                 if not arg.startswith("--disable-web-security")]
        
        self.browser = browser_launcher[self.browser_type].launch(**launch_args)

        # 更真实的用户代理和上下文配置
        context_args = {
            "viewport": self.viewport,
            "user_agent": self.user_agent or
               "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
               "AppleWebKit/537.36 (KHTML, like Gecko) "
               "Chrome/120.0.0.0 Safari/537.36",
            "locale": "en-US",
            "timezone_id": "America/New_York",
            "extra_http_headers": {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9",
                "Cache-Control": "max-age=0",
                "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"',
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
            }
        }
        self.context = self.browser.new_context(**context_args)
        self.page = self.context.new_page()

        # 注入 Stealth，隐藏常见自动化指纹
        stealth_sync(self.page)
        
        # 额外的反检测脚本
        self.page.add_init_script("""
            // 覆盖 webdriver 属性
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // 覆盖 plugins 数组
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            // 覆盖 languages 属性
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
            
            // 模拟真实的鼠标移动
            window.chrome = {
                runtime: {},
            };
            
            // 删除自动化相关属性
            delete navigator.__proto__.webdriver;
        """)

    def _simulate_human_behavior(self):
        """模拟人类行为"""
        try:
            # 随机移动鼠标
            for _ in range(random.randint(2, 5)):
                x = random.randint(100, 800)
                y = random.randint(100, 600)
                self.page.mouse.move(x, y)
                time.sleep(random.uniform(0.1, 0.3))
            
            # 随机滚动
            for _ in range(random.randint(1, 3)):
                self.page.mouse.wheel(0, random.randint(100, 300))
                time.sleep(random.uniform(0.5, 1.0))
        except Exception as e:
            print(f"模拟行为失败: {e}")

    def _goto_and_wait(self,
                      url: str,
                      selector: str = "body",
                      timeout: int = 15000,
                      check_visibility: bool = False,
                      retry_with_visible: bool = True):
        print(f"👉 Go to: {url}")
        try:
            # 随机延迟，模拟人类行为
            time.sleep(random.uniform(2, 4))
            
            # 导航到 URL
            self.page.goto(url, timeout=timeout, wait_until="domcontentloaded")
            
            # 检查是否遇到 Cloudflare 挑战页面
            if "Just a moment" in self.page.title() or "cloudflare" in self.page.url.lower():
                print("🛡️ 检测到 Cloudflare 挑战页面...")
                
                # 如果当前是headless模式且允许重试，切换到非headless模式
                if self.headless and retry_with_visible:
                    print("🔄 切换到可视模式重试...")
                    self.headless = False
                    self._init_browser()
                    return self._goto_and_wait(url, selector, timeout, check_visibility, False)
                
                print("⏳ 等待 Cloudflare 验证...")
                # 模拟人类行为
                self._simulate_human_behavior()
                
                # 增加等待时间，给 Cloudflare 更多时间完成验证
                for i in range(6):  # 最多等待 60 秒
                    time.sleep(10)
                    print(f"⏳ 等待验证中... ({(i+1)*10}s)")
                    
                    # 继续模拟人类行为
                    if i % 2 == 0:
                        self._simulate_human_behavior()
                    
                    try:
                        # 检查页面是否已经跳转或标题是否改变
                        current_title = self.page.title()
                        if "Just a moment" not in current_title:
                            print(f"✅ 验证完成，当前标题: {current_title}")
                            break
                    except:
                        continue
                else:
                    print("⚠️ Cloudflare 验证可能未完成，继续尝试...")
            
            # 人为多等待，让 JS 验证有机会跑完
            time.sleep(random.uniform(3, 6))
            
            # 再次模拟人类行为
            self._simulate_human_behavior()

            # 然后再去等待某个 selector
            if check_visibility:
                self.page.wait_for_selector(selector, timeout=timeout, state="visible")
            else:
                self.page.wait_for_selector(selector, timeout=timeout, state="attached")
                
        except PlaywrightTimeoutError:
            print(f"⛔️ Timeout: 在 {timeout}ms 内未找到 {selector}")
            print(f"📄 当前页面标题: {self.page.title()}")
            print(f"🔗 当前页面URL: {self.page.url}")
            self.page.screenshot(path="debug_stealth.png", full_page=True)
            print("📸 已保存调试截图: debug_stealth.png")

        return self.page.content()

    def get_html_UCL(self, url: str) -> str:
        return self._goto_and_wait(url,
                                   selector=".result-item",
                                   timeout=45000,  # 增加到 45 秒
                                   check_visibility=True)

    def get_html(self, url: str) -> str:
        return self._goto_and_wait(url,
                                   selector="body",
                                   timeout=15000,
                                   check_visibility=False)

    def get_cookies(self, url: str) -> list[dict]:
        _ = self._goto_and_wait(url, selector="body", timeout=15000, check_visibility=False)
        return self.context.cookies()

    @staticmethod
    def format_cookies_for_request_header(cookies: list[dict]) -> str:
        parts = [f"{c['name']}={c['value']}" for c in cookies]
        return "; ".join(parts)

    def get_cookie_string(self, url: str) -> str:
        cookies = self.get_cookies(url)
        return self.format_cookies_for_request_header(cookies)

    def close(self):
        try:
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
        finally:
            if self.playwright:
                self.playwright.stop()


if __name__ == "__main__":
    print("🚀 启动增强版 WebScraper...")
    print("💡 提示：如果遇到 Cloudflare，脚本会自动切换到可视模式")
    print("📌 注意：可视模式需要 X11 转发或图形界面支持")
    
    # —— 先尝试 headless 模式 —— #
    scraper = WebScraperStealth(headless=True, browser_type="chromium")

    test_url = "https://www.ucl.ac.uk/prospective-students/graduate/taught-degrees"
    html = scraper.get_html_UCL(test_url)
    print("返回的 HTML 长度：", len(html))
    
    # 检查是否成功获取到正确内容
    if "Just a moment" in html:
        print("❌ 仍然遇到 Cloudflare 挑战页面")
        print("📄 页面标题包含验证信息")
        print("💡 建议：在有图形界面的环境中运行，或考虑使用代理服务")
    elif ".result-item" in html or "course" in html.lower():
        print("✅ 成功获取到页面内容")
    else:
        print("⚠️ 获取到内容，但可能不完整")
    
    # 显示页面开头内容以便调试
    print("\n🔍 页面内容预览 (前500字符):")
    print(html[:500] + "..." if len(html) > 500 else html)

    scraper.close()