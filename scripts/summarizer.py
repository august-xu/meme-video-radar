#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
summarizer.py — 模因与 AI 视频监控多模型通用 LLM 研报提炼器

特性：
  1. 零第三方依赖：纯原生 urllib.request 发起 HTTP 请求
  2. 多协议通用适配：
     - OpenAI 兼容协议 (OpenRouter / OpenAI / DeepSeek / 聚合中转)
     - 支持 openrouter/free 免费模型路由
     - 自动识别并支持 Google Gemini 原生 REST API
  3. 稳健容灾保底：若 LLM 发生网络抖动或超时，自动生成结构化事实研报，绝不丢失数据
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
import urllib.error
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta

# 业务展示统一时区：北京时间 (UTC+8)
BEIJING_TZ = timezone(timedelta(hours=8))


def format_beijing_time(ts_str: str) -> str:
    """将任何时间串统一转换为规范格式的北京时间: YYYY-MM-DD HH:MM"""
    if not ts_str or ts_str in ("首次运行", "N/A"):
        return "首次初始化基线"
    try:
        clean_s = ts_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(BEIJING_TZ).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return ts_str[:16].replace("T", " ")


def compute_gap_hours(since_ts: str, until_ts: str) -> float:
    """计算两次运行跨度小时数"""
    try:
        clean_s1 = since_ts.replace("Z", "+00:00")
        clean_s2 = until_ts.replace("Z", "+00:00")
        dt1 = datetime.fromisoformat(clean_s1)
        dt2 = datetime.fromisoformat(clean_s2)
        return round(abs((dt2 - dt1).total_seconds()) / 3600, 1)
    except Exception:
        return 6.0


def ensure_blank_links(text: str) -> str:
    """将普通 Markdown 链接转换为带有 target='_blank' 的 HTML 标签，保证外部链接安全新标签打开"""
    return re.sub(
        r'(?<!\!)\[([^\]]+)\]\((https?://[^)]+)\)',
        r'<a href="\2" target="_blank" rel="noopener noreferrer">\1</a>',
        text
    )


def call_openai_compatible(
    base_url: str,
    api_key: str,
    model: str,
    prompt: str,
    timeout_sec: int = 60
) -> str | None:
    """调用 OpenAI 兼容端点 (含 OpenRouter / DeepSeek / OpenAI)"""
    # 容错处理：如果 base_url 已经包含了 /chat/completions，不再重复拼接
    clean_base = base_url.rstrip("/")
    if clean_base.endswith("/chat/completions"):
        url = clean_base
    else:
        url = f"{clean_base}/chat/completions"

    # 1. 深度清洗环境变量（去除空格、换行符、不可见字符、单双引号）
    raw_model = model or ""
    has_whitespace = (raw_model != raw_model.strip())
    has_newlines = ("\n" in raw_model or "\r" in raw_model)
    has_quotes = (raw_model.startswith(("'", '"', '`')) or raw_model.endswith(("'", '"', '`')))

    cleaned_model = re.sub(r"[\r\n\t\u200b\ufeff]+", "", raw_model).strip().strip("'\"`").strip()
    while "openrouter/openrouter/" in cleaned_model:
        cleaned_model = cleaned_model.replace("openrouter/openrouter/", "openrouter/")

    # 打印明确的环境变量体检诊断日志，绝不靠猜
    print("🔍 [LLM 配置深度体检与诊断]")
    print(f"   • API 端点 URL: {url}")
    print(f"   • 原始模型名称长度: {len(raw_model)} 字符")
    if has_whitespace or has_newlines or has_quotes:
        print(f"   • ⚠️ 检测到配置项中存在干扰字符: [空格: {has_whitespace}, 换行: {has_newlines}, 引号: {has_quotes}]，已自动强力清洗剥离！")
    print(f"   • 清洗后初始模型 ID: '{cleaned_model}'")

    # 防呆纠错：如果 model 误填成了 API Key (如 sk- 开头)，自动重置
    if cleaned_model.startswith("sk-") or (len(cleaned_model) > 35 and "/" not in cleaned_model):
        print(f"   • ⚠️ 检测到模型名称疑似误填为 API Key，已自动纠正为 'openrouter/free'")
        cleaned_model = "openrouter/free"

    # 针对 OpenRouter 场景构建高可靠候选模型序列 (openrouter/free 为官方最稳聚合路由)
    is_openrouter = "openrouter" in clean_base.lower()
    candidate_models = []
    if is_openrouter:
        if cleaned_model in ("", "free", "openrouter/free", "openrouter/auto"):
            candidate_models = ["openrouter/free"]
        else:
            candidate_models = [cleaned_model, "openrouter/free"]
    else:
        candidate_models = [cleaned_model or "deepseek-chat"]

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key.strip()}",
    }
    if is_openrouter:
        headers["HTTP-Referer"] = "https://github.com/august-xu/research-dossiers"
        headers["X-Title"] = "Meme Video Radar"

    for current_model in candidate_models:
        print(f"🤖 正在请求大模型端点 (模型: {current_model})...")
        payload = {
            "model": current_model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位精通全球网络流行文化（Meme）、社媒热点趋势、短视频动效与出海独立开发（Micro-SaaS）的商业分析师。你的任务是将最新的网页差分和跨域碰撞事实，编写成专业、硬核、可落地的决策研报。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.4,
            "max_tokens": 3000
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
                content = resp_data["choices"][0]["message"]["content"]
                if content and len(content.strip()) > 50:
                    print(f"✅ 大模型成功响应 (当前生效模型: {current_model})！")
                    return content.strip()
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8", "ignore")
            sys.stderr.write(f"[WARN] 模型 '{current_model}' 请求返回 HTTPError {e.code}: {err_msg}\n")
            print(f"🔄 模型 '{current_model}' 不可用，自动尝试下一个候选模型...")
            continue
        except Exception as e:
            sys.stderr.write(f"[WARN] 模型 '{current_model}' 调用异常: {e}\n")
            print(f"🔄 模型 '{current_model}' 异常，自动尝试下一个候选模型...")
            continue

    return None


def call_gemini_native(
    api_key: str,
    model: str,
    prompt: str,
    timeout_sec: int = 60
) -> str | None:
    """调用 Google Gemini 官方原生 REST API"""
    if not model or model == "openrouter/free":
        model = "gemini-2.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 3000
        }
    }
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            resp_data = json.loads(resp.read().decode("utf-8"))
            content = resp_data["candidates"][0]["content"]["parts"][0]["text"]
            return content.strip()
    except Exception as e:
        sys.stderr.write(f"[WARN] Gemini 原生接口调用失败: {e}\n")
        return None


def render_new_entries_markdown(new_entries: List[dict]) -> str:
    """标准格式化输出各站点新增 URL 详细清单，确保多层列表换行分明、排版美观"""
    if not new_entries:
        return "⚪ 本次窗口无新收录页面。\n"

    by_src = {}
    for e in new_entries:
        by_src.setdefault(e.get("source_name", e.get("domain")), []).append(e)

    blocks = []
    for src_name, items in by_src.items():
        sub_lines = [f"### 🌐 {src_name}（新增 {len(items)} 个页面）\n"]
        for it in items:
            u = it.get("url", "")
            t = (it.get("title") or u).replace("\n", " ").strip()
            sub_lines.append(f"- <a href=\"{u}\" target=\"_blank\" rel=\"noopener noreferrer\">**{t}**</a>")
            time_parts = []
            if it.get("first_seen"):
                time_parts.append(f"发现时间: `{it['first_seen']}`")
            if it.get("lastmod"):
                time_parts.append(f"页面更新: `{it['lastmod']}`")
            if time_parts:
                sub_lines.append(f"  - {' ｜ '.join(time_parts)}")
            if it.get("description"):
                desc = it["description"].replace("\n", " ").strip()[:160]
                sub_lines.append(f"  - 描述: {desc}")
            if it.get("entities"):
                ents = [e for e in it["entities"][:5] if e]
                if ents:
                    sub_lines.append(f"  - 实体词: `{', '.join(ents)}`")
            sub_lines.append("")  # 每个条目间留出空行，符合 Markdown 标准规范
        blocks.append("\n".join(sub_lines))

    return "\n\n".join(blocks)


def build_fallback_report(
    date_str: str,
    slot_str: str,
    report_title_date: str,
    last_run_ts: str,
    new_entries: List[dict],
    collisions: List[dict],
    source_stats: List[dict],
    current_run_ts: str = ""
) -> str:
    """保底研报：当 LLM 完全不可用时，输出结构化事实 Markdown"""
    cur_ts = current_run_ts or datetime.now(timezone.utc).isoformat()
    since_bj = format_beijing_time(last_run_ts)
    until_bj = format_beijing_time(cur_ts)
    gap_h = compute_gap_hours(last_run_ts, cur_ts)
    window_line = f"> 📅 监测窗口：`{since_bj}` → `{until_bj}`（北京时间，跨度 {gap_h} 小时） | 🎯 窗口内新增页面：**{len(new_entries)}** 条 | 💥 检测到跨域碰撞：**{len(collisions)}** 组\n"

    lines = [
        f"# ⚡ 全网模因与 AI 视频落地页 6小时增量监控与跨域碰撞研报 ({report_title_date})\n",
        window_line,
        "---\n",
        "## 💥 核心跨域碰撞事实表 (Cross-Domain Collisions)\n"
    ]
    if collisions:
        for c in collisions:
            c_type = "【Meme-to-Product 模因落地闭环】" if c["collision_type"] == "meme_to_product" else "【同行扎堆抢跑】"
            lines.append(f"### 🔥 {c_type} `{c['term']}`（跨 {c['domains_count']} 个独立域名）")
            lines.append(f"- **首次发现时间**：`{c.get('first_seen', 'N/A')}`")
            lines.append(f"- **涉及站点**：{', '.join(c['domains'])}")
            lines.append("- **代表性页面**：")
            for u in c.get("sample_urls", []):
                lines.append(f"  - <a href=\"{u['url']}\" target=\"_blank\" rel=\"noopener noreferrer\">{u.get('title') or u['url']}</a> (`{u['domain']}`)")
            lines.append("")
    else:
        lines.append("⚪ 本次窗口暂未检测到命中 >=2 个域的跨站碰撞。\n")

    lines.append("---\n\n## 📋 各站点新增 URL 详细清单 (全量索引)\n")
    lines.append(render_new_entries_markdown(new_entries))
    return "\n".join(lines)


def generate_report(
    date_str: str,
    slot_str: str,
    report_title_date: str,
    last_run_ts: str,
    new_entries: List[dict],
    collisions: List[dict],
    source_stats: List[dict],
    current_run_ts: str = ""
) -> str:
    """生成最终 Markdown 研报"""
    # 准备 Prompt 结构化数据
    summary_data = {
        "monitor_window": {
            "since": last_run_ts,
            "total_new_entries": len(new_entries),
            "collisions_count": len(collisions)
        },
        "source_stats": source_stats,
        "collisions": collisions[:15],
        "top_new_entries": [
            {
                "source": e.get("source_name"),
                "url": e.get("url"),
                "title": e.get("title"),
                "description": e.get("description", "")[:180],
                "entities": e.get("entities", [])[:5]
            }
            for e in new_entries[:25]
        ]
    }

    cur_ts = current_run_ts or datetime.now(timezone.utc).isoformat()
    since_bj = format_beijing_time(last_run_ts)
    until_bj = format_beijing_time(cur_ts)
    gap_h = compute_gap_hours(last_run_ts, cur_ts)
    window_line = f"> 📅 监测窗口：`{since_bj}` → `{until_bj}`（北京时间，跨度 {gap_h} 小时） | 🎯 窗口内新增页面：{len(new_entries)} 条 | 💥 跨域碰撞数：{len(collisions)} 组"

    prompt = f"""请根据以下 6 小时内捕获的【模因与短视频动效落地页增量数据及跨域碰撞事实】，编写一份结构紧凑、高信噪比的《全网模因与 AI 视频落地页 6小时增量监控与跨域碰撞研报 ({report_title_date})》。

【输入数据 JSON】：
```json
{json.dumps(summary_data, ensure_ascii=False, indent=2)}
```

【撰写结构要求】：
# ⚡ 全网模因与 AI 视频落地页 6小时增量监控与跨域碰撞研报 ({report_title_date})
{window_line}

## 💥 核心跨域碰撞深度解构 (Cross-Domain Collisions)
- 逐一分析碰撞数据中的重点词条，说明：
  1. 它是【模因落地闭环 (KYM × 工具站)】还是【竞品扎堆抢跑 (多个商业站)】；
  2. 为什么该词会在这几个站点同时出现？背后的 TikTok/Reels 真实场景是什么？
  3. 列出代表性页面链接（必须使用 HTML 标签：<a href="URL" target="_blank" rel="noopener noreferrer">文字</a>）。

## ⚡ 6小时突发单域动向 (Single-Domain Emerging)
- 重点解构新增页面中的亮点落地页（尤其是万兴 Media.io 动态 Zone、APT Video AI、TryAlorsOnDanse 等出海团队的新模版）；
- 提炼其背后的通用痛点词（Generic Job，如 `two photos dance video generator`）。

## 🚀 独立开发与微创新商机 (24~48h MVP)
- 给独立开发者/出海团队 2~3 个具体务实的灵感（如单功能轻量站、Prompt截流博客、模板制作）。

注意：
1. 语言干练，严禁套话、废话和虚空宏大叙事。
2. 凡是页面或站点链接，必须使用 `<a href="URL" target="_blank" rel="noopener noreferrer">名称</a>` 格式。
3. 请直接输出标准 Markdown 正文："""

    # 读取环境变量中的模型配置
    llm_api_key = os.environ.get("LLM_API_KEY") or os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")
    llm_base_url = os.environ.get("LLM_BASE_URL")
    llm_model = os.environ.get("LLM_MODEL", "openrouter/free")

    # 默认回退到 OpenRouter 官方端点
    if not llm_base_url:
        if "openrouter" in llm_model.lower() or (llm_api_key and llm_api_key.startswith("sk-or-")):
            llm_base_url = "https://openrouter.ai/api/v1"
        elif "deepseek" in llm_model.lower():
            llm_base_url = "https://api.deepseek.com"
        else:
            llm_base_url = "https://api.openai.com/v1"

    gemini_key = os.environ.get("GEMINI_API_KEY")

    ai_output = None
    if llm_api_key:
        print(f"🤖 正在通过 OpenAI 兼容接口请求大模型 ({llm_base_url}, model: {llm_model})...")
        ai_output = call_openai_compatible(llm_base_url, llm_api_key, llm_model, prompt, timeout_sec=70)

    if not ai_output and gemini_key:
        print("🤖 正在通过 Google Gemini 原生接口请求大模型...")
        ai_output = call_gemini_native(gemini_key, llm_model, prompt, timeout_sec=60)

    # 如果模型调用失败，使用保底模板
    if not ai_output or len(ai_output.strip()) < 200:
        print("⚠️ LLM 调用未返回有效内容，使用高精度事实保底报告。")
        return build_fallback_report(
            date_str, slot_str, report_title_date, last_run_ts, new_entries, collisions, source_stats
        )

    # 格式化外部链接并追加全量清单附录
    ai_output = ensure_blank_links(ai_output)

    appendix_text = "\n\n---\n\n## 📋 各站点新增 URL 详细清单 (全量索引)\n\n" + render_new_entries_markdown(new_entries)
    return ai_output.strip() + appendix_text
