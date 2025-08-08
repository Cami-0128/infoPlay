from flask import Blueprint, render_template
from flask_login import login_required
import feedparser
import requests
from datetime import datetime

info = Blueprint('info', __name__, url_prefix='/info')

@info.route('/')
@login_required
def info_page():
    weather = None
    articles = []
    
    # 取得天氣資訊
    try:
        res = requests.get('https://wttr.in/Taipei?format=j1', timeout=10)
        if res.status_code == 200:
            data = res.json()
            weather = {
                'city': data['nearest_area'][0]['areaName'][0]['value'],
                'weather': data['current_condition'][0]['weatherDesc'][0]['value'],
                'temp': data['current_condition'][0]['temp_C']
            }
    except Exception as e:
        print("Weather error:", e)
        # 提供預設天氣資訊
        weather = {
            'city': '台北',
            'weather': '資料載入中',
            'temp': '--'
        }
    
    # 取得新聞資訊
    try:
        feed = feedparser.parse("https://news.google.com/rss?hl=zh-TW&gl=TW&ceid=TW:zh-Hant")
        for entry in feed.entries[:10]:  # 取得更多新聞
            # 處理發布時間
            published_time = "無日期"
            if hasattr(entry, 'published'):
                try:
                    # 嘗試解析時間
                    published_time = entry.published[:10]  # 取前10個字符作為日期
                except:
                    published_time = "無日期"
            
            articles.append({
                'title': entry.title,
                'url': entry.link,  # 改名為 url 以符合模板期望
                'description': entry.get('summary', '無摘要')[:200] + '...' if entry.get('summary') else '無摘要',
                'source': {
                    'name': entry.get('source', {}).get('href', '未知來源') if hasattr(entry, 'source') else 'Google 新聞'
                },
                'publishedAt': published_time
            })
    except Exception as e:
        print("News error:", e)
        # 提供預設新聞
        articles = [{
            'title': '無法載入新聞',
            'url': '#',
            'description': '目前無法取得最新新聞，請稍後再試',
            'source': {'name': '系統訊息'},
            'publishedAt': datetime.now().strftime('%Y-%m-%d')
        }]
    
    return render_template('info.html', weather=weather, articles=articles)

@info.route('/weather')
@login_required
def weather_page():
    """單獨的天氣頁面"""
    weather_info = "載入中..."
    
    try:
        res = requests.get('https://wttr.in/Taipei?format=j1', timeout=10)
        if res.status_code == 200:
            data = res.json()
            city = data['nearest_area'][0]['areaName'][0]['value']
            weather_desc = data['current_condition'][0]['weatherDesc'][0]['value']
            temp = data['current_condition'][0]['temp_C']
            weather_info = f"{city}: {temp}°C, {weather_desc}"
        else:
            weather_info = "無法取得天氣資訊"
    except Exception as e:
        print("Weather error:", e)
        weather_info = "天氣服務暫時無法使用"
    
    return render_template('weather.html', weather=weather_info)

@info.route('/news')
@login_required  
def news_page():
    """單獨的新聞頁面"""
    articles = []
    
    try:
        feed = feedparser.parse("https://news.google.com/rss?hl=zh-TW&gl=TW&ceid=TW:zh-Hant")
        for entry in feed.entries[:15]:  # 新聞頁面顯示更多
            published_time = "無日期"
            if hasattr(entry, 'published'):
                try:
                    published_time = entry.published[:10]
                except:
                    published_time = "無日期"
            
            articles.append({
                'title': entry.title,
                'url': entry.link,
                'description': entry.get('summary', '無摘要')[:300] + '...' if entry.get('summary') else '無摘要',
                'source': {
                    'name': 'Google 新聞'
                },
                'publishedAt': published_time
            })
    except Exception as e:
        print("News error:", e)
        articles = [{
            'title': '無法載入新聞',
            'url': '#', 
            'description': '目前無法取得最新新聞，請稍後再試',
            'source': {'name': '系統訊息'},
            'publishedAt': datetime.now().strftime('%Y-%m-%d')
        }]
    
    return render_template('news.html', articles=articles)