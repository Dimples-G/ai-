import requests
from datetime import datetime
import urllib.parse

# ====== 飞书 Webhook 地址 ======
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/1f546a5f-22c4-474e-818a-e008d54c6906"


# ====== 代理请求（解决海外IP被屏蔽问题）======
def fetch(url, name=""):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    # 方法1：直接请求
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except:
        pass
    # 方法2：通过代理请求
    try:
        proxy_url = f"https://api.allorigins.win/raw?url={urllib.parse.quote(url, safe='')}"
        resp = requests.get(proxy_url, headers=headers, timeout=15)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"[{name}] 代理也失败: {e}")
    return None


# ====== 微博热搜 ======
def get_weibo():
    data = fetch("https://weibo.com/ajax/side/hotSearch", "微博热搜")
    if not data:
        return []
    items = data.get("data", {}).get("realtime", [])
    results = []
    for item in items[:10]:
        label = item.get("label_name", "")
        results.append({
            "title": item.get("word", ""),
            "heat": item.get("num", 0),
            "label": label,
            "url": f"https://s.weibo.com/weibo?q=%23{item.get('word', '')}%23",
            "source": "微博热搜"
        })
    return [r for r in results if r["title"]]


# ====== 百度热搜 ======
def get_baidu():
    data = fetch("https://top.baidu.com/board?tab=realtime", "百度热搜")
    if not data:
        return []
    items = data.get("data", {}).get("data", [])
    results = []
    for item in items[:8]:
        results.append({
            "title": item.get("word", ""),
            "url": item.get("url", ""),
            "source": "百度热搜"
        })
    return [r for r in results if r["title"]]


# ====== 知乎热榜 ======
def get_zhihu():
    data = fetch("https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=8", "知乎热榜")
    if not data:
        return []
    items = data.get("data", [])
    results = []
    for item in items[:8]:
        target = item.get("target", {})
        results.append({
            "title": target.get("title", ""),
            "url": f"https://www.zhihu.com/question/{target.get('id', '')}",
            "source": "知乎热榜"
        })
    return [r for r in results if r["title"]]


# ====== 抖音热点 ======
def get_douyin():
    data = fetch("https://www.douyin.com/aweme/v1/web/hot/search/list/", "抖音热点")
    if not data:
        return []
    word_list = data.get("data", {}).get("word_list", [])
    results = []
    for item in word_list[:8]:
        results.append({
            "title": item.get("word", ""),
            "url": f"https://www.douyin.com/search/{item.get('word', '')}",
            "source": "抖音热点"
        })
    return [r for r in results if r["title"]]


# ====== 36氪科技 ======
def get_36kr():
    data = fetch("https://36kr.com/api/search-column/mainsite", "36氪")
    if not data:
        return []
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


# ====== Hacker News AI（海外AI，补充）======
def get_hacker_news():
    try:
        story_ids = requests.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            timeout=10
        ).json()[:30]
    except:
        return []
    ai_keywords = [
        "ai", "gpt", "llm", "claude", "gemini", "openai", "chatgpt",
        "anthropic", "nvidia", "deepseek", "qwen", "mistral", "llama",
        "diffusion", "copilot", "agent", "transformer", "deep learning"
    ]
    results = []
    for sid in story_ids:
        try:
            item = requests.get(
                f"https://hacker-news.firebaseio.com/v0/item/{sid}.json",
                timeout=5
            ).json()
            if item and item.get("title"):
                if any(k in item["title"].lower() for k in ai_keywords):
                    results.append({
                        "title": item["title"],
                        "url": item.get("url", f"https://news.ycombinator.com/item?id={sid}"),
                        "source": "Hacker News"
                    })
        except:
            continue
        if len(results) >= 5:
            break
    return results


# ====== 筛选AI相关新闻 ======
def filter_ai_news(all_news):
    ai_keywords = [
        "ai", "人工智能", "大模型", "gpt", "chatgpt", "claude", "gemini",
        "openai", "anthropic", "deepseek", "通义千问", "文心一言", "kimi",
        "智谱", "百川", "零一万物", "月之暗面", "minimax",
        "机器学习", "深度学习", "神经网络", "transformer", "llm",
        "多模态", "agent", "rag", "aigc", "生成式",
        "自动驾驶", "具身智能", "机器人", "芯片", "算力", "gpu",
        "nvidia", "英伟达", "华为昇腾", "寒武纪", "商汤", "科大讯飞",
        "小米大模型", "字节跳动", "阿里云", "腾讯混元"
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
    today = datetime.now().strftime("%Y-%m-%d")

    # 获取数据
    weibo = get_weibo()
    baidu = get_baidu()
    zhihu = get_zhihu()
    douyin = get_douyin()
    kr = get_36kr()
    hn = get_hacker_news()

    # 合并非微博来源
    all_other = baidu + zhihu + douyin + kr
    ai_news, other_top = filter_ai_news(all_other)

    msg = f"🌅 早安！每日新闻速递 · {today}\n\n"
    has_content = False

    # 微博热搜
    if weibo:
        has_content = True
        msg += "━━━━━━━━━━━━━━━━\n"
        msg += "🔥 微博热搜 TOP10\n\n"
        for i, item in enumerate(weibo, 1):
            tag = f" [{item['label']}]" if item['label'] else ""
            heat_str = f"{item['heat']:,}" if item['heat'] else ""
            msg += f"{i}. {item['title']}{tag}\n"
            if heat_str:
                msg += f"   热度 {heat_str}\n"
            msg += f"   🔗 {item['url']}\n\n"

    # 国内AI热门
    if ai_news:
        has_content = True
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

    # 海外AI（补充）
    if hn:
        has_content = True
        msg += "━━━━━━━━━━━━━━━━\n"
        msg += "🌐 海外AI动态\n\n"
        for i, item in enumerate(hn, 1):
            msg += f"{i}. {item['title']}\n"
            msg += f"   🔗 {item['url']}\n\n"

    # 其他热门
    if other_top:
        has_content = True
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

    # 全部失败提示
    if not has_content:
        msg += "⚠️ 今日新闻源暂时无法获取，请稍后再试。\n"

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
