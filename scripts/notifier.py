#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
notifier.py — 模因与 AI 视频监控飞书通知模块

支持两种推送通道（自动探测）：
  通道 1（首选推荐·个人私聊）：通过飞书开放平台自建应用 (Bot / lark-cli 同款智能体) 直接私聊推送给你个人
       - 需要: FEISHU_APP_SECRET (App ID 与 User Open ID 已默认预置)
  通道 2（备选兜底·群机器人）：通过飞书群自定义 Webhook 机器人推送
       - 需要: FEISHU_WEBHOOK_URL
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import sys
import time
import urllib.request
import urllib.error
from typing import List, Dict, Any

GITHUB_REPO_URL = "https://github.com/august-xu/meme-video-radar/blob/main"

# 默认智能体应用与用户 OpenID (与本地 lark-cli 保持一致)
DEFAULT_APP_ID = "cli_a947bb510bf95bd7"
DEFAULT_USER_OPEN_ID = "ou_9a8e4fbc5605af13300ba19a2ba268e5"


def get_tenant_access_token(app_id: str, app_secret: str) -> str | None:
    """获取飞书自建应用的 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {"app_id": app_id, "app_secret": app_secret}
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("code") == 0:
                return data.get("tenant_access_token")
            else:
                sys.stderr.write(f"[WARN] 获取飞书 tenant_access_token 失败: {data}\n")
                return None
    except Exception as e:
        sys.stderr.write(f"[WARN] 请求飞书 token 异常: {e}\n")
        return None


def send_via_user_bot(app_id: str, app_secret: str, user_open_id: str, msg_text: str, gh_url: str) -> bool:
    """通过飞书自建应用 (智能体 Bot) 向用户个人发起私聊推送"""
    token = get_tenant_access_token(app_id, app_secret)
    if not token:
        return False

    url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }

    # 优先使用 interactive 卡片
    card_content = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": "⚡ 模因与AI视频 6h 预警"},
            "template": "carmine"
        },
        "elements": [
            {"tag": "markdown", "content": msg_text},
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {"tag": "plain_text", "content": "📖 在线阅读完整决策研报"},
                        "type": "primary",
                        "url": gh_url
                    }
                ]
            }
        ]
    }

    payload = {
        "receive_id": user_open_id,
        "msg_type": "interactive",
        "content": json.dumps(card_content, ensure_ascii=False)
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            if res.get("code") == 0:
                print("✅ 飞书自建应用私聊卡片消息推送成功！")
                return True
            else:
                print(f"⚠️ 飞书自建应用发送卡片报错: {res}，正在尝试降级为纯文本私聊...")
    except Exception as e:
        print(f"⚠️ 飞书自建应用卡片请求异常: {e}，尝试纯文本...")

    # 降级：纯文本私聊
    text_payload = {
        "receive_id": user_open_id,
        "msg_type": "text",
        "content": json.dumps({"text": f"{msg_text}\n\n在线直达: {gh_url}"}, ensure_ascii=False)
    }
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(text_payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            if res.get("code") == 0:
                print("✅ 飞书自建应用私聊纯文本消息推送成功！")
                return True
            else:
                print(f"❌ 飞书自建应用纯文本私聊失败: {res}")
                return False
    except Exception as e:
        print(f"❌ 飞书自建应用纯文本私聊异常: {e}")
        return False


def get_webhook_url() -> str:
    """按优先级尝试读取飞书 Webhook 环境变量"""
    for key in ["FEISHU_WEBHOOK_URL", "FEISHU_WEBHOOK", "LARK_WEBHOOK_URL", "LARK_WEBHOOK", "WEBHOOK_URL"]:
        val = os.environ.get(key, "").strip()
        if val:
            return val
    return ""


def send_via_webhook(webhook_url: str, msg_markdown: str, gh_url: str, collisions: list, slot_str: str) -> bool:
    """通道 2：群 Webhook 机器人兜底推送"""
    payload_card = {
        "msg_type": "interactive",
        "card": {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": f"⚡ 模因与AI视频 6h 预警 ({slot_str} 槽位)"},
                "template": "carmine" if collisions else "blue"
            },
            "elements": [
                {"tag": "markdown", "content": msg_markdown},
                {
                    "tag": "action",
                    "actions": [
                        {
                            "tag": "button",
                            "text": {"tag": "plain_text", "content": "📖 在线阅读完整研报"},
                            "type": "primary",
                            "url": gh_url
                        }
                    ]
                }
            ]
        }
    }

    req = urllib.request.Request(
        webhook_url,
        data=json.dumps(payload_card).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8")
            res = json.loads(raw)
            if res.get("code") == 0 or res.get("StatusCode") == 0:
                print("✅ 飞书群 Webhook 推送成功！")
                return True
            else:
                print(f"⚠️ 飞书群 Webhook 返回未成功: {raw}")
                return False
    except Exception as e:
        print(f"⚠️ 飞书群 Webhook 推送异常: {e}")
        return False


def send_feishu_alert(
    date_str: str,
    slot_str: str,
    total_new: int,
    collisions: List[dict],
    report_rel_path: str
) -> bool:
    """统一通知派发入口：优先智能体私聊，次选群 Webhook"""
    # 防噪音门禁：零新增且零碰撞直接不打扰
    if total_new == 0 and len(collisions) == 0:
        print("ℹ️ 本次运行无新增条目且无碰撞，触发防刷屏静默门禁，不推送飞书。")
        return False

    gh_url = f"{GITHUB_REPO_URL}/{report_rel_path}"

    # 提炼碰撞要点
    collision_highlights = []
    for c in collisions[:3]:
        c_type = "【模因闭环】" if c.get("collision_type") == "meme_to_product" else "【同行扎堆】"
        term = c["term"]
        doms = ", ".join(c["domains"][:3])
        collision_highlights.append(f"• {c_type} `{term}` ({len(c['domains'])}站: {doms})")

    collision_text = ""
    if collision_highlights:
        collision_text = "\n\n💥 **高置信度跨域碰撞**：\n" + "\n".join(collision_highlights)

    msg_markdown = (
        f"⚡ **【全网模因与 AI 视频 6小时增量预警】**\n"
        f"📅 **时段**：`{date_str} {slot_str[:2]}:{slot_str[2:]} (北京时间)`\n"
        f"🎯 **新增页面**：{total_new} 条 | 💥 **跨域碰撞**：{len(collisions)} 组"
        f"{collision_text}\n\n"
        f"🔗 **在线阅读决策研报**：\n{gh_url}"
    )

    # 1. 优先尝试自建应用私聊通道 (与本地 lark-cli 行为一致)
    app_secret = os.environ.get("FEISHU_APP_SECRET", "").strip()
    app_id = os.environ.get("FEISHU_APP_ID", "").strip() or DEFAULT_APP_ID
    user_open_id = os.environ.get("FEISHU_USER_ID", "").strip() or DEFAULT_USER_OPEN_ID

    if app_secret:
        print(f"🤖 检测到飞书自建应用配置 (AppID: {app_id})，正在通过智能体私聊推送到用户 ({user_open_id})...")
        if send_via_user_bot(app_id, app_secret, user_open_id, msg_markdown, gh_url):
            return True
        print("⚠️ 智能体私聊通道未成功，尝试备选 Webhook 通道...")

    # 2. 备选 Webhook 通道
    webhook_url = get_webhook_url()
    if webhook_url:
        print("📡 正在尝试飞书群 Webhook 通道...")
        if send_via_webhook(webhook_url, msg_markdown, gh_url, collisions, slot_str):
            return True

    if not app_secret and not webhook_url:
        print("⚠️ [飞书通知未发送] 未检测到 FEISHU_APP_SECRET (智能体私聊) 或 FEISHU_WEBHOOK_URL (群机器人)！")
        print("   推荐在 GitHub Secrets 配置 FEISHU_APP_SECRET，即可像本地 lark-cli 一样收到私聊推送。")
    return False



def send_feishu_heartbeat(
    date_str: str,
    slot_str: str,
    sources_count: int,
    tracked_urls: int
) -> bool:
    """零新增时的轻量巡航报平安打卡，告知用户系统健康运行且已准时执行"""
    app_secret = os.environ.get("FEISHU_APP_SECRET", "").strip()
    app_id = os.environ.get("FEISHU_APP_ID", "").strip() or DEFAULT_APP_ID
    user_open_id = os.environ.get("FEISHU_USER_ID", "").strip() or DEFAULT_USER_OPEN_ID

    msg_text = (
        f"🟢 **【模因与 AI 视频 6h 巡航打卡】**\n"
        f"⏰ **打卡时段**：`{date_str} {slot_str[:2]}:{slot_str[2:]} (北京时间)`\n"
        f"📡 **监控状态**：{sources_count} 个重点站点全部扫描完毕，存量基准库正常 ({tracked_urls} 条)。\n"
        f"⚪ **当期态势**：过去 6 小时全网无突发新模因与新增落地页，系统健康运行中。"
    )

    if app_secret:
        token = get_tenant_access_token(app_id, app_secret)
        if token:
            url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json; charset=utf-8"
            }
            card_content = {
                "config": {"wide_screen_mode": True},
                "header": {
                    "title": {"tag": "plain_text", "content": "🟢 模因与AI视频 6h 巡航正常"},
                    "template": "turquoise"
                },
                "elements": [
                    {"tag": "markdown", "content": msg_text}
                ]
            }
            payload = {
                "receive_id": user_open_id,
                "msg_type": "interactive",
                "content": json.dumps(card_content, ensure_ascii=False)
            }
            try:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers=headers,
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    res = json.loads(resp.read().decode("utf-8"))
                    if res.get("code") == 0:
                        print("✅ 飞书零新增巡航报平安推送成功！")
                        return True
            except Exception as e:
                print(f"⚠️ 飞书报平安发送异常: {e}")

    webhook_url = get_webhook_url()
    if webhook_url:
        payload = {
            "msg_type": "text",
            "content": {
                "text": f"🟢【模因与AI视频 6h 巡航正常】{date_str} {slot_str} UTC: {sources_count} 站点扫描完毕，当期零新增。"
            }
        }
        try:
            req = urllib.request.Request(
                webhook_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                print("✅ 飞书 Webhook 报平安推送成功！")
                return True
        except Exception:
            pass

    return False
