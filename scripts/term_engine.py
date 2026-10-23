#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
term_engine.py — 模因与 AI 视频实体挖掘与跨域碰撞引擎

专门针对网络模因（Meme）与短视频动效落地页（AI Video Landing Pages）：
1. 深度清洗 URL slug、页面 Title 与描述中的噪音词与通用词
2. 提取具体的模因实体短语（Entity Phrases: unigram, bigram, trigram）
3. 统计各实体在历史知识库与本次增量中的跨域出现频次
4. 识别两类高价值碰撞：
   - 【Meme-to-Product 模因落地闭环】：Know Your Meme (梗源) × 商业工具站 (落地页)
   - 【Competitor Swarm 竞品扎堆抢跑】：>= 2 个独立商业工具站同时铺设该词
"""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Dict, List, Set, Tuple
from urllib.parse import urlparse

# 通用停用词 + 视频/模因领域的泛化大路货（必须过滤，避免假碰撞）
STOP_WORDS = set("""
a an and are as at be by can for from has have in into is it its of on or that the this to with your you
about after all also any around back been before being between both but came could did do does down each
even find first get give go good had he her here him his how if just know like look make many may me
more most much must my new no not now off only out over said see she should so some take than their them
then there these they through time up uses using very was way we well were what when which who will would
ai app apps tool tools generator maker creator builder editor online free web software pro
video videos photo photos image images picture pictures pic pics clip clips reel reels short shorts
tiktok instagram youtube social media prompt prompts template templates guide tutorial tutorials
meme memes trending trend trends viral dance dances effect effects filter filters feature features
how make create get use turn convert easily fast simple best top new official officialsite
download watch listen view full hd 4k 1080p page site sitemap post blog news article explore zone
two three four five six seven eight nine ten
dog dogs cat cats pet pets baby babies boy girl man woman person people
mascota mascotas baile bailes foto fotos con sin del para por que como una uno un el la los las tu su
nah cuh tik tok
com net org io app co video me xyz
""".split())

# URL 中常见的无意义路径与语言代码
PATH_NOISE_TOKENS = set("""
lp ai-video image-to-video tools effects templates how-to blog memes videos search category tag
zh cn tw ja jp en es fr de pt ru ar ko it
""".split())

_CAMEL_REGEX = re.compile(r"(?<=[a-z])(?=[A-Z])")
_NON_ALPHANUM = re.compile(r"[^a-z0-9\s]+")
_MULTISPACE = re.compile(r"\s+")


def clean_text(text: str) -> str:
    """归一化文本：转小写、展开驼峰、替换标点为空格"""
    if not text:
        return ""
    text = _CAMEL_REGEX.sub(" ", text)
    text = _NON_ALPHANUM.sub(" ", text.lower())
    return _MULTISPACE.sub(" ", text).strip()


def extract_slug_text(url: str) -> str:
    """从 URL 中提取最具信息量的末尾 slug 文本，剥离常见的语言和分类前缀"""
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if not path:
        return ""
    
    parts = path.split("/")
    # 过滤掉常见路径前缀如 /lp/, /zh/, /tools/, /explore/zone/
    valid_parts = [p for p in parts if p.lower() not in PATH_NOISE_TOKENS]
    if not valid_parts:
        valid_parts = parts
    
    # 取最末尾的核心 slug（例如 banana-tree-run-ai -> banana tree run）
    slug = valid_parts[-1]
    # 去除常见的 .html, .xml 扩展名
    slug = re.sub(r"\.(html?|xml|php|aspx?)$", "", slug, flags=re.IGNORECASE)
    # 替换连接符
    slug = slug.replace("-", " ").replace("_", " ")
    return clean_text(slug)


def extract_entity_terms(text: str, max_words: int = 4) -> Set[str]:
    """
    从清理后的文本中提取 1~4 元连续短语候选。
    严格过滤全停用词短语与短数字。
    """
    words = clean_text(text).split()
    # 单独移除末尾常见的后缀词如 "ai", "generator", "online", "free"
    filtered_words = [w for w in words if w not in PATH_NOISE_TOKENS]
    if not filtered_words:
        filtered_words = words

    n = len(filtered_words)
    candidates = set()

    # 核心红线：模因实体必须是具体的复合短语 (至少 2 个单词)！严禁单个单词造成泛化假碰撞
    for length in range(2, min(max_words + 1, n + 1)):
        for i in range(n - length + 1):
            phrase_words = filtered_words[i:i + length]
            # 剥离首尾通用停用词
            while phrase_words and phrase_words[0] in STOP_WORDS:
                phrase_words = phrase_words[1:]
            while phrase_words and phrase_words[-1] in STOP_WORDS:
                phrase_words = phrase_words[:-1]
            if not phrase_words:
                continue
            phrase = " ".join(phrase_words).strip()
            # 过滤纯停用词组成的短语、短于3字符、纯数字
            if len(phrase) >= 3 and not phrase.replace(" ", "").isdigit():
                candidates.add(phrase)

    return candidates


def extract_page_entities(url: str, title: str = "", meta_desc: str = "") -> Set[str]:
    """
    综合 URL slug 与 Title 提取该页面的实体候选集合。
    对模因页面来说，slug 和 title 包含最高浓度的实体信息。
    """
    slug_text = extract_slug_text(url)
    slug_entities = extract_entity_terms(slug_text)

    title_entities = set()
    if title:
        # 去除常见的网站后缀如 " | LightX Editor", " - Know Your Meme"
        clean_title = re.sub(r"\s*[-|–—]\s*.*$", "", title)
        title_entities = extract_entity_terms(clean_title)

    # 实体优先以 slug 和 title 的交集或高质量短语为主
    entities = slug_entities | title_entities

    # 去嵌套：如果同时有 "banana tree run" 和 "banana", 优先保留长实体
    pruned = set()
    sorted_entities = sorted(entities, key=lambda x: len(x), reverse=True)
    for ent in sorted_entities:
        # 严格过滤单单词：实体必须至少由 2 个单词组成！
        words = ent.split()
        if len(words) < 2:
            continue
        if ent in STOP_WORDS or len(ent) < 5:
            continue
        pruned.add(ent)

    return pruned


def detect_collisions(
    entities_db: Dict[str, dict],
    min_domains: int = 2
) -> List[dict]:
    """
    跨域碰撞判定：
    接收当前全局实体知识库 entities_db，格式：
    {
      "banana tree run": {
        "first_seen": "2026-10-20T08:00:00",
        "domains": {
          "knowyourmeme.com": [{"url": "...", "title": "...", "first_seen": "..."}],
          "aptvideoai.com": [{"url": "...", "title": "...", "first_seen": "..."}]
        }
      }
    }
    输出符合条件的碰撞列表，按置信度和域名数降序排列。
    """
    collisions = []

    for term, data in entities_db.items():
        # 严格过滤单单词：只有 2~4 词复合短语才能发生跨域碰撞
        if len(term.split()) < 2:
            continue

        dom_map = data.get("domains", {})
        n_dom = len(dom_map)
        if n_dom < min_domains:
            continue

        # 检查是否命中 Know Your Meme 梗源
        has_meme_origin = any("knowyourmeme.com" in d for d in dom_map.keys())
        tool_domains = [d for d in dom_map.keys() if "knowyourmeme.com" not in d]

        # 碰撞类型分类
        collision_type = "multi_domain"
        confidence = "normal"
        if has_meme_origin and len(tool_domains) >= 1:
            collision_type = "meme_to_product"  # 梗源 + 工具落地闭环
            confidence = "high"
        elif len(tool_domains) >= 2:
            collision_type = "competitor_swarm" # 多个商业竞品扎堆抢跑
            confidence = "high"

        # 整理代表性页面
        sample_urls = []
        for d, u_list in dom_map.items():
            for item in u_list[:2]:  # 每个域取前 2 条代表 URL
                sample_urls.append({
                    "domain": d,
                    "url": item.get("url"),
                    "title": item.get("title", ""),
                    "first_seen": item.get("first_seen", "")
                })

        collisions.append({
            "term": term,
            "domains_count": n_dom,
            "domains": list(dom_map.keys()),
            "collision_type": collision_type,
            "confidence": confidence,
            "has_meme_origin": has_meme_origin,
            "first_seen": data.get("first_seen", ""),
            "sample_urls": sample_urls
        })

    # 排序：high 置信度优先，其次按域名数量，再次按最新发现时间
    collisions.sort(
        key=lambda x: (
            1 if x["confidence"] == "high" else 0,
            x["domains_count"],
            x["first_seen"]
        ),
        reverse=True
    )

    return collisions
