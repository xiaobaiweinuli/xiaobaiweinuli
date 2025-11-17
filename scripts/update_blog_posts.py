#!/usr/bin/env python3
"""
从Atom feed读取文章并更新README.md
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import re
from urllib.parse import urlparse

# 配置
ATOM_FEED_URL = "https://blog.xingshuang.xyz/atom.xml"
README_FILE = "README.md"

# Atom feed 命名空间
NAMESPACE = {'atom': 'http://www.w3.org/2005/Atom'}

def parse_atom_feed(feed_url):
    """解析Atom feed并返回文章列表"""
    try:
        response = requests.get(feed_url, timeout=10)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        
        articles = []
        for entry in root.findall('atom:entry', NAMESPACE):
            title_elem = entry.find('atom:title', NAMESPACE)
            link_elem = entry.find('atom:link', NAMESPACE)
            published_elem = entry.find('atom:published', NAMESPACE)
            updated_elem = entry.find('atom:updated', NAMESPACE)
            
            if title_elem is not None and link_elem is not None:
                title = title_elem.text.strip() if title_elem.text else ""
                link = link_elem.get('href', '')
                
                # 使用发布时间，如果没有则使用更新时间
                date_elem = published_elem if published_elem is not None else updated_elem
                if date_elem is not None and date_elem.text:
                    # 解析ISO格式时间并转换为YYYY-MM-DD
                    try:
                        pub_date = datetime.fromisoformat(date_elem.text.replace('Z', '+00:00'))
                        formatted_date = pub_date.strftime('%Y-%m-%d')
                    except ValueError:
                        formatted_date = "未知日期"
                else:
                    formatted_date = "未知日期"
                
                if title and link:
                    articles.append({
                        'title': title,
                        'link': link,
                        'date': formatted_date
                    })
        
        # 按日期倒序排列（最新的在前）
        articles.sort(key=lambda x: x['date'], reverse=True)
        return articles
        
    except Exception as e:
        print(f"解析Atom feed时出错: {e}")
        return []

def generate_blog_section(articles):
    """生成博客文章部分的Markdown"""
    if not articles:
        return "暂无博客文章"
    
    lines = []
    for article in articles:
        # 清理标题中的特殊字符
        clean_title = re.sub(r'[\[\]]', '', article['title'])
        line = f"{article['date']}-[{clean_title}]({article['link']})"
        lines.append(line)
    
    return "\n".join(lines)

def update_readme(blog_content):
    """更新README文件"""
    try:
        with open(README_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 定义标记
        start_marker = "<!-- BLOG_POSTS_START -->"
        end_marker = "<!-- BLOG_POSTS_END -->"
        
        # 检查标记是否存在
        if start_marker in content and end_marker in content:
            # 替换标记之间的内容
            pattern = f"{re.escape(start_marker)}.*?{re.escape(end_marker)}"
            replacement = f"{start_marker}\n{blog_content}\n{end_marker}"
            new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        else:
            # 如果标记不存在，在文件末尾添加
            new_content = content + f"\n\n{start_marker}\n{blog_content}\n{end_marker}\n"
        
        # 写入文件
        with open(README_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("README.md 更新成功！")
        return True
        
    except Exception as e:
        print(f"更新README时出错: {e}")
        return False

def main():
    print("开始更新博客文章...")
    
    # 获取文章列表
    articles = parse_atom_feed(ATOM_FEED_URL)
    print(f"找到 {len(articles)} 篇文章")
    
    # 生成博客内容
    blog_content = generate_blog_section(articles)
    
    # 更新README
    if update_readme(blog_content):
        print("更新完成！")
    else:
        print("更新失败！")
        exit(1)

if __name__ == "__main__":
    main()