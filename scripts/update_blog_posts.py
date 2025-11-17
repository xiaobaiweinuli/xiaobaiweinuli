#!/usr/bin/env python3
import requests
import xmltodict
from datetime import datetime
import os
import re

def update_readme():
    # 获取 Atom feed
    feed_url = "https://blog.xingshuang.xyz/atom.xml"
    response = requests.get(feed_url)
    response.raise_for_status()
    
    # 解析 XML
    data = xmltodict.parse(response.content)
    entries = data['feed']['entry']
    
    # 处理文章数据
    articles = []
    for entry in entries[:5]:  # 只取最新5篇
        title = entry['title']['#text'] if '#text' in entry['title'] else entry['title']
        # 清理标题中的特殊字符
        title = re.sub(r'[\[\]]', '', title)
        
        # 获取链接
        if isinstance(entry['link'], list):
            link = entry['link'][0]['@href']
        else:
            link = entry['link']['@href']
            
        # 处理日期
        pub_date = entry.get('published', entry.get('updated', ''))
        if pub_date:
            date_obj = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
            formatted_date = date_obj.strftime('%Y-%m-%d')
        else:
            formatted_date = "未知日期"
            
        articles.append({
            'date': formatted_date,
            'title': title,
            'link': link
        })
    
    # 生成博客内容
    blog_lines = []
    for article in articles:
        line = f"{article['date']}-[{article['title']}]({article['link']})"
        blog_lines.append(line)
    
    blog_content = "\n".join(blog_lines)
    
    # 读取并更新 README
    with open('README.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    start_marker = "<!-- BLOG_POSTS_START -->"
    end_marker = "<!-- BLOG_POSTS_END -->"
    
    # 替换内容
    pattern = f"{re.escape(start_marker)}.*?{re.escape(end_marker)}"
    replacement = f"{start_marker}\n{blog_content}\n{end_marker}"
    
    if re.search(pattern, content, re.DOTALL):
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    else:
        # 如果标记不存在，添加到文件末尾
        new_content = content + f"\n\n{start_marker}\n{blog_content}\n{end_marker}\n"
    
    # 写回文件
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("README updated successfully!")

if __name__ == "__main__":
    update_readme()