import requests
from bs4 import BeautifulSoup, Tag
from typing import Dict, List, Optional, Union
import sys


def scrape_bangumi(subject_id: Union[int, str]) -> Dict[str, Union[str, List[str], None]]:
    """从 Bangumi 抓取番剧信息

    Args:
        subject_id: Bangumi 番剧 ID（数字或字符串形式）

    Returns:
        包含以下键的字典：
        - 'name': 中文名称（字符串，可能为 None）
        - 'summary': 剧情简介（字符串，可能为 None）
        - 'cover_url': 封面图片 URL（字符串，可能为 None）
        - 'tags': 标签列表（字符串列表，可能为空）
        - 'error': 错误信息（仅当发生错误时存在）
    """
    url = f"https://bangumi.tv/subject/{subject_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }

    try:
        # 发送 HTTP 请求
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        response.raise_for_status()  # 检查 HTTP 状态码

        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. 提取中文名称
        name: Optional[str] = None

        # 方法1：尝试从基本信息中提取
        info_box: Optional[Tag] = soup.find('ul', id='infobox')
        if info_box:
            for li in info_box.find_all('li'):
                text: str = li.get_text().strip()
                if text.startswith('中文名:'):
                    # 提取中文名（去除"中文名:"前缀）
                    name = text.split(':', 1)[1].strip()
                    break

        # 方法2：如果基本信息中没有，尝试从标题中提取
        if not name:
            title_elem: Optional[Tag] = soup.find('h1', class_='nameSingle')
            if title_elem:
                # 尝试提取中文部分（通常在小标签中）
                chinese_part: Optional[Tag] = title_elem.find('small', lang='zh') or title_elem.find('a', lang='zh')
                if chinese_part:
                    name = chinese_part.get_text().strip()
                else:
                    # 如果没有明确标记，直接使用标题
                    name = title_elem.get_text().strip()

        # 2. 提取简介
        summary_elem: Optional[Tag] = soup.find('div', id='subject_summary')
        summary: Optional[str] = summary_elem.text.strip() if summary_elem else None

        # 3. 提取封面URL
        cover_elem: Optional[Tag] = soup.find('img', class_='cover')
        cover_url: Optional[str] = cover_elem['src'] if cover_elem else None
        if cover_url and cover_url.startswith('//'):
            cover_url = 'https:' + cover_url

        # 4. 提取标签
        tags: List[str] = []
        # 定位到标签容器
        tag_container: Optional[Tag] = soup.find('div', class_='subject_tag_section')
        if tag_container:
            # 找到内部容器
            inner_div: Optional[Tag] = tag_container.find('div', class_='inner')
            if inner_div:
                # 提取所有标签链接（排除"更多+"）
                tag_links: List[Tag] = inner_div.find_all('a', class_='l')

                for link in tag_links:
                    # 排除"更多+"链接
                    if link.get('id') == 'show_user_tags':
                        continue

                    # 提取标签文本（位于 <span> 中）
                    span_tag: Optional[Tag] = link.find('span')
                    if span_tag:
                        tag_text: str = span_tag.text.strip()
                        # 添加到标签列表
                        tags.append(tag_text)

        return {
            'name': name,
            'summary': summary,
            'cover_url': cover_url,
            'tags': tags
        }

    except requests.exceptions.RequestException as e:
        return {'error': f"网络请求失败: {str(e)}"}
    except Exception as e:
        return {'error': f"处理错误: {str(e)}"}


def setup_console_encoding() -> None:
    """配置控制台使用UTF-8编码"""
    if sys.platform.startswith('win'):
        # Windows系统需要特殊处理
        import ctypes
        try:
            # 设置控制台代码页为UTF-8
            ctypes.windll.kernel32.SetConsoleOutputCP(65001)
            ctypes.windll.kernel32.SetConsoleCP(65001)
        except Exception:
            pass
    # Linux/macOS 通常默认支持UTF-8，无需额外处理


if __name__ == "__main__":
    # 配置控制台编码
    setup_console_encoding()

    subject_id = 292970  # 魔女之旅的ID

    result: Dict[str, Union[str, List[str], None]] = scrape_bangumi(subject_id)

    if 'error' in result:
        print(f"错误: {result['error']}")
    else:
        print("=== 提取结果 ===")
        print(f"中文名称: {result['name']}")
        print(f"\n简介: {result['summary']}")
        print(f"\n封面URL: {result['cover_url']}")

        if result['tags']:
            print("\n标签:")
            for i, tag in enumerate(result['tags'], 1):
                print(f"{i}. {tag}")
        else:
            print("\n标签: 未找到标签信息")