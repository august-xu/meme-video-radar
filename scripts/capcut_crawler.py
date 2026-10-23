#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
capcut_crawler.py — CapCut (剪映海外版) Most Used 热门爆款模板爬虫

机制与价值：
  1. 纯原生 HTTP 请求，解析 Modern.js SSR 首帧数据，零无头浏览器依赖，耗时 < 1 秒
  2. 提取全球短视频最源头的卡点动效、热门模因神曲与模版规格
  3. 捕获核心商业指标：
     - templateId: 模板唯一标识 (拼装官网直达落地页)
     - title & titleDesc: 模板标题及关联的 TikTok 核心话题标签 (#trend, #dance 等)
     - useCount: 真实剪同款使用量 (精确量化全网热度)
     - clipsCount: 所需照片/切片张数 (1图=单图换脸/换装; 2图=双人合影/对镜; 多图=卡点)
     - uploadDate: 精确到秒的模板真实上传时间戳 (Unix Timestamp)
     - videoUrl: 免登录、无水印的 1080P/720P MP4 视频预览直链
     - coverUrl: 高清封面图
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
CAPCUT_EXPLORE_URL = "https://www.capcut.com/explore/most-used"
BEIJING_TZ = timezone(timedelta(hours=8))


def parse_json_array_balanced(html: str, key_marker: str = '"videoTemplates":[') -> list:
    """使用精准括号栈匹配，从 HTML 字符串中提取 JSON 数组，避免贪婪正则截断或转义错误"""
    idx = html.find(key_marker)
    if idx == -1:
        return []

    start_pos = idx + len(key_marker) - 1
    depth = 0
    end_pos = -1
    in_string = False
    escape = False

    for i in range(start_pos, len(html)):
        ch = html[i]
        if escape:
            escape = False
            continue
        if ch == '\\':
            escape = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if not in_string:
            if ch == '[':
                depth += 1
            elif ch == ']':
                depth -= 1
                if depth == 0:
                    end_pos = i + 1
                    break

    if end_pos == -1:
        return []

    raw_json = html[start_pos:end_pos]
    clean_json = raw_json.replace('\\u002F', '/')
    try:
        return json.loads(clean_json)
    except Exception as e:
        sys.stderr.write(f"[WARN] CapCut JSON 解析失败: {e}\n")
        return []


def crawl_capcut_most_used(timeout: int = 20) -> List[dict]:
    """抓取并解析 CapCut Most Used 热门爆款模板列表"""
    req = urllib.request.Request(
        CAPCUT_EXPLORE_URL,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            html_text = resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        sys.stderr.write(f"[WARN] 获取 CapCut Most Used 失败: {e}\n")
        return []

    raw_templates = parse_json_array_balanced(html_text)
    if not raw_templates:
        sys.stderr.write("[WARN] 未能在 CapCut 页面中提取到 videoTemplates 数据\n")
        return []

    now_bj = datetime.now(timezone.utc).astimezone(BEIJING_TZ).strftime("%Y-%m-%d %H:%M")
    results = []

    for item in raw_templates:
        template_id = str(item.get("templateId") or item.get("id") or "").strip()
        if not template_id:
            continue

        title = str(item.get("title") or "").strip()
        title_desc = str(item.get("titleDesc") or "").strip()
        use_count = item.get("useCount") or 0
        like_count = item.get("likeCount") or 0
        duration_ms = item.get("templateDuration") or 0
        duration_sec = round(duration_ms / 1000.0, 1) if duration_ms else 0.0

        struct = item.get("structuredData") or {}
        clips_count = struct.get("clipsCount") or 1
        upload_ts = struct.get("uploadDate") or 0

        # 格式化真实上传时间戳为北京时间
        created_at_str = ""
        if upload_ts:
            try:
                dt_created = datetime.fromtimestamp(upload_ts, tz=timezone.utc).astimezone(BEIJING_TZ)
                created_at_str = dt_created.strftime("%Y-%m-%d %H:%M")
            except Exception:
                pass

        # 视频直链与封面
        video_url = item.get("videoUrl") or struct.get("contentUrl") or ""
        cover_url = item.get("coverUrl") or struct.get("thumbnailUrl") or ""
        template_url = f"https://www.capcut.com/template-detail/{template_id}"

        # 提取话题标签
        tags = re.findall(r"#([a-zA-Z0-9_\u4e00-\u9fa5]+)", title_desc)

        results.append({
            "source_id": "capcut",
            "source_name": "CapCut (剪映海外版)",
            "domain": "www.capcut.com",
            "role": "template_origin",
            "template_id": template_id,
            "name": title or f"CapCut Template {template_id[:8]}",
            "title": title,
            "title_desc": title_desc,
            "tags": tags,
            "url": template_url,
            "canonical_url": template_url,
            "use_count": use_count,
            "like_count": like_count,
            "clips_count": clips_count,
            "duration_sec": duration_sec,
            "video_url": video_url,
            "cover_url": cover_url,
            "page_created_at": created_at_str,
            "first_seen": now_bj,
            "description": f"CapCut 全球爆款模板，剪同款使用量: {use_count:,} 次，所需素材: {clips_count} 张照片/切片，时长: {duration_sec}秒。标签: {title_desc[:100]}"
        })

    return results


if __name__ == "__main__":
    t0 = time.time()
    items = crawl_capcut_most_used()
    print(f"抓取耗时: {time.time()-t0:.2f}s | 共获取 {len(items)} 个 CapCut 爆款模板:")
    for it in items[:6]:
        print(f"  🔥 [{it['name']}] 使用量: {it['use_count']:,} 次 | 所需照片: {it['clips_count']} 张 | 格式: {it['page_created_at']}")
        print(f"     链接: {it['url']}")
        print(f"     标签: {', '.join(it['tags'][:5])}")
