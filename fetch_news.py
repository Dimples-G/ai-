import requests
import json
from datetime import datetime

# ====== 配置 ======
FEISHU_WEBHOOK = "把你的webhook地址粘贴到这里"

# ====== 免费新闻源：Hacker News（科技/AI为主）======
def get_hacker_news():
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    resp = requests.get(url, timeout=10)
    story_ids = resp.json()[:30]

    stories = []
    for sid in story_ids:
        try:
            item = requests.get(
                f"https://hacker-news.firebaseio.com/v0/item/{sid}.json",
                timeout=5
            ).json()
            if item and item.get("title"):
                stories.append({
                    "title": item["title"],
                    "url": item.get("url", f"https://news.ycombinator.com/item?id={sid}"),
                    "score": item.get("score", 0)
                })
        except:
            continue

    # 筛选AI相关
    ai_keywords = ["ai", "gpt", "llm", "claude", "gemini", "openai", "machine learning",
                    "deep learning", "neural", "transformer", "agent", "model", "chatgpt",
                    "anthropic", "nvidia", "deepseek", "qwen", "mistral"]

    ai_stories = [s for s in stories if any(k in s["title"].lower() for k in ai_keywords)]
    other_top = [s for s in stories if s not in ai_stories]

    return ai_stories[:6] + other_top[:4]

# ====== 免费新闻源：Reddit AI板块 ======
def get_reddit_ai():
    headers = {"User-Agent": "AI-Daily-Bot/1.0"}
    subreddits = ["artificial", "MachineLearning", "LocalLLaMA"]

    posts = []
    for sub in subreddits:
        try:
            url = f"https://www.reddit.com/r/{sub}/hot.json?limit=5"
            resp = requests.get(url, headers=headers, timeout=10).json()
            for post in resp["data"]["children"]:
                p = post["data"]
                posts.append({
                    "title": p["title"],
                    "url": f"https://reddit.com{p['permalink']}",
                    "score": p.get("score", 0),
                    "sub": sub
                })
        except:
            continue

    posts.sort(key=lambda x: x["score"], reverse=True)
    return posts[:5]

# ====== 格式化消息 ======
def format_news():
    today = datetime.now().strftime("%Y-%m-%d")

    hn_news = get_hacker_news()
    reddit_news = get_reddit_ai()

    msg = f"🌅 AI早报 · {today}\n\n"
    msg += "━━━━━━━━━━━━━━━━\n"
    msg += "🔥 Hacker News 热门\n\n"

    for i, item in enumerate(hn_news, 1):
        msg += f"{i}. {item['title']}\n"
        msg += f"   🔗 {item['url']}\n\n"

    if reddit_news:
        msg += "━━━━━━━━━━━━━━━━\n"
        msg += "💬 Reddit AI 社区\n\n"

        for i, item in enumerate(reddit_news, 1):
            msg += f"{i}. [{item['sub']}] {item['title']}\n"
            msg += f"   🔗 {item['url']}\n\n"

    msg += "━━━━━━━━━━━━━━━━\n"
    msg += "💪 新的一天，继续探索 AI 的无限可能！"

    return msg

# ====== 推送到飞书 ======
def push_to_feishu():
    content = format_news()

    resp = requests.post(FEISHU_WEBHOOK, json={
        "msg_type": "text",
        "content": {"text": content}
    })

    print(f"推送结果: {resp.status_code}")
    print(resp.json())

if __name__ == "__main__":
    push_to_feishu()
