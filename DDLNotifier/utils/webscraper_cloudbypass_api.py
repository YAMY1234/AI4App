# webscraper_cloudbypass_api.py
# 使用穿云API绕过Cloudflare防护

import requests
import time
import random
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

class CloudBypassAPIScraper:
    def __init__(self, api_key: str = "103fa266894f44d5b38248128b1d656d"):
        self.api_key = api_key
        self.api_base_url = "https://api.cloudbypass.com"
        self.session = requests.Session()
        self.setup_session()
    
    def setup_session(self):
        """设置会话"""
        self.session.headers.update({
            'x-cb-apikey': self.api_key,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        print(f"✅ 穿云API初始化完成，API Key: {self.api_key[:8]}...")

    def get_html_content(self, target_url: str, verbose: bool = False) -> Optional[str]:
        """
        获取指定URL的HTML内容（通过穿云API绕过Cloudflare）
        
        Args:
            target_url: 目标URL
            verbose: 是否输出详细日志
            
        Returns:
            HTML内容字符串，失败时返回None
        """
        try:
            if verbose:
                print(f"🌩️ 使用穿云API获取: {target_url}")
            
            # 从目标URL提取主机名
            parsed_url = urlparse(target_url)
            host = parsed_url.netloc
            path = parsed_url.path
            if parsed_url.query:
                path += "?" + parsed_url.query
            
            # 构建API请求URL
            api_url = f"{self.api_base_url}{path}"
            
            headers = {
                'x-cb-apikey': self.api_key,
                'x-cb-host': host,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            
            if verbose:
                print(f"📡 API URL: {api_url}")
                print(f"🏠 目标主机: {host}")
            
            # 随机延迟
            time.sleep(random.uniform(1, 3))
            
            response = self.session.get(api_url, headers=headers, timeout=30)
            
            if verbose:
                print(f"📊 响应状态码: {response.status_code}")
                print(f"📏 响应大小: {len(response.text)} 字符")
            
            if response.status_code == 200:
                # 检查响应内容
                if "Just a moment" in response.text:
                    if verbose:
                        print("⚠️ 响应仍包含Cloudflare挑战页面")
                    return None
                elif len(response.text) > 1000:  # 合理的页面大小
                    if verbose:
                        print("✅ 穿云API调用成功")
                    return response.text
                else:
                    if verbose:
                        print("⚠️ 响应内容可能不完整")
                    return response.text
            else:
                if verbose:
                    print(f"❌ 穿云API调用失败，状态码: {response.status_code}")
                return None
                
        except Exception as e:
            if verbose:
                print(f"❌ 穿云API调用异常: {e}")
            return None

    def extract_ucl_courses(self, html_content: str, source_url: str, verbose: bool = False) -> List[Dict]:
        """
        从HTML内容中提取UCL课程信息
        
        Args:
            html_content: HTML内容
            source_url: 源URL
            verbose: 是否输出详细日志
            
        Returns:
            课程信息列表
        """
        if not html_content:
            return []
            
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            courses = []
            
            if verbose:
                print(f"🔍 开始提取课程信息...")
                print(f"📄 HTML标题: {soup.title.string if soup.title else 'Unknown'}")
            
            # 检查页面是否有效
            if "Just a moment" in html_content:
                if verbose:
                    print("⚠️ 内容仍然是Cloudflare挑战页面")
                return []
            
            # 多种提取策略
            selectors_to_try = [
                '.result-item',
                '.course-item', 
                '.programme-item',
                '.course-card',
                '.degree-item',
                '[data-course]',
                '.search-result',
                '.course-listing',
                '.program-item',
                '.course-details',
                '.degree-programme'
            ]
            
            # 尝试CSS选择器
            for selector in selectors_to_try:
                elements = soup.select(selector)
                if elements:
                    if verbose:
                        print(f"✅ 找到 {len(elements)} 个课程元素 (选择器: {selector})")
                    for elem in elements:
                        course_info = self._extract_course_from_element(elem, source_url)
                        if course_info:
                            courses.append(course_info)
                    if courses:
                        break
            
            # 如果选择器没找到，尝试链接提取
            if not courses:
                if verbose:
                    print("🔍 尝试通过链接提取课程信息...")
                links = soup.find_all('a', href=True)
                course_keywords = ['master', 'msc', 'ma', 'course', 'programme', 'degree', 'taught', 'graduate']
                
                for link in links:
                    text = link.get_text(strip=True)
                    href = link.get('href', '')
                    
                    if (len(text) > 25 and len(text) < 200 and 
                        any(keyword in text.lower() for keyword in course_keywords) and
                        ('ucl.ac.uk' in href or href.startswith('/'))):
                        
                        courses.append({
                            'title': text,
                            'url': urljoin(source_url, href),
                            'description': '',
                            'source': 'link_extraction'
                        })
                        
                        if len(courses) >= 50:
                            break
            
            if verbose:
                print(f"📋 总共提取到 {len(courses)} 个课程")
            return courses
            
        except Exception as e:
            if verbose:
                print(f"❌ 提取课程信息失败: {e}")
            return []

    def _extract_course_from_element(self, element, base_url: str) -> Optional[Dict]:
        """从单个元素提取课程信息"""
        try:
            # 提取标题
            title_selectors = ['h1', 'h2', 'h3', 'h4', '.title', '.course-title', '.programme-title', 'a']
            title = ""
            
            for selector in title_selectors:
                title_elem = element.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if title and len(title) > 5 and len(title) < 300:
                        break
            
            if not title:
                title = element.get_text(strip=True)[:200]
            
            # 提取链接
            link_elem = element.find('a', href=True)
            url = urljoin(base_url, link_elem.get('href', '')) if link_elem else base_url
            
            # 提取描述
            desc_selectors = ['.description', '.summary', '.excerpt', 'p']
            description = ""
            for selector in desc_selectors:
                desc_elem = element.select_one(selector)
                if desc_elem:
                    description = desc_elem.get_text(strip=True)
                    if description and len(description) > 10:
                        break
            
            if title and len(title) > 5:
                return {
                    'title': title,
                    'url': url,
                    'description': description[:300],
                    'source': 'element_extraction'
                }
        except Exception as e:
            return None
        
        return None

    def close(self):
        """清理资源"""
        if self.session:
            self.session.close()


# 全局实例
_default_scraper = None

def get_default_scraper() -> CloudBypassAPIScraper:
    """获取默认的穿云API爬虫实例"""
    global _default_scraper
    if _default_scraper is None:
        _default_scraper = CloudBypassAPIScraper()
    return _default_scraper

def get_html_ucl_cloudbypass(url: str, verbose: bool = False) -> str:
    """
    使用穿云API获取UCL网页HTML内容
    
    Args:
        url: 目标URL
        verbose: 是否输出详细日志
        
    Returns:
        HTML内容字符串
    """
    scraper = get_default_scraper()
    html_content = scraper.get_html_content(url, verbose=verbose)
    return html_content or ""

def get_ucl_courses_cloudbypass(url: str = None, verbose: bool = False) -> List[Dict]:
    """
    使用穿云API获取UCL课程信息
    
    Args:
        url: 目标URL，默认为UCL研究生课程页面
        verbose: 是否输出详细日志
        
    Returns:
        课程信息列表，每个元素包含title、url、description、source字段
    """
    if url is None:
        url = "https://www.ucl.ac.uk/prospective-students/graduate/taught-degrees"
    
    scraper = get_default_scraper()
    html_content = scraper.get_html_content(url, verbose=verbose)
    
    if html_content:
        courses = scraper.extract_ucl_courses(html_content, url, verbose=verbose)
        return courses
    else:
        if verbose:
            print("❌ 无法获取HTML内容")
        return []

def cleanup_scraper():
    """清理全局爬虫实例"""
    global _default_scraper
    if _default_scraper:
        _default_scraper.close()
        _default_scraper = None


if __name__ == "__main__":
    print("🚀 启动穿云API UCL课程信息获取工具")
    print("💡 使用专业的穿云API服务绕过Cloudflare防护")
    
    try:
        # 测试获取课程信息
        courses = get_ucl_courses_cloudbypass(verbose=True)
        
        print(f"\n📊 结果:")
        print(f"📈 找到课程总数: {len(courses)}")
        
        if courses:
            print(f"\n🎓 UCL课程列表 (前10个):")
            for i, course in enumerate(courses[:10], 1):
                print(f"\n{i}. {course['title']}")
                print(f"   🔗 URL: {course['url']}")
                if course['description']:
                    print(f"   📝 描述: {course['description'][:100]}...")
                print(f"   🔍 来源: {course['source']}")
        else:
            print("\n❌ 未找到任何课程信息")
        
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cleanup_scraper() 