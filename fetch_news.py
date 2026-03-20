import requests
from datetime import datetime

# ====== 填你的飞书webhook地址 ======
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/1f546a5f-22c4-474e-818a-e008d54c6906"
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
                "url": f"https://s.weibo.com/weibo?q=%23{item.get('word', '')}%23"
            })
        return [r for r in results if r["title"]]
    except:
        return []

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
                "url": f"https://36kr.com/p/{info.get('itemId', '')}"
            })
        return [r for r in results if r["title"]]
    except:
        return []

def get_hacker_news():
    try:
        url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        story_ids = requests.get(url, timeout=10).json()[:30]
        ai_keywords = ["ai", "gpt", "llm", "claude", "gemini", "openai",
                        "chatgpt", "anthropic", "nvidia", "deepseek", "qwen"]
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
                            "url": item.get("url", f"https://news.ycombinator.com/item?id={sid}")
                        })
            except:
                continue
        return ai_stories[:5]
    except:
        return []

def format_news():
    today = datetime.now().strftime("%Y-%m-%d")
    weibo = get_weibo()
    kr = get_36kr()
    hn = get_hacker_news()

    msg = f"🌅 早安！每日新闻速递 · {today}\n\n"

    if weibo:
        msg += "━━━━━━━━━━━━━━━━\n"
        msg += "🔥 微博热搜\n\n"
        for i, item in enumerate(weibo, 1):
            msg += f"{i}. {item['title']}\n"
            msg += f"   🔗 {item['url']}\n\n"

    if kr:
        msg += "━━━━━━━━━━━━━━━━\n"
        msg += "📰 36氪科技\n\n"
        for i, item in enumerate(kr, 1):
            msg += f"{i}. {item['title']}\n"
            msg += f"   🔗 {item['url']}\n\n"

    if hn:
        msg += "━━━━━━━━━━━━━━━━\n"
        msg += "🤖 海外AI动态\n\n"
        for i, item in enumerate(hn, 1):
            msg += f"{i}. {item['title']}\n"
            msg += f"   🔗 {item['url']}\n\n"

    msg += "━━━━━━━━━━━━━━━━\n"
    msg += "💪 新的一天，加油！"
    return msg

def push():
    content = format_news()
    requests.post(FEISHU_WEBHOOK, json={
        "msg_type": "text",
        "content": {"text": content}
    })

if __name__ == "__main__":
    push()
