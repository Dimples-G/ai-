import requests
from datetime import datetime

# ====== 飞书 Webhook 地址 ======FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/1f546a5f-22c4-474e-818a-e008d54c6906"

# ====== 微博热搜（直接GET，无需cookie）======
def get_weibo():
    try:
        url = "https://weibo.com/ajax/side/hotSearch"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        items = data.get("data", {}).get("realtime", [])
        results = []
        for item in items[:10]:
            label = item.get("label_name", "")
            results.append({
                "title": item.get("word", ""),
                "heat": f"热度 {item.get('num', '')}",
                "label": label,
                "url": f"https://s.weibo.com/weibo?q=%23{item.get('word', '')}%23"
            })
        return [r for r in results if r["title"]]
    except Exception as e:
        print(f"微博热搜获取失败: {e}")
        return []


# ====== 热门聚合API（百度、知乎、抖音、B站等）======
def get_hot_from_api(platform, name):
    try:
        url = f"https://api-hot.imsyy.top/{platform}"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        items = data.get("data", [])
        results = []
        for item in items[:5]:
            results.append({
                "title": item.get("title", item.get("name", "")),
                "url": item.get("url", item.get("link", "")),
                "source": name
            })
        return [r for r in results if r["title"]]
    except Exception as e:
        print(f"{name}获取失败: {e}")
        return []


# ====== 百度热搜 ======
def get_baidu():
    return get_hot_from_api("baidu", "百度热搜")


# ====== 知乎热榜 ======
def get_zhihu():
    return get_hot_from_api("zhihu", "知乎热榜")


# ====== 抖音热点 ======
def get_douyin():
    return get_hot_from_api("douyin", "抖音热点")


# ====== B站热门 ======
def get_bilibili():
    return get_hot_from_api("bilibili", "B站热门")


# ====== IT之家热榜 ======
def get_ithome():
    return get_hot_from_api("ithome", "IT之家")


# ====== 少数派热榜 ======
def get_sspai():
    return get_hot_from_api("sspai", "少数派")


# ====== 36氪科技 ======
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
                "summary": info.get("summary", "")[:60],
                "url": f"https://36kr.com/p/{info.get('itemId', '')}",
                "source": "36氪"
            })
        return [r for r in results if r["title"]]
    except Exception as e:
        print(f"36氪获取失败: {e}")
        return []


# ====== 从所有来源中筛选AI相关新闻 ======
def filter_ai_news(all_news):
    ai_keywords = [
        "ai", "人工智能", "大模型", "gpt", "chatgpt", "claude", "gemini",
        "openai", "anthropic", "deepseek", "通义千问", "文心一言", "kimi",
        "智谱", "百川", "零一万物", "月之暗面", "minimax",
        "机器学习", "深度学习", "神经网络", "transformer", "llm",
        "多模态", "agent", "rag", "aigc", "生成式",
        "自动驾驶", "具身智能", "机器人", "芯片", "算力", "gpu", "nvidia", "英伟达",
        "华为昇腾", "寒武纪", "商汤", "科大讯飞", "百度",
        "小米大模型", "小米ai", "字节跳动", "阿里云", "腾讯混元"
    ]
    ai_news = []
    other_news = []
    for item in all_news:
        title_lower = item["title"].lower()
        if any(k in title_lower for k in ai_keywords):
            ai_news.append(item)
        else:
            other_news.append(item)
    return ai_news, other_news


# ====== 格式化消息 ======
def format_news():
    today = datetime.now().strftime("%Y-%m-%d %A")

    # 获取各来源数据
    weibo = get_weibo()
    baidu = get_baidu()
    zhihu = get_zhihu()
    douyin = get_douyin()
    bilibili = get_bilibili()
    ithome = get_ithome()
    sspai = get_sspai()
    kr = get_36kr()

    # 合并所有来源，用于筛选AI新闻
    all_news = baidu + zhihu + douyin + bilibili + ithome + sspai + kr
    ai_news, other_top = filter_ai_news(all_news)

    msg = f"🌅 早安！每日新闻速递 · {today}\n\n"

    # 微博热搜
    if weibo:
        msg += "━━━━━━━━━━━━━━━━\n"
        msg += "🔥 微博热搜\n\n"
        for i, item in enumerate(weibo, 1):
            tag = f" [{item['label']}]" if item['label'] else ""
            msg += f"{i}. {item['title']}{tag}\n"
            msg += f"   {item['heat']}\n"
            msg += f"   🔗 {item['url']}\n\n"

    # 国内AI热门
    if ai_news:
        msg += "━━━━━━━━━━━━━━━━\n"
        msg += "🤖 国内AI热门\n\n"
        seen = set()
        count = 0
        for item in ai_news:
            if item["title"] not in seen and count < 8:
                seen.add(item["title"])
                count += 1
                msg += f"{count}. {item['title']}\n"
                if item.get("summary"):
                    msg += f"   {item['summary']}\n"
                if item.get("url"):
                    msg += f"   🔗 {item['url']}\n"
                msg += f"   来源：{item.get('source', '')}\n\n"

    # 其他热门
    if other_top:
        msg += "━━━━━━━━━━━━━━━━\n"
        msg += "📰 其他热门\n\n"
        seen = set()
        count = 0
        for item in other_top:
            if item["title"] not in seen and count < 5:
                seen.add(item["title"])
                count += 1
                msg += f"{count}. [{item.get('source', '')}] {item['title']}\n"
                if item.get("url"):
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
