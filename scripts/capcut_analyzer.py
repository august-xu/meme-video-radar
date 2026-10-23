#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
capcut_analyzer.py — CapCut Most-Used 时序快照与热度生命周期分析引擎

职责（每次运行）：
  1. 读取 capcut_crawler 抓到的当期视频模板列表（Top 20，含精确 useCount）
  2. 追加写入 JSONL 时序快照（data/capcut_history.jsonl，每行一次快照）
  3. 与 6h 前 / 24h 前的快照做差分：
       - delta_6h   = useCount(现在) - useCount(6h前)     → 6小时增量
       - rank_delta = 名次(6h前) - 名次(现在)              → 正数=冲榜
       - age_days   = (now - uploadDate) 天数              → 上架天数
       - daily_v    = useCount / age_days                  → 日均爆发力
  4. 生命周期状态机（阈值在冷启动期后由实际分布动态校准）：
       🆕 new_entry     本期新进入榜单（历史快照中从未出现）
       🔥 surging       6h增量 >= surge_threshold 或 (rank_delta>=5 且 use>=200k)
       📈 heating       age<=7天 且 daily_v >= 20k/天
       💎 saturated     use>=1M 但增量停滞
       📉 cooling       rank_delta <= -4，或增量较自身近期高点跌逾70%
       ⚪ stable        其余
  5. 识别「跌出榜单」：上一期在榜、本期消失的模板（最强下降信号）
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

BEIJING_TZ = timezone(timedelta(hours=8))

# 路径
_CUR = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(_CUR)
HISTORY_FILE = os.path.join(_REPO, "data", "capcut_history.jsonl")

# 保留最近 60 天快照（每天4次=240行，每行~10KB，约2.4MB）
MAX_HISTORY_LINES = 240 * 3

# ---------- 冷启动与阈值 ----------
# 前 3 天（12 个快照）只积累不判定状态；之后用实际增量的 P90 动态校准 surge 阈值。
CALIBRATION_SNAPSHOTS = 12
DEFAULT_SURGE_THRESHOLD = 50000      # 冷启动缺省值（推测值，校准后覆盖）
HEATING_DAILY_V = 20000              # 升温期日均爆发力门槛（推测值）
SATURATED_TOTAL = 1000000            # 稳态体量门槛


def _now_bj() -> str:
    return datetime.now(timezone.utc).astimezone(BEIJING_TZ).strftime("%Y-%m-%d %H:%M")


def load_history() -> List[dict]:
    """读取全部历史快照（每行一个 {ts, templates:{tid:{use,rank,title}}}）"""
    snaps = []
    if not os.path.exists(HISTORY_FILE):
        return snaps
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    snaps.append(json.loads(line))
                except Exception:
                    continue
    except Exception as e:
        sys.stderr.write(f"[WARN] 读取 capcut_history 失败: {e}\n")
    return snaps


def append_snapshot(templates: List[dict]) -> dict:
    """把当期快照追加写入 JSONL。templates 为 capcut_crawler 的返回值（仅视频）。"""
    ts = _now_bj()
    tpl_map = {}
    for rank, t in enumerate(templates, 1):
        tid = t.get("template_id") or t.get("url", "").rstrip("/").split("/")[-1]
        tpl_map[tid] = {
            "use": t.get("use_count", 0),
            "rank": rank,
            "title": t.get("title", ""),
        }
    snap = {"ts": ts, "templates": tpl_map}
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(snap, ensure_ascii=False) + "\n")
    _trim_history()
    return snap


def _trim_history():
    """滚动修剪，防止历史文件无限膨胀"""
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if len(lines) > MAX_HISTORY_LINES:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                f.writelines(lines[-MAX_HISTORY_LINES:])
    except Exception:
        pass


def _find_snapshot(snaps: List[dict], hours_ago: float) -> dict:
    """找最接近 N 小时前的快照（容忍 ±2h）"""
    if not snaps:
        return {}
    target = datetime.now(BEIJING_TZ) - timedelta(hours=hours_ago)
    best, best_diff = None, None
    for s in snaps:
        try:
            ts = datetime.strptime(s["ts"], "%Y-%m-%d %H:%M").replace(tzinfo=BEIJING_TZ)
        except Exception:
            continue
        diff = abs((ts - target).total_seconds())
        if best_diff is None or diff < best_diff:
            best, best_diff = s, diff
    # 超出容忍窗口（目标±3h）视为找不到
    if best is not None and best_diff is not None and best_diff <= 3 * 3600:
        return best
    return {}


def _calibrate_surge_threshold(snaps: List[dict]) -> int:
    """用近期全部 6h 相邻快照对的增量分布的 P90 动态定爆火阈值；样本不足回退缺省"""
    deltas = []
    for prev, cur in zip(snaps, snaps[1:]):
        for tid, t in cur.get("templates", {}).items():
            p = prev.get("templates", {}).get(tid)
            if p and t.get("use", 0) > p.get("use", 0):
                deltas.append(t["use"] - p["use"])
    if len(deltas) < 20:
        return DEFAULT_SURGE_THRESHOLD
    deltas.sort()
    p90 = deltas[int(len(deltas) * 0.9)]
    return max(p90, 1000)  # 下限保护


def analyze(templates: List[dict]) -> dict:
    """
    主入口：写入当期快照并产出分析结果。
    返回:
      {
        "lifecycle": [ {title, template_id, use_count, delta_6h, rank, rank_delta,
                        age_days, daily_v, status, status_label, url, clips_count} ],
        "new_entries":   [ ... ],   # 本期新上榜
        "dropped_out":   [ ... ],   # 上期在榜本期消失
        "snapshot_count": int,
        "calibrating": bool         # 是否处于冷启动校准期
      }
    """
    snaps = load_history()
    cur = append_snapshot(templates)
    snaps.append(cur)

    snap_6h = _find_snapshot(snaps[:-1], 6)
    prev_snap = snaps[-2] if len(snaps) >= 2 else {}

    surge_thr = _calibrate_surge_threshold(snaps)
    calibrating = len(snaps) <= CALIBRATION_SNAPSHOTS

    now_ts = datetime.now(BEIJING_TZ)
    lifecycle, new_entries = [], []
    prev_ids = set(prev_snap.get("templates", {}).keys())
    hist_ids = {tid for s in snaps[:-1] for tid in s.get("templates", {})}

    for t in templates:
        tid = t.get("template_id") or t.get("url", "").rstrip("/").split("/")[-1]
        use = t.get("use_count", 0)
        rank = next((i for i, x in enumerate(templates, 1)
                     if (x.get("template_id") or x.get("url","").rstrip("/").split("/")[-1]) == tid), 0)

        # 6h 增量与名次变动
        ref6 = snap_6h.get("templates", {}).get(tid)
        delta_6h = (use - ref6["use"]) if ref6 else None
        rank_delta = (ref6["rank"] - rank) if ref6 else None

        # 上架天数与日均爆发力
        age_days, daily_v = None, None
        created = t.get("page_created_at", "")
        if created:
            try:
                ct = datetime.strptime(created, "%Y-%m-%d %H:%M").replace(tzinfo=BEIJING_TZ)
                age_days = round(max((now_ts - ct).total_seconds() / 86400.0, 0.1), 1)
                daily_v = int(use / age_days) if age_days > 0 else None
            except Exception:
                pass

        # 状态机
        is_new = tid not in hist_ids
        if is_new:
            status, label = "new_entry", "🆕 新上榜"
        elif calibrating:
            status, label = "collecting", "⚪ 数据积累中"
        elif delta_6h is not None and delta_6h >= surge_thr:
            status, label = "surging", "🔥 爆火"
        elif rank_delta is not None and rank_delta >= 5 and use >= 200000:
            status, label = "surging", "🔥 爆火"
        elif age_days is not None and age_days <= 7 and (daily_v or 0) >= HEATING_DAILY_V:
            status, label = "heating", "📈 升温"
        elif use >= SATURATED_TOTAL and (delta_6h is not None and delta_6h < surge_thr * 0.3):
            status, label = "saturated", "💎 高热稳态"
        elif rank_delta is not None and rank_delta <= -4:
            status, label = "cooling", "📉 降温"
        else:
            status, label = "stable", "⚪ 平稳"

        item = {
            "template_id": tid,
            "title": t.get("title", ""),
            "url": t.get("url", ""),
            "use_count": use,
            "rank": rank,
            "delta_6h": delta_6h,
            "rank_delta": rank_delta,
            "age_days": age_days,
            "daily_v": daily_v,
            "clips_count": t.get("clips_count"),
            "tags": t.get("tags", []),
            "video_url": t.get("video_url", ""),
            "status": status,
            "status_label": label,
        }
        lifecycle.append(item)
        if is_new:
            new_entries.append(item)

    # 跌出榜单：上期在榜、本期不在
    cur_ids = {x["template_id"] for x in lifecycle}
    dropped = []
    for tid in (prev_ids - cur_ids):
        p = prev_snap.get("templates", {}).get(tid, {})
        dropped.append({
            "template_id": tid,
            "title": p.get("title", ""),
            "last_use": p.get("use", 0),
            "last_rank": p.get("rank", 0),
        })

    # 排序输出：新上榜 > 爆火 > 升温 > 稳态 > 降温
    order = {"new_entry": 0, "surging": 1, "heating": 2, "stable": 3, "saturated": 4, "cooling": 5, "collecting": 6}
    lifecycle.sort(key=lambda x: (order.get(x["status"], 9), -(x["use_count"] or 0)))

    return {
        "lifecycle": lifecycle,
        "new_entries": new_entries,
        "dropped_out": dropped,
        "snapshot_count": len(snaps),
        "surge_threshold": surge_thr,
        "calibrating": calibrating,
    }


if __name__ == "__main__":
    import capcut_crawler
    items = capcut_crawler.crawl_capcut_most_used()
    video_only = [t for t in items]
    res = analyze(video_only)
    print(f"快照总数: {res['snapshot_count']} | 校准期: {res['calibrating']} | 爆火阈值: {res['surge_threshold']:,}")
    print(f"新上榜: {len(res['new_entries'])} | 跌出榜: {len(res['dropped_out'])}")
    for x in res["lifecycle"][:8]:
        d6 = f"+{x['delta_6h']:,}" if x["delta_6h"] is not None else "—"
        rd = f"⬆{x['rank_delta']}" if (x["rank_delta"] or 0) > 0 else (f"⬇{abs(x['rank_delta'])}" if (x["rank_delta"] or 0) < 0 else "—")
        print(f"  {x['status_label']:<8} 第{x['rank']:>2}名 {x['title'][:28]:<30} use={x['use_count']:>10,} Δ6h={d6:>9} {rd}")
