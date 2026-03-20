import requests
import json
from datetime import datetime

# ====== 飞书 Webhook 地址 ======
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/1f546a5f-22c4-474e-818a-e008d54c6906"

# ====== 36氪热门 ======
def get_36kr():
    try:
        url = "https://36kr.com/api/search-column/mainsite"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        items = data.get("data", {}).get("items", [])
        results = []
        for item in items[:8]:
            info = item.get("templateMaterial", {})
            results.append({
                "title": info.get("widgetTitle", ""),
                "summary": info.get("summary", "")[:80],
                "url": f"https://36kr.com/p/{info.get('itemId', '')}",
                "source": "36氪"
            })
        return [r for r in results if r["title"]]
    except:
        return []

# ====== 华尔街见闻 ======
def get_wallstreetcn():
    try:
        url = "https://api-one-wscn.awtmt.com/apiv1/content/articles?channel=global-channel&limit=10"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        items = data.get("data", {}).get("items", [])
        results = []
        for item in items[:8]:
            results.append({
                "title": item.get("title", ""),
                "summary": item.get("display_time_str", ""),
                "url": f"https://wallstreetcn.com/articles/{item.get('id', '')}",
                "source": "华尔街见闻"
            })
        return [r for r in results if r["title"]]
    except:
        return []

# ====== 微博热搜 ======
def get_weibo():
    try:
        url = "https://weibo.com/ajax/side/hotSearch"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        items = data.get("data", {}).get("realtime", [])
        results = []
        for item in items[:8]:
            results.append({
                "title": item.get("word", ""),
                "summary": f"热度 {item.get('num', '')}",
                "url": f"https://s.weibo.com/weibo?q=%23{item.get('word', '')}%23",
                "source": "微博热搜"
            })
        return [r for r in results if r["title"]]
    except:
        return []

# ====== Hacker News AI 相关 ======
def get_hacker_news():
    try:
        url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        story_ids = requests.get(url, timeout=10).json()[:30]

        ai_keywords = ["ai", "gpt", "llm", "claude", "gemini", "openai",
                        "machine learning", "deep learning", "chatgpt",
                        "anthropic", "nvidia", "deepseek", "qwen", "mistral"]

        ai_stories = []
        for sid in story_ids:
            try:
                item = requests.get(
                    f"https://hacker-news.firebaseio.com/v0/item/{sid}.json",
                    timeout=5
                ).json()
                if item and item.get("title"):
                    if any(k in item["title"].lower() for k in ai_keywords):
                        ai_stories.append({
                            "title": item["title"],
                            "summary": "",
                            "url": item.get("url", f"https://news.ycombinator.com/item?id={sid}"),
                            "source": "Hacker News"
                        })
            except:
                continue
        return ai_stories[:5]
    except:
        return []

# ====== 格式化消息 ======
def format_news():
    today = datetime.now().strftime("%Y-%m-%d")

    kr_news = get_36kr()
    wsj_news = get_wallstreetcn()
    weibo_news = get_weibo()
    hn_news = get_hacker_news()

    msg = f"🌅 早安！每日新闻速递 · {today}\n\n"

    if weibo_news:
        msg += "━━━━━━━━━━━━━━━━\n"
        msg += "🔥 微博热搜\n\n"
        for i, item in enumerate(weibo_news, 1):
            msg += f"{i}. {item['title']}\n"
            msg += f"   {item['summary']}\n"
            msg += f"   🔗 {item['url']}\n\n"

    if kr_news:
        msg += "━━━━━━━━━━━━━━━━\n"
        msg += "📰 36氪科技\n\n"
        for i, item in enumerate(kr_news, 1):
            msg += f"{i}. {item['title']}\n"
            if item['summary']:
                msg += f"   {item['summary']}\n"
            msg += f"   🔗 {item['url']}\n\n"

    if wsj_news:
        msg += "━━━━━━━━━━━━━━━━\n"
        msg += "💰 华尔街见闻\n\n"
        for i, item in enumerate(wsj_news, 1):
            msg += f"{i}. {item['title']}\n"
            msg += f"   🔗 {item['url']}\n\n"

    if hn_news:
        msg += "━━━━━━━━━━━━━━━━\n"
        msg += "🤖 海外 AI 动态\n\n"
        for i, item in enumerate(hn_news, 1):
            msg += f"{i}. {item['title']}\n"
            msg += f"   🔗 {item['url']}\n\n"

    msg += "━━━━━━━━━━━━━━━━\n"
    msg += "💪 新的一天，加油！"

    return msg

# ====== 推送到飞书 ======
def push_to_feishu():
    content = format_news()
    resp = requests.post(FEISHU_WEBHOOK, json={
        "msg_type": "text",
        "content": {"text": content}
    })
    print(f"推送状态: {resp.status_code}")
    print(resp.json())

if __name__ == "__main__":
    push_to_feishu()
