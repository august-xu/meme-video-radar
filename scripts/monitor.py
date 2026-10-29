#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
monitor.py — 全网模因与 AI 视频落地页 6小时增量监控与跨域碰撞主调度器

功能定位：
  - 专门监控 8~9 个核心模因与视频落地页矩阵
  - 多源 Sitemap 并发差分抓取 + Media.io 隐藏动态 Zone 模板极速嗅探
  - 纯文本 JSON 状态持久化 (data/meme_video_state.json)
  - 模因实体挖掘与跨时间差跨域碰撞计算 (term_engine.py)
  - 多模型通用 LLM 提炼总结 (summarizer.py)
  - 飞书高价值新增卡片通知 (notifier.py)
  - 研报产物独立落盘于 meme-video/<YYYY-MM-DD>/<HHMM>-monitor.md
"""

from __future__ import annotations

import argparse
import concurrent.futures
import gzip
import html
import json
import os
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

# 统一时区规范：北京时间 (UTC+8)
BEIJING_TZ = timezone(timedelta(hours=8))
from urllib.parse import urlparse

# 本模块依赖导入
# 仓库根目录与默认文件路径
CUR_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(CUR_DIR)
sys.path.insert(0, CUR_DIR)

import term_engine
import capcut_crawler
import capcut_analyzer

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
LANG_CODE_REGEX = re.compile(r"/(zh|ja|jp|es|de|fr|pt|ru|ko|ar|it|tw|cn|en)(/|$)", re.IGNORECASE)

SOURCES_FILE = os.path.join(CUR_DIR, "sources.json")
STATE_FILE = os.path.join(REPO_DIR, "data", "state.json")
REPORTS_DIR = os.path.join(REPO_DIR, "reports")


def fetch_bytes(url: str, timeout: int = 15, retries: int = 2) -> bytes | None:
    """HTTP GET 请求并返回 bytes，支持自动 gzip 解压缩"""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
        }
    )
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read()
                if resp.headers.get("Content-Encoding") == "gzip" or url.endswith(".gz") or data[:2] == b"\x1f\x8b":
                    try:
                        data = gzip.decompress(data)
                    except Exception:
                        pass
                return data
        except Exception as e:
            if attempt == retries:
                sys.stderr.write(f"[WARN] 获取失败 ({url}): {e}\n")
                return None
            time.sleep(1.0)
    return None


def strip_xml_namespace(tag: str) -> str:
    return tag.split("}", 1)[1] if "}" in tag else tag


def parse_sitemap_recursive(url: str, depth: int = 0, max_depth: int = 2) -> List[dict]:
    """递归解析 sitemap / sitemapindex，对 KYM 仅提取核心模因子树"""
    if depth > max_depth:
        return []

    data = fetch_bytes(url)
    if not data:
        return []

    try:
        root = ET.fromstring(data)
    except Exception as e:
        sys.stderr.write(f"[ERROR] XML 解析失败 ({url}): {e}\n")
        return []

    root_tag = strip_xml_namespace(root.tag).lower()
    results = []

    if root_tag == "sitemapindex":
        child_urls = []
        for sitemap_node in root:
            if strip_xml_namespace(sitemap_node.tag).lower() == "sitemap":
                for child in sitemap_node:
                    if strip_xml_namespace(child.tag).lower() == "loc" and child.text:
                        c_url = child.text.strip()
                        # KYM 特殊优化：只深入抓取 memes 相关的子 sitemap，忽略海量纯图片/视频/用户子树
                        if "knowyourmeme.com" in url:
                            if "memes" not in c_url and "trends" not in c_url:
                                continue
                        child_urls.append(c_url)

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {
                executor.submit(parse_sitemap_recursive, c, depth + 1, max_depth): c
                for c in child_urls
            }
            for future in concurrent.futures.as_completed(future_to_url):
                sub_res = future.result()
                if sub_res:
                    results.extend(sub_res)

    elif root_tag == "urlset":
        for url_node in root:
            if strip_xml_namespace(url_node.tag).lower() == "url":
                loc = None
                lastmod = None
                for child in url_node:
                    tag = strip_xml_namespace(child.tag).lower()
                    if tag == "loc" and child.text:
                        loc = child.text.strip()
                    elif tag == "lastmod" and child.text:
                        lastmod = child.text.strip()
                if loc:
                    # KYM 过滤：只保留 /memes/ 核心百科页面
                    if "knowyourmeme.com" in loc and "/memes/" not in loc:
                        continue
                    results.append({"url": loc, "lastmod": lastmod or ""})

    return results


def normalize_url(url: str, dedup_multilang: bool = False) -> str:
    """多语言与尾斜杠归一化"""
    if not dedup_multilang:
        return url.rstrip("/")
    m = LANG_CODE_REGEX.search(url)
    if m:
        canonical = url[:m.start()] + "/" + url[m.end():]
    else:
        canonical = url
    if "://" in canonical:
        proto, rest = canonical.split("://", 1)
        canonical = proto + "://" + re.sub(r"/+", "/", rest)
    return canonical.rstrip("/")


def crawl_mediaio_dynamic_zones() -> List[dict]:
    """通过 2-hop 快速 BFS 嗅探万兴 Media.io 的 /explore/zone/* 动态模板"""
    seed_urls = [
        "https://www.media.io/ai/explore/zone/unforgettable-ai-car-video-generator",
        "https://www.media.io/ai/explore/zone/hotel-lobby-ai-video-trend",
        "https://www.media.io/ai/explore/zone/bulin-47-rap-ai-trend",
        "https://www.media.io/ai/explore/zone/alors-on-danse-ai-video-generator",
        "https://www.media.io/ai/explore/zone/ai-dance-generator"
    ]
    base_prefix = "https://www.media.io/ai/explore/zone/"
    locale_regex = re.compile(r"https://www\.media\.io/ai/[a-z]{2}(?:-[A-Za-z]{2,4})?/explore/zone/([a-z0-9-]+)")

    headers = {"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"}

    def probe_page(u: str) -> set:
        try:
            req = urllib.request.Request(u, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as res:
                html_text = res.read().decode("utf-8", "ignore")
            found = set(re.findall(r"href=[\"\x27](https://www\.media\.io/ai/explore/zone/[a-z0-9-]+)[\"\x27]", html_text))
            for slug in re.findall(locale_regex, html_text):
                found.add(f"{base_prefix}{slug}")
            return found
        except Exception:
            return set()

    discovered = set()
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futs = [executor.submit(probe_page, u) for u in seed_urls]
        for f in concurrent.futures.as_completed(futs):
            discovered.update(f.result())

    hop2 = list(discovered - set(seed_urls))[:6]
    if hop2:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futs = [executor.submit(probe_page, u) for u in hop2]
            for f in concurrent.futures.as_completed(futs):
                discovered.update(f.result())

    now_iso = datetime.now(timezone.utc).isoformat()
    results = []
    for u in discovered:
        slug = u.replace(base_prefix, "").strip()
        results.append({
            "url": u,
            "lastmod": now_iso[:10],
            "is_dynamic_zone": True,
            "title": f"Media.io AI Effect Zone: {slug.replace('-', ' ').title()}"
        })
    return results


def fetch_page_metadata(url: str) -> dict:
    """抓取页面 Title 与 Description，若超时则从 slug 推导"""
    slug = term_engine.extract_slug_text(url).title()
    meta = {"title": slug, "description": "", "url": url}
    data = fetch_bytes(url, timeout=8)
    if not data:
        return meta

    html_text = data.decode("utf-8", errors="ignore")
    # Title
    m_title = re.search(r"<title>(.*?)</title>", html_text, re.DOTALL | re.IGNORECASE)
    if m_title:
        title = html.unescape(m_title.group(1)).strip()
        meta["title"] = re.sub(r"\s+", " ", title)

    # Meta Description
    m_desc = re.search(
        r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']',
        html_text, re.DOTALL | re.IGNORECASE
    )
    if not m_desc:
        m_desc = re.search(
            r'<meta\s+property=["\']og:description["\']\s+content=["\'](.*?)["\']',
            html_text, re.DOTALL | re.IGNORECASE
        )
    if m_desc:
        desc = html.unescape(m_desc.group(1)).strip()
        meta["description"] = re.sub(r"\s+", " ", desc)[:250]

    # Published / Generated Time (网页真实生成或发布时间)
    # [性能红线] 旧写法 `<meta[^>]+content=["'](.*?)["'][^>]+...` 在大型 HTML 上会灾难性回溯，
    # 单个页面可拖死线程数分钟。改为：先限定标签内部不含 '>'（[^>]），且用单遍扫描代替多组回溯。
    pub_meta_names = (
        "article:published_time", "og:published_time", "publishdate",
        "datePublished", "datepublished", "date", "pubdate", "article:modified_time"
    )
    # 1) 优先：逐个 <meta ...> 标签解析属性（线性、无回溯风险）
    for tag in re.findall(r"<meta\b[^>]{0,800}>", html_text, re.IGNORECASE):
        low = tag.lower()
        if not any(n.lower() in low for n in pub_meta_names):
            continue
        m_c = re.search(r'content\s*=\s*["\']([^"\']{4,64})["\']', tag, re.IGNORECASE)
        if m_c:
            val = html.unescape(m_c.group(1)).strip()
            if len(val) >= 10:
                meta["published_at"] = val
                break

    # 2) 兜底：JSON-LD / <time datetime>（限定长度，避免回溯）
    if "published_at" not in meta:
        for pat in (
            r'"datePublished"\s*:\s*"([^"]{10,40})"',
            r'"dateCreated"\s*:\s*"([^"]{10,40})"',
            r'<time\b[^>]{0,300}datetime=["\']([^"\']{10,40})["\']',
        ):
            m_pub = re.search(pat, html_text, re.IGNORECASE)
            if m_pub:
                val = html.unescape(m_pub.group(1)).strip()
                if len(val) >= 10:
                    meta["published_at"] = val
                    break

    return meta


class StateManager:
    """纯文本 JSON 状态管理：存储已见 URL 集合与历史实体知识库"""
    def __init__(self, path: str):
        self.path = path
        self.data = self._load()

    def _load(self) -> dict:
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                sys.stderr.write(f"[WARN] 加载状态文件异常: {e}\n")
        return {
            "last_run_timestamp": "",
            "total_urls_seen": 0,
            "seen_urls": {},    # domain -> list of urls
            "entities": {}      # term -> {first_seen, domains: {domain: [url_entries]}}
        }

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        # 统计总数
        total = sum(len(v) for v in self.data.get("seen_urls", {}).values())
        self.data["total_urls_seen"] = total
        self.data["last_run_timestamp"] = datetime.now(timezone.utc).isoformat()
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def is_seen(self, domain: str, canonical_url: str) -> bool:
        domain_seen = self.data.setdefault("seen_urls", {}).setdefault(domain, [])
        return canonical_url in domain_seen

    def mark_seen(self, domain: str, canonical_url: str):
        self.data.setdefault("seen_urls", {}).setdefault(domain, []).append(canonical_url)

    def update_entity(self, term: str, domain: str, url: str, title: str):
        entities = self.data.setdefault("entities", {})
        now_iso = datetime.now(timezone.utc).isoformat()
        if term not in entities:
            entities[term] = {
                "first_seen": now_iso,
                "domains": {}
            }
        dom_map = entities[term].setdefault("domains", {})
        if domain not in dom_map:
            dom_map[domain] = []

        # 检查是否已有该 URL
        existing_urls = {item["url"] for item in dom_map[domain]}
        if url not in existing_urls:
            dom_map[domain].append({
                "url": url,
                "title": title,
                "first_seen": now_iso
            })


def update_readme_index(report_date: str, slot: str, file_rel_path: str, new_count: int, collision_count: int):
    """更新 meme-video/README.md 专刊总目录索引"""
    index_path = os.path.join(REPO_DIR, "README.md")
    os.makedirs(REPORTS_DIR, exist_ok=True)

    header = """# ⚡ 全网模因与 AI 视频落地页 6小时增量监控专刊

> 7×24小时高频捕捉全网突发模因热梗、TikTok/Reels 爆款 AI 视频动效落地页与跨域竞争碰撞。

---

## 📅 历史研报归档索引

| 监控日期 | 时段 (UTC/槽位) | 新增页面 | 跨域碰撞数 | 报告直达 |
| :--- | :--- | :--- | :--- | :--- |
"""
    existing_content = ""
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            existing_content = f.read()

    new_line = f"| **{report_date}** | `{slot}` | **{new_count}** 条 | **{collision_count}** 组 | [📖 阅读全文]({file_rel_path}) |\n"

    if "| 监控日期 |" in existing_content:
        # 在表格的第一条数据前插入新记录
        parts = existing_content.split("| :--- |\n", 1)
        if len(parts) == 2:
            new_content = parts[0] + "| :--- |\n" + new_line + parts[1]
        else:
            new_content = existing_content + new_line
    else:
        new_content = header + new_line

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(new_content)


def main():
    parser = argparse.ArgumentParser(description="Meme & AI Video 6h Monitor & Collision Radar")
    parser.add_argument("--sources", default=SOURCES_FILE, help="监控源配置文件路径")
    parser.add_argument("--state", default=STATE_FILE, help="状态文件路径")
    parser.add_argument("--dry-run", action="store_true", help="演练模式，不写文件与不发通知")
    parser.add_argument("--force-report", action="store_true", help="即使零新增也强制输出测试研报")
    parser.add_argument("--init-baseline", action="store_true", help="强制将当前全部抓取存量沉淀为基线底库，不触发报警")
    args = parser.parse_args()

    print("=================================================================")
    print("🚀 启动【全网模因与 AI 视频落地页 6小时增量监控与跨域碰撞引擎】")
    print(f"⏰ 当前运行时间: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=================================================================")

    if not os.path.exists(args.sources):
        sys.stderr.write(f"[ERROR] 配置文件未找到: {args.sources}\n")
        sys.exit(1)

    with open(args.sources, "r", encoding="utf-8") as f:
        sources_cfg = json.load(f)

    state_mgr = StateManager(args.state)
    last_run = state_mgr.data.get("last_run_timestamp") or "首次运行"
    print(f"📦 增量基线水位线: {last_run} | 历史已见 URL 存量: {state_mgr.data.get('total_urls_seen', 0)}")

    newly_crawled_entries = []  # 记录本次所有新增页面条目
    source_stats = []

    # 1. 并发抓取各站点 Sitemap
    print(f"⏳ 正在并发扫描 {len(sources_cfg)} 个模因与视频重点站点的 Sitemap...")
    for src in sources_cfg:
        src_id = src["id"]
        src_name = src["name"]
        src_url = src["url"]
        domain = urlparse(src_url).netloc
        dedup_multi = src.get("dedup_multilang", False)
        if src_id == "capcut":
            continue

        raw_urls = parse_sitemap_recursive(src_url)
        # 若是 Media.io 且开启动态 zone，合并动态嗅探结果
        if src.get("has_dynamic_zone"):
            print("  ⚡ 正在并发嗅探 Media.io 动态 Zone 模板...")
            zone_items = crawl_mediaio_dynamic_zones()
            raw_urls.extend(zone_items)

        # 差分对比
        new_in_src = []
        for item in raw_urls:
            raw_u = item["url"]
            canonical_u = normalize_url(raw_u, dedup_multilang=dedup_multi)
            if not state_mgr.is_seen(domain, canonical_u):
                # 记录新增
                item_copy = dict(item)
                item_copy["domain"] = domain
                item_copy["source_id"] = src_id
                item_copy["source_name"] = src_name
                item_copy["canonical_url"] = canonical_u
                new_in_src.append(item_copy)
                item_copy["first_seen"] = datetime.now(timezone.utc).astimezone(BEIJING_TZ).strftime("%Y-%m-%d %H:%M")

        # 首次接入检测：若该域无任何历史记录，打上基线标记，存量不作为“突发新增”扰民
        is_first_seen_domain = (domain not in state_mgr.data.get("seen_urls", {}))
        if is_first_seen_domain or getattr(args, "init_baseline", False):
            print(f"  🌱 [{src_name}] 首次接入/初始化基线：将 {len(raw_urls)} 条存量 URL 沉淀为基线底库")
            if not args.dry_run:
                for item in raw_urls:
                    canonical_u = normalize_url(item["url"], dedup_multilang=dedup_multi)
                    state_mgr.mark_seen(domain, canonical_u)
            source_stats.append({
                "name": src_name,
                "total": len(raw_urls),
                "new": 0,
                "note": "首次接入基线初始化"
            })
        else:
            print(f"  ✅ [{src_name}] 全量监控 {len(raw_urls)} 条 | 本次新增 {len(new_in_src)} 条")
            source_stats.append({
                "name": src_name,
                "total": len(raw_urls),
                "new": len(new_in_src)
            })
            max_fetch = src.get("max_detail_fetch", 15)
            newly_crawled_entries.extend(new_in_src[:max_fetch])
    # 1.5 专线抓取 CapCut (剪映海外版) Most Used 全球爆款模板流
    print("  ⚡ 正在并发抓取 CapCut (剪映海外版) Most Used 全球爆款模板...")
    capcut_items = capcut_crawler.crawl_capcut_most_used()
    capcut_domain = "www.capcut.com"
    capcut_new = []
    is_first_capcut = (capcut_domain not in state_mgr.data.get("seen_urls", {}))

    for item in capcut_items:
        can_u = item["canonical_url"]
        if is_first_capcut or getattr(args, "init_baseline", False):
            if not args.dry_run:
                state_mgr.mark_seen(capcut_domain, can_u)
        else:
            if not state_mgr.is_seen(capcut_domain, can_u):
                capcut_new.append(item)

    # 1.6 时序快照与热度生命周期分析（新上榜/爆火/升温/降温/跌出榜）
    print("  ⏳ 正在计算 CapCut 时序差分与热度生命周期...")
    capcut_trend = capcut_analyzer.analyze(capcut_items)
    n_new = len(capcut_trend["new_entries"])
    n_drop = len(capcut_trend["dropped_out"])
    calib = capcut_trend["calibrating"]
    print(f"  📊 [CapCut 热度引擎] 快照 #{capcut_trend['snapshot_count']} | 新上榜 {n_new} | 跌出榜 {n_drop} | {'校准积累期' if calib else '动态阈值已启用'}")

    # 新上榜模板必逃实体提取与跨域碰撞；非新增但状态为爆火/升温的也纳入碰撞信号
    for x in capcut_trend["lifecycle"]:
        if x["status"] in ("new_entry", "surging", "heating"):
            # 找到对应的原始条目并补充实体
            for item in capcut_items:
                if item.get("template_id") == x["template_id"]:
                    item["trend_status"] = x["status_label"]
                    item["delta_6h"] = x["delta_6h"]
                    item["rank_delta"] = x["rank_delta"]
                    ents = term_engine.extract_page_entities(item["url"], item["title"], item.get("title_desc", ""))
                    item["entities"] = list(ents)
                    if not args.dry_run:
                        state_mgr.mark_seen(item["domain"], item["canonical_url"])
                        for ent in ents:
                            state_mgr.update_entity(ent, item["domain"], item["url"], item["title"])
                    break

    # 研报呈现策略：新上榜优先；无新增时呈现热度状态最靠前的 12 条
    capcut_report_items = capcut_new if capcut_new else capcut_items[:12]
    newly_crawled_entries.extend(capcut_report_items)

    print(f"  ✅ [CapCut (剪映海外版)] 实时监控 {len(capcut_items)} 条热门模板 | 本期呈现 {len(capcut_report_items)} 条爆款")
    source_stats.append({
        "name": "CapCut (剪映海外版)",
        "total": len(capcut_items),
        "new": len(capcut_report_items)
    })

    total_new_count = len(newly_crawled_entries)
    print(f"\n📊 扫描完毕：本次 6 小时窗口共捕捉到 {total_new_count} 个新增页面与爆款模板！")

    # 2. 对新增页面并发补充抓取 Metadata 并提取模因实体
    # 注意：as_completed 会无限等待单个卡死连接，必须加全局硬超时。
    if total_new_count > 0:
        print(f"⏳ 正在并发抓取 {total_new_count} 个新增页面的 Title 与 Meta 描述并抽取实体...")
        html_entries = [e for e in newly_crawled_entries if e.get("source_id") != "capcut"]
        capcut_entries = [e for e in newly_crawled_entries if e.get("source_id") == "capcut"]

        # 直接处理自带完整元数据的 CapCut 模板 (零网络请求，秒级完成)
        for entry in capcut_entries:
            entities = term_engine.extract_page_entities(entry["url"], entry["title"], entry.get("title_desc", ""))
            entry["entities"] = list(entities)
            if not args.dry_run:
                state_mgr.mark_seen(entry["domain"], entry["canonical_url"])
                for ent in entities:
                    state_mgr.update_entity(ent, entry["domain"], entry["url"], entry["title"])

        executor = concurrent.futures.ThreadPoolExecutor(max_workers=8)
        future_to_entry = {
            executor.submit(fetch_page_metadata, e["url"]): e
            for e in html_entries
        }
        done_count = 0
        try:
            # 整体超时：36 个页面 8 线程，单页 8s，给 180s 余量
            hard_deadline = time.time() + max(120, min(300, total_new_count * 8))
            pending = set(future_to_entry.keys())
            while pending:
                remain = hard_deadline - time.time()
                if remain <= 0:
                    print(f"⚠️ Metadata 抓取超时，{len(pending)} 个页面使用回退标题")
                    break
                done, pending = concurrent.futures.wait(
                    pending, timeout=min(remain, 10),
                    return_when=concurrent.futures.FIRST_COMPLETED
                )
                for fut in done:
                    entry = future_to_entry[fut]
                    try:
                        meta = fut.result(timeout=1)
                    except Exception as ex:
                        print(f"[WARN] metadata 抓取失败 {entry.get('url','')[:60]}: {ex}")
                        meta = {"title": entry.get("title", ""), "description": ""}
                    entry["title"] = meta.get("title") or entry.get("title") or ""
                    entry["description"] = meta.get("description", "")
                    entry["page_created_at"] = meta.get("published_at") or entry.get("lastmod") or ""

                    entities = term_engine.extract_page_entities(
                        entry["url"], entry["title"], entry["description"]
                    )
                    entry["entities"] = list(entities)

                    if not args.dry_run:
                        state_mgr.mark_seen(entry["domain"], entry["canonical_url"])
                        for ent in entities:
                            state_mgr.update_entity(ent, entry["domain"], entry["url"], entry["title"])
                    done_count += 1
            # 超时未完成的条目也要保留（用 slug 推导标题），避免数据丢失
            for fut in pending:
                entry = future_to_entry[fut]
                if not entry.get("title"):
                    entry["title"] = term_engine.extract_slug_text(entry["url"]).title()
                entry["description"] = entry.get("description", "")
                entry["page_created_at"] = entry.get("lastmod") or ""
                entry["entities"] = list(term_engine.extract_page_entities(entry["url"], entry["title"], ""))
        finally:
            # cancel_futures 仅 Python 3.9+，3.8 会 TypeError，需容错
            try:
                executor.shutdown(wait=False, cancel_futures=True)
            except TypeError:
                executor.shutdown(wait=False)
        print(f"✅ Metadata 抓取完成：{done_count}/{total_new_count} 成功")
        _ = (lambda: None)

    # 3. 执行跨时差、跨域实体碰撞计算
    print("⏳ 正在结合历史实体底库执行【跨域实体碰撞计算】...")
    collisions = term_engine.detect_collisions(
        state_mgr.data.get("entities", {}),
        min_domains=2,
        since_iso=last_run if last_run != "首次运行" else ""
    )
    print(f"💥 跨域碰撞分析完成：共检测到 {len(collisions)} 组【本期窗口内新激活】的跨域碰撞！")

    # 4. 零新增且无碰撞判定 (防刷屏与无意义落盘)
    if total_new_count == 0 and len(collisions) == 0:
        if not args.force_report:
            print("⚪ 本次窗口未检测到任何新增页面与新碰撞，更新水位线并向飞书推送巡航打卡...")
            if not args.dry_run:
                state_mgr.save()
                import notifier
                now_utc = datetime.now(timezone.utc)
                now_beijing = now_utc.astimezone(BEIJING_TZ)
                notifier.send_feishu_heartbeat(
                    date_str=now_beijing.strftime("%Y-%m-%d"),
                    slot_str=now_beijing.strftime("%H%M"),
                    sources_count=len(sources_cfg),
                    tracked_urls=state_mgr.data.get("total_urls_seen", 0)
                )
            return
        else:
            print("🧪 检测到 --force-report 演练模式：零新增时注入高价值实测样本，测试全流程与模型连通性...")
            # 注入高质量演练样本
            newly_crawled_entries = [
                {
                    "source_name": "Know Your Meme",
                    "domain": "knowyourmeme.com",
                    "url": "https://knowyourmeme.com/memes/banana-tree-run",
                    "title": "Banana Tree Run (Viral Parkour Meme)",
                    "description": "Banana Tree Run refers to a series of surreal viral videos of people running effortlessly across the tops of banana trees, popular on TikTok.",
                    "entities": ["banana tree run", "parkour dance"]
,
                    "page_created_at": "2026-10-21 13:00"
,
                    "first_seen": datetime.now(timezone.utc).astimezone(BEIJING_TZ).strftime("%Y-%m-%d %H:%M")
                },
                {
                    "source_name": "MakeTrend AI (原 APT Video AI)",
                    "domain": "maketrendai.com",
                    "url": "https://maketrendai.com/banana-tree-run-ai",
                    "title": "Banana Tree Run AI Video Generator | Single Photo to Parkour Clip",
                    "description": "Upload a photo and generate a viral 9:16 vertical video running across banana tree tops. Multi-language landing page.",
                    "entities": ["banana tree run", "ai video generator"]
,
                    "page_created_at": "2026-10-21 18:30"
,
                    "first_seen": datetime.now(timezone.utc).astimezone(BEIJING_TZ).strftime("%Y-%m-%d %H:%M")
                },
                {
                    "source_name": "TryAlorsOnDanse",
                    "domain": "tryalorsondanse.video",
                    "url": "https://tryalorsondanse.video/tools/cat-in-the-hat",
                    "title": "Cat in the Hat AI Doorbell Prank Video Generator",
                    "description": "Create spooky Halloween doorbell camera footage featuring the Cat in the Hat. Choose Doorbell, Window, or Behind me angles.",
                    "entities": ["cat in the hat", "doorbell prank"]
,
                    "page_created_at": "2026-10-21 21:00"
,
                    "first_seen": datetime.now(timezone.utc).astimezone(BEIJING_TZ).strftime("%Y-%m-%d %H:%M")
                },
                {
                    "source_name": "Media.io",
                    "domain": "www.media.io",
                    "url": "https://www.media.io/ai/explore/zone/hotel-lobby-ai-video-trend",
                    "title": "Media.io AI Effect Zone: Hotel Lobby AI Video Trend",
                    "description": "Generate trending hotel lobby duet dance videos automatically from portraits. pSEO dynamic template.",
                    "entities": ["hotel lobby", "duet dance"]
,
                    "page_created_at": "2026-10-22 09:20"
,
                    "first_seen": datetime.now(timezone.utc).astimezone(BEIJING_TZ).strftime("%Y-%m-%d %H:%M")
                },
                {
                    "source_name": "GetStarrd",
                    "domain": "www.getstarrd.app",
                    "url": "https://www.getstarrd.app/template/bby-wow-guy-ai-video",
                    "title": "Bby Wow Guy AI Video Dance Template | Starrd",
                    "description": "TikTok viral Latin dance trend Bby Wow Guy video template with KAROL G BGM.",
                    "entities": ["bby wow", "latin dance"]
,
                    "page_created_at": "2026-10-22 14:10"
,
                    "first_seen": datetime.now(timezone.utc).astimezone(BEIJING_TZ).strftime("%Y-%m-%d %H:%M")
                }
            ]
            collisions = [
                {
                    "term": "banana tree run",
                    "domains_count": 2,
                    "domains": ["knowyourmeme.com", "maketrendai.com"],
                    "collision_type": "meme_to_product",
                    "confidence": "high",
                    "has_meme_origin": True,
                    "first_seen": datetime.now(timezone.utc).isoformat()[:10],
                    "sample_urls": [
                        {"domain": "knowyourmeme.com", "url": "https://knowyourmeme.com/memes/banana-tree-run", "title": "Banana Tree Run Meme"},
                        {"domain": "maketrendai.com", "url": "https://maketrendai.com/banana-tree-run-ai", "title": "Banana Tree Run AI Generator"}
                    ]
                }
            ]
            total_new_count = len(newly_crawled_entries)
    # 5. 调用 summarizer 模块生成 Markdown 研报
    import summarizer
    now_utc = datetime.now(timezone.utc)
    now_beijing = now_utc.astimezone(BEIJING_TZ)
    date_str = now_beijing.strftime("%Y-%m-%d")
    slot_str = now_beijing.strftime("%H%M")
    report_title_date = now_beijing.strftime("%Y年%m月%d日 %H:%M") + " (北京时间)"
    current_run_ts = now_utc.isoformat()

    print(f"⏳ 正在调用大模型生成《全网模因与 AI 视频 6小时增量监控研报》({slot_str} 北京时间)...")
    report_md = summarizer.generate_report(
        date_str=date_str,
        slot_str=slot_str,
        report_title_date=report_title_date,
        last_run_ts=last_run,
        new_entries=newly_crawled_entries,
        collisions=collisions,
        source_stats=source_stats,
        current_run_ts=current_run_ts,
        capcut_trend=capcut_trend
    )

    # 6. 落盘保存研报至 meme-video/<date>/<slot>-monitor.md
    out_date_dir = os.path.join(REPORTS_DIR, date_str)
    os.makedirs(out_date_dir, exist_ok=True)
    report_file_path = os.path.join(out_date_dir, f"{slot_str}-monitor.md")
    rel_path_for_readme = f"reports/{date_str}/{slot_str}-monitor.md"

    if not args.dry_run:
        with open(report_file_path, "w", encoding="utf-8") as f:
            f.write(report_md)
        print(f"✅ 增量研报已成功落盘: {report_file_path}")

        # 更新 meme-video/README.md 索引表
        update_readme_index(date_str, slot_str, rel_path_for_readme, total_new_count, len(collisions))

        # 保存更新后的增量底库
        state_mgr.save()
        print(f"💾 实体知识库与已见 URL 底库已持久化至: {args.state}")

    # 7. 飞书卡片推送 (若配置了 Webhook 且非 dry-run)
    import notifier
    print("⏳ 正在检查并触发飞书实时卡片推送...")
    notifier.send_feishu_alert(
        date_str=date_str,
        slot_str=slot_str,
        total_new=total_new_count,
        collisions=collisions,
        report_rel_path=rel_path_for_readme
    )

    print("=================================================================")
    print("🎉 本次 6 小时模因与视频独立监控全部顺利完成！")
    print("=================================================================")


if __name__ == "__main__":
    main()
