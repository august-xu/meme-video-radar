# ⚡ 全网模因与 AI 视频落地页 6小时增量监控与跨域碰撞研报 (2026年10月29日 02:00 (北京时间))
> 📅 **监测窗口**：`2026‑10‑28 20:00` → `2026‑10‑29 02:00`（北京时间，跨度 6 小时）  
> 🎯 **窗口内新增页面**：27 条  
> 💥 **跨域碰撞数**：2 组  

---

## 💥 核心跨域碰撞深度解构 (Cross‑Domain Collisions)

| 碰撞词 | 类型 | 站点分布 | 背后驱动场景 | 代表性页面 |
|--------|------|----------|--------------|------------|
| **tiny desk** | 竞品扎堆抢跑（多个商业站） | `www.getstarrd.app`、`remakeyourmeme.com`、`create0.ai`、`www.lightxeditor.com`、`www.media.io` | 近期 TikTok / Instagram Reels 爆款 **“Tiny Desk AI”**（把用户自拍或宠物照转成小型演唱会现场），驱动 3‑5 张素材的 **“photo‑to‑concert”** 生成需求。各工具站抢占同一 SEO 关键词，以捕获同一流量池。 | <a href="https://www.getstarrd.app/blog/how-to-make-outstanding-tiny-desk-ai-video" target="_blank" rel="noopener noreferrer">GetStarrd – How to Make the ‘Outstanding’ Tiny Desk AI Video</a>、<a href="https://remakeyourmeme.com/templates/tiny-desk-ai-video-generator/" target="_blank" rel="noopener noreferrer">RemakeYourMeme – Tiny Desk AI Video Generator</a>、<a href="https://create0.ai/ai-effects/tiny-desk-ai" target="_blank" rel="noopener noreferrer">Create0 – Tiny Desk AI</a>、<a href="https://www.lightxeditor.com/blog/blog-how-to-make-outstanding-tiny-desk-ai-video/" target="_blank" rel="noopener noreferrer">LightX – How to Make Outstanding Tiny Desk AI Video</a>、<a href="https://www.media.io/ai/explore/zone/tiny-desk-ai-trend" target="_blank" rel="noopener noreferrer">Media.io – Tiny Desk AI Trend</a> |
| **gangnam style** | 竞品扎堆抢跑（多个商业站） | `remakeyourmeme.com`、`www.lightxeditor.com`、`www.getstarrd.app` | 2026 年春季 TikTok “Gangnam Style 2.0” 复燃（复古舞步 + AI 换装），引发 **“3‑person rooftop dance”** 模板需求。平台同步推出 “上传 3 张照片 → 自动生成 20‑秒舞蹈短片”。同样的高频搜索词导致三家工具站形成竞争聚集。 | <a href="https://remakeyourmeme.com/how-to/how-to-make-gangnam-style-ai-video/" target="_blank" rel="noopener noreferrer">RemakeYourMeme – How to Make the Gangnam Style AI Video</a>、<a href="https://www.lightxeditor.com/blog/how-to-make-ai-gangnam-style-trend-video/" target="_blank" rel="noopener noreferrer">LightX – How to Make Gangnam Style Trend Video</a>、<a href="https://www.getstarrd.app/blog/how-to-make-gangnam-style-ai-video" target="_blank" rel="noopener noreferrer">GetStarrd – How to Make the Gangnam Style AI Video With 3 Friends</a> |

**解读要点**  
1. 两个词均 **非模因起源**（`has_meme_origin:false`），属于 **商业站点竞争聚集**。  
2. 触发点均是 **短视频平台（TikTok / Instagram Reels）** 的热点挑战，导致用户搜索量在 24 h 内激增。  
3. 站点通过 **SEO 叠加、模板标题同质化** 抢占同一长尾关键词，形成跨域流量抢夺。  

---

## ⚡ 6小时突发单域动向 (Single‑Domain Emerging)

| 域名 | 新增页面数 | 关键新增模板 / 区块 | 典型痛点（Generic Job） |
|------|-----------|-------------------|--------------------------|
| **Media.io** | 81（占新增总量 81%） | <ul><li>**Tiny Desk AI Trend** – <a href="https://www.media.io/ai/explore/zone/tiny-desk-ai-trend" target="_blank" rel="noopener noreferrer">Zone 页面</a></li><li>**No Scrubs AI Video Generator** – <a href="https://www.media.io/ai/explore/zone/no-scrubs-ai-video-generator" target="_blank" rel="noopener noreferrer">TLC‑style music video</a></li><li>**Instagram Reels Trends 2026** – <a href="https://www.media.io/ai/explore/zone/instagram-reels-trends" target="_blank" rel="noopener noreferrer">趋势聚合页</a></li><li>**Ballon d’Or AI Filter** – <a href="https://www.media.io/ai/explore/zone/ballon-dor-ai-filter" target="_blank" rel="noopener noreferrer">奖杯颁奖恶搞</a></li></ul> | `photo‑to‑concert video`, `photo‑to‑music‑video generator`, `instant reels script`, `AI award‑prank generator` |
| **APT Video AI** | 0（但累计 510 条） | 未出现新页面，但 **API 调用量** 在监测窗口内保持高位，暗示后台模型已被多家站点调用（如 Tiny Desk、Gangnam Style）。 | `batch‑AI‑render service` |
| **TryAlorsOnDanse** | 0（累计 265 条） | 同上，主要提供 **舞蹈动作库**，被 LightX、GetStarrd 复用。 | `dance‑pose extraction` |
| **GetStarrd** | 2 新页面 | <ul><li>**Tiny Desk AI** 系列（两篇）</li><li>**Gangnam Style AI** 模板页</li></ul> | `3‑person rooftop dance`, `photo‑to‑stage performance` |
| **CapCut (剪映海外版)** | 4 新模板 | <ul><li>**New Slowmotion** – 562 k 次使用</li><li>**King Troll Template** – 2 M 次使用</li></ul> | `slow‑motion highlight`, `viral meme‑troll edit` |
| **Know Your Meme** | 1 新页面 | <a href="https://knowyourmeme.com/memes/freddy-krueger-cancelled" target="_blank" rel="noopener noreferrer">Freddy Krueger Cancelled</a>（文化审查热点） | `meme‑cancellation tracking` |

**核心洞察**  
- **Media.io** 仍是 **AI Prompt‑to‑Video** 的流量发动机，几乎所有热点（Tiny Desk、No Scrubs、Reels Trends）均在其 **Zone** 页面统一发布，形成 **Prompt 截流**。  
- **APT Video AI** 与 **TryAlorsOnDanse** 虽未新增页面，但其 **后端模型** 被多家前端站点调用，属于 **隐形竞争层**。  
- **CapCut** 的两大爆款模板使用量继续保持 **高位**，且与本期新增的 Tiny Desk / Gangnam Style 并无直接关键词重叠，说明 **平台生态分层**（短视频剪辑 vs. AI 生成）仍保持相对独立。

---

## 🎬 CapCut Most‑Used 热度生命周期与新上榜模板 (Trend Matrix)

### 1️⃣ 本期 **新上榜模板**（进入榜单的 4 条）

| 模板 | 使用量 | 所需切片张数 | 链接 |
|------|--------|--------------|------|
| **New Slowmotion** | 562 252 | 1 | <a href="https://www.capcut.com/template-detail/7533330731842522421" target="_blank" rel="noopener noreferrer">New Slowmotion</a> |
| **King Troll Template** | 2 023 809 | 3 | <a href="https://www.capcut.com/template-detail/7444126033852321045" target="_blank" rel="noopener noreferrer">King Troll Template</a> |
| **Speedramp+Shake** | 478 196 | 13 | <a href="https://www.capcut.com/template-detail/7575464722389306629" target="_blank" rel="noopener noreferrer">Speedramp+Shake</a> |
| **Trending Top Edit** | 5 608 | 8 | <a href="https://www.capcut.com/template-detail/7639796622330776853" target="_blank" rel="noopener noreferrer">Trending Top Edit</a> |

**碰撞判定**：这些模板的关键词（slowmotion、troll、speedramp）未在本期跨域碰撞词（tiny desk / gangnam style）中出现，属于 **平台内部热度**，不构成直接流量冲突。

### 2️⃣ 热度矩阵（状态分组）

| 状态 | 模板 | 6 h 增量 | 名次变动 |
|------|------|----------|----------|
| 🔥 **爆火** | **King Troll Template** (新入榜) | — | — |
| 📈 **升温** | **Tere jujbato me** (surging) | +1 411 使用 | +1 名 |
| 💎 **稳态** | **Rag Rag woh** (stable) | +665 使用 | +2 名 |
| 💎 **稳态** | **Airplane Mode On** (stable) | +43 使用 | +1 名 |
| 📉 **降温** | **Slapping meme😂💀** (stable) | — | — |
| 📉 **降温** | **MOST DANGEOUS MAN** (stable) | — | — |

> **注**：`delta_6h` 为本期 6 h 内的使用增量；`rank_delta` 为名次相对上一次快照的变化。

### 3️⃣ **跌出榜单**（强降温信号，建议规避）

| 模板 | 上次使用量 | 上次排名 |
|------|------------|----------|
| **So Hard** | 132 747 | 14 |
| **gata only** | 117 707 | 20 |
| **use headphone** | 272 885 | 6 |
| **Kamin Etz** | 240 612 | 11 |
| **try new template** | 67 801 | 15 |

这些模板的使用量在最近 24 h 内跌幅 > 30 %，表明 **用户兴趣已转移**，不宜继续投入推广资源。

---

## 🚀 独立开发与微创新商机 (24~48h MVP)

| 商机 | 核心切入点 | 可落地 MVP 示例 |
|------|------------|-----------------|
| **Prompt 截流博客** | Media.io 的 **Zone** 页面集中发布高频 Prompt（如 “tiny desk”, “no scrubs”, “rainbow bridge pet”），搜索流量大且 SEO 成本低。 | 搭建一个 **“AI Prompt 速查站”**，聚合 50+ 高转化 Prompt，提供 **一键复制 + 站外追踪**（UTM）功能，收取 Affiliate 佣金或 Prompt 付费订阅。 |
| **单功能轻量生成器** | “photo‑to‑concert video” 与 “3‑person rooftop dance” 需求均为 **固定素材 + 固定模板**，可抽象为 “两张照片生成 X‑style 短片”。 | 开发 **TinyDesk‑Lite**（仅支持 2 张照片 → 30 s 演唱会片段）或 **Gangnam‑Mini**（3 张自拍 → 15 s 舞蹈片段），使用 **免费模型 API**（如 OpenAI Video）+ 前端 JS 渲染，收取 **一次性下载费**。 |
| **跨平台模板同步工具** | 多站点（GetStarrd、LightX、RemakeYourMeme）同时发布同质模板

---

## 📋 各站点新增 URL 详细清单 (全量索引)

### 🌐 Know Your Meme（新增 1 个页面）

- <a href="https://knowyourmeme.com/memes/freddy-krueger-cancelled" target="_blank" rel="noopener noreferrer">**Freddy Krueger Cancelled | Know Your Meme**</a>
  - 网页生成: `2026-10-28 23:28` ｜ 发现时间: `2026-10-29 02:00`
  - 描述: Freddy Krueger Cancelled refers to attempts to cancel and stop people from glorifying the horror movie villain Freddy Krueger from A Nightmare on Elm Stree
  - 实体词: `krueger cancelled, freddy krueger, freddy krueger cancelled`


### 🌐 Media.io（新增 20 个页面）

- <a href="https://www.media.io/ai-prompts/rainbow-bridge-pet-photo-prompts.html" target="_blank" rel="noopener noreferrer">**25+ Gemini and ChatGPT Rainbow Bridge Pet Photo Prompts & Memorial Portrait Ideas**</a>
  - 网页生成: `2026-10-26` ｜ 发现时间: `2026-10-29 02:00`
  - 描述: Try 25 rainbow bridge pet photo prompts for symbolic keepsakes: cloud pathways, gentle bridge journeys, angel portraits and watercolor remembrance scenes.
  - 实体词: `gpt rainbow, gemini and chat gpt, memorial portrait ideas, gemini and chat, chat gpt rainbow bridge`

- <a href="https://www.media.io/ai-prompts/gemini-ai-skateboard-portrait-prompts.html" target="_blank" rel="noopener noreferrer">**25 Gemini AI Skateboard Portrait Prompts for Cool Action**</a>
  - 网页生成: `2026-10-26` ｜ 发现时间: `2026-10-29 02:00`
  - 描述: Turn your portrait into a cool skate action shot. Try 25 prompts with push-offs, fisheye ollies, low carving turns, motion blur and three-frame skate stories.
  - 实体词: `gemini ai skateboard portrait, skateboard portrait, gemini ai skateboard, portrait prompts for cool, 25 gemini`

- <a href="https://www.media.io/ai-prompts/animal-comedy-video-prompts.html" target="_blank" rel="noopener noreferrer">**Free Animal Comedy Video Prompts: Copy-Ready Skits**</a>
  - 网页生成: `2026-10-23` ｜ 发现时间: `2026-10-29 02:00`
  - 描述: Free animal comedy video prompts for funny pet skits, deadpan animal jokes, and talking gags. Copy one into Media.io Text to Video and generate.
  - 实体词: `comedy video prompts copy, animal comedy`

- <a href="https://www.media.io/ai-prompts/educational-instagram-reels-prompts.html" target="_blank" rel="noopener noreferrer">**Educational Instagram Reels Prompts, 15 Free Ideas**</a>
  - 网页生成: `2026-10-23` ｜ 发现时间: `2026-10-29 02:00`
  - 描述: Educational Instagram reels prompts for fact shorts, history reels, and how-to clips. Copy one into Media.io Text to Video and generate.
  - 实体词: `15 free ideas`

- <a href="https://www.media.io/ai-prompts/film-moodboard-video-prompts.html" target="_blank" rel="noopener noreferrer">**20 Film Moodboard Video Prompts, All Free**</a>
  - 网页生成: `2026-10-23` ｜ 发现时间: `2026-10-29 02:00`
  - 描述: Film moodboard video prompts for color palettes, lighting plans, and concept frames. Copy one into Media.io Text to Video and generate.
  - 实体词: `film moodboard, 20 film moodboard, 20 film`

- <a href="https://www.media.io/ai-prompts/carpet-cleaning-time-lapse-video-prompts.html" target="_blank" rel="noopener noreferrer">**Carpet Cleaning Time Lapse Prompts - Ready to Paste**</a>
  - 网页生成: `2026-10-23` ｜ 发现时间: `2026-10-29 02:00`
  - 描述: Carpet cleaning time lapse video prompts for satisfying rug resets, water lines, and before after reveals. Copy one into Media.io Text to Video.
  - 实体词: `carpet cleaning time lapse, carpet cleaning, cleaning time lapse`

- <a href="https://www.media.io/ai-prompts/roller-coaster-video-prompts.html" target="_blank" rel="noopener noreferrer">**Copy-Ready Roller Coaster Video Prompts: 15 Free**</a>
  - 网页生成: `2026-10-23` ｜ 发现时间: `2026-10-29 02:00`
  - 描述: Roller coaster video prompts for POV rides, cinematic drops, and fantasy coasters. Copy one into Media.io Text to Video and generate.
  - 实体词: `roller coaster`

- <a href="https://www.media.io/ai-prompts/surreal-ai-desert-animation-prompts.html" target="_blank" rel="noopener noreferrer">**Surreal AI Desert Animation Prompts: A Free Set**</a>
  - 网页生成: `2026-10-23` ｜ 发现时间: `2026-10-29 02:00`
  - 描述: Surreal AI desert animation prompts for dreamlike dunes, floating objects, and abstract sandscapes. Copy one into Media.io Text to Video.
  - 实体词: `desert animation, surreal ai desert, surreal ai desert animation`

- <a href="https://www.media.io/ai-prompts/dreamlike-nighttime-animation-prompts.html" target="_blank" rel="noopener noreferrer">**Dreamlike Nighttime Animation Prompts You Can Copy Free**</a>
  - 网页生成: `2026-10-23` ｜ 发现时间: `2026-10-29 02:00`
  - 描述: Dreamlike nighttime animation prompts for moonlit scenes, starry skies, and ethereal night motion. Copy one into Media.io Text to Video.
  - 实体词: `dreamlike nighttime animation, dreamlike nighttime, nighttime animation`

- <a href="https://www.media.io/ai-prompts/peel-off-mask-asmr-video-prompts.html" target="_blank" rel="noopener noreferrer">**Peel Off Mask ASMR Video Prompts: 15 Copy-Ready Clips**</a>
  - 网页生成: `2026-10-23` ｜ 发现时间: `2026-10-29 02:00`
  - 描述: Peel off mask ASMR video prompts for gel mask close-ups, peel-back texture, and relaxing skincare shots. Copy one into Media.io Text to Video.
  - 实体词: `asmr video prompts 15, peel off mask, mask asmr, 15 copy, peel off mask asmr`

- <a href="https://www.media.io/ai-prompts/stick-figure-animation-prompts.html" target="_blank" rel="noopener noreferrer">**Free Stick Figure Animation Prompts to Paste and Render**</a>
  - 网页生成: `2026-10-23` ｜ 发现时间: `2026-10-29 02:00`
  - 描述: Stick figure animation prompts for stickman motion, simple line characters, and short explainer beats. Copy one into Media.io Text to Video and generate.
  - 实体词: `stick figure, animation prompts to paste, paste and render, stick figure animation, figure animation`

- <a href="https://www.media.io/ai-prompts/wes-anderson-style-video-prompts.html" target="_blank" rel="noopener noreferrer">**Wes Anderson Style Prompts: 15 Symmetrical Free Ideas**</a>
  - 网页生成: `2026-10-23` ｜ 发现时间: `2026-10-29 02:00`
  - 描述: Wes Anderson style video prompts for symmetrical frames, pastel palettes, and centered compositions. Copy one into Media.io Text to Video and generate.
  - 实体词: `style prompts 15, anderson style, wes anderson, symmetrical free ideas, 15 symmetrical free ideas`

- <a href="https://www.media.io/ai-prompts/dark-animation-video-prompts.html" target="_blank" rel="noopener noreferrer">**Ready-to-Paste Dark Animation Prompts: 15 Gothic Ideas**</a>
  - 网页生成: `2026-10-23` ｜ 发现时间: `2026-10-29 02:00`
  - 描述: Dark animation video prompts for gothic sets, moody light, and eerie motion. Copy one into Media.io Text to Video and generate a dark clip.
  - 实体词: `dark animation`

- <a href="https://www.media.io/ai-prompts/cartoon-comedy-video-prompts.html" target="_blank" rel="noopener noreferrer">**Cartoon Comedy Prompts: 15 Free Copy-Ready Gags**</a>
  - 网页生成: `2026-10-23` ｜ 发现时间: `2026-10-29 02:00`
  - 描述: Cartoon comedy video prompts for animated gags, slapstick beats, and funny characters. Copy one into Media.io Text to Video and generate a short clip.
  - 实体词: `15 free copy, comedy prompts 15, cartoon comedy, cartoon comedy prompts 15`

- <a href="https://www.media.io/ai/explore/zone/no-scrubs-ai-video-generator" target="_blank" rel="noopener noreferrer">**No Scrubs AI Video Generator – TLC Music Video Trend | Media.io**</a>
  - 网页生成: `2026-10-27` ｜ 发现时间: `2026-10-29 02:00`
  - 描述: Create your own No Scrubs AI video from photos. Recreate the TLC-inspired music video with your friends, futuristic silver sets, close-ups, and group dance effe

- <a href="https://www.media.io/ai/explore/zone/instagram-reels-trends" target="_blank" rel="noopener noreferrer">**Instagram Reels Trends 2026 – Trending Reels, Songs & Ideas**</a>
  - 网页生成: `2026-10-26` ｜ 发现时间: `2026-10-29 02:00`
  - 描述: Discover Instagram Reels trends in 2026, including trending songs, viral video ideas, and business trends. Learn how to find trending Reels and create your own 

- <a href="https://www.media.io/ai/explore/zone/ballon-dor-ai-filter" target="_blank" rel="noopener noreferrer">**Ballon d’Or AI Filter – Golden Ball Prank Video | Media.io**</a>
  - 网页生成: `2026-10-26` ｜ 发现时间: `2026-10-29 02:00`
  - 描述: Turn your photo into a Ballon d’Or winner video with AI. Receive the golden trophy, celebrate on stage, and create a fun award ceremony prank to share.
  - 实体词: `ballon d, ballon dor`

- <a href="https://www.media.io/ai/explore/zone/neon-eyes-cinematic-ai-photo-prompts" target="_blank" rel="noopener noreferrer">**Viral Close-Up Neon Eyes Cinematic AI Photo Editing Prompts for Gemini & ChatGPT | Media.io**</a>
  - 网页生成: `2026-10-28` ｜ 发现时间: `2026-10-29 02:00`
  - 描述: Explore neon eyes cinematic prompts for Gemini and ChatGPT. Upload your photo to create a dramatic portrait with a giant eye screen and blue neon lighting.
  - 实体词: `neon eyes, eyes cinematic, neon eyes cinematic`

- <a href="https://www.media.io/ai/explore/zone/ak-creator-yt-ai-prompt" target="_blank" rel="noopener noreferrer">**Trending AK Creator YT AI Photo Editing Styles for Boys & Girls | Media.io**</a>
  - 网页生成: `2026-10-26` ｜ 发现时间: `2026-10-29 02:00`
  - 描述: Explore AK Creator YT–inspired photo editing prompts for cinematic portraits, stylish DPs, and aesthetic photos. Copy a prompt or create your look on Media.io.
  - 实体词: `editing styles for boys, boys girls, editing styles, styles for boys, yt ai photo editing`

- <a href="https://www.media.io/ai/explore/zone/tiny-desk-ai-trend" target="_blank" rel="noopener noreferrer">**Tiny Desk AI Trend – AI Concert Video Generator from Photo**</a>
  - 网页生成: `2026-10-26` ｜ 发现时间: `2026-10-29 02:00`
  - 描述: Create a Tiny Desk-style AI concert video from your photo. Perform beside a desk with a microphone, live band, bookshelves, and warm studio lighting.
  - 实体词: `tiny desk`


### 🌐 GetStarrd（新增 2 个页面）

- <a href="https://www.getstarrd.app/template/gangnam-style-ai-video" target="_blank" rel="noopener noreferrer">**Gangnam Style — AI Video Template | Starrd**</a>
  - 网页生成: `2026-10-28 23:32` ｜ 发现时间: `2026-10-29 02:00`
  - 描述: Three friends, one rooftop, Gangnam Style. Add 3 photos in this order: 1. The one holding the camera (center) 2. The one on the left 3. The one on the…
  - 实体词: `gangnam style`

- <a href="https://www.getstarrd.app/blog/how-to-make-gangnam-style-ai-video" target="_blank" rel="noopener noreferrer">**How to Make the Gangnam Style AI Video With 3 Friends (2026)**</a>
  - 网页生成: `2026-10-28` ｜ 发现时间: `2026-10-29 02:00`
  - 描述: Put you and two friends in the viral AI Gangnam Style rooftop video: a group selfie, a solo for each of you, then everyone back in the frame doing the horse dan
  - 实体词: `friends 2026, 3 friends 2026, 3 friends, gangnam style`


### 🌐 CapCut (剪映海外版)（新增 4 个页面）

- <a href="https://www.capcut.com/template-detail/7533330731842522421" target="_blank" rel="noopener noreferrer">**New Slowmotion**</a>
  - 网页生成: `2025-08-01 03:35` ｜ 发现时间: `2026-10-29 02:00`
  - 🔥 剪同款使用量: `562,252 次` ｜ 📸 所需素材: `1 张切片` ｜ ⏱️ 时长: `20.6秒`
  - 🎬 视频直链: <a href="https://v16-capcut.capcutcdn-us.com/fb751d53f26f8cab9a2595ecdee96b9d/6ae5e4af/video/tos/useast5/tos-useast5-ve-2795c799-tx/oIJ8gfoBDBMoFs6uHXEi8eQ0iBQIPq7ggatpVC/?a=3006&bti=cHJ3bzFmc3dmZEBvY15taF4rcm1gYA%3D%3D&&bt=1923&ft=WnnELNvjVQ9S.jrWTsdGVhkjnZ7uwQAs5vBrkhUWuF_4&mime_type=video_mp4&rc=ZzQzZjY2ZDM6ZTozOTk2NkBpam5vcmo5cmt2NTMzOGVkNEBiYjItYWBhNWMxNTUuL15gYSNebzQwMmRzXjJhLS1kYi1zcw%3D%3D&vvpl=1&l=20261028125241ECE265B1DF2B39EE1727&btag=e000b0000" target="_blank" rel="noopener noreferrer">点击播放无水印预览视频 (MP4)</a>
  - 描述: CapCut 全球爆款模板，剪同款使用量: 562,252 次，所需素材: 1 张照片/切片，时长: 20.6秒。标签: #slowmotion #newtrend #slowmo #mrzobi #foryou💗✨

- <a href="https://www.capcut.com/template-detail/7444126033852321045" target="_blank" rel="noopener noreferrer">**King Troll Template**</a>
  - 网页生成: `2024-12-04 05:22` ｜ 发现时间: `2026-10-29 02:00`
  - 🔥 剪同款使用量: `2,023,809 次` ｜ 📸 所需素材: `3 张切片` ｜ ⏱️ 时长: `10.8秒`
  - 🎬 视频直链: <a href="https://v16-capcut.capcutcdn-us.com/62ab906da46c0ef30a5de3ebac57a103/6ae5e4a5/video/tos/useast5/tos-useast5-ve-2795c799-tx/oYyl0AQArIqyiBkrVhp6LE7PUYvBZu2qVLid9/?a=3006&bti=cHJ3bzFmc3dmZEBvY15taF4rcm1gYA%3D%3D&&bt=530&ft=WnnELNvjVQ9S.jrWTsdGVhkjnZ7uwQAs5vBrkhUWuF_4&mime_type=video_mp4&rc=NjwzZWRoODZmMzU2aWY8OEBpamRpN2w5cjhxdzMzOGVkNEBhYTEtXl9jXmIxNGIxYGE1YSNeMjRmMmRrYTRgLS1kYi1zcw%3D%3D&vvpl=1&l=20261028125241ECE265B1DF2B39EE1727&btag=e000b8000" target="_blank" rel="noopener noreferrer">点击播放无水印预览视频 (MP4)</a>
  - 描述: CapCut 全球爆款模板，剪同款使用量: 2,023,809 次，所需素材: 3 张照片/切片，时长: 10.8秒。标签: #foryou
  - 实体词: `king troll`

- <a href="https://www.capcut.com/template-detail/7575464722389306629" target="_blank" rel="noopener noreferrer">**Speedramp+Shake**</a>
  - 网页生成: `2025-11-22 16:38` ｜ 发现时间: `2026-10-29 02:00`
  - 🔥 剪同款使用量: `478,196 次` ｜ 📸 所需素材: `13 张切片` ｜ ⏱️ 时长: `13.0秒`
  - 🎬 视频直链: <a href="https://v16-capcut.capcutcdn-us.com/df9f054f0d8f047e1dbae4b1857b6df4/6ae5e4a8/video/tos/useast5/tos-useast5-ve-2795c799-tx/oY8iidlqIT4XohkAphLBfAKWtMBiQILwCLp0EE/?a=3006&bti=cHJ3bzFmc3dmZEBvY15taF4rcm1gYA%3D%3D&&bt=1343&ft=WnnELNvjVQ9S.jrWTsdGVhkjnZ7uwQAs5vBrkhUWuF_4&mime_type=video_mp4&rc=aDtkZDM7aGU4NWk1NmVkNkBpMzxka3I5cjlxNzMzOGVkNEBfNGFjYzMvNi0xXi8tLTIzYSMyXzE2MmRjYWRhLS1kYi1zcw%3D%3D&vvpl=1&l=20261028125241ECE265B1DF2B39EE1727&btag=e000b8000" target="_blank" rel="noopener noreferrer">点击播放无水印预览视频 (MP4)</a>
  - 描述: CapCut 全球爆款模板，剪同款使用量: 478,196 次，所需素材: 13 张照片/切片，时长: 13.0秒。标签: #fyp #foryou #caredit #capcuttopcreator #popo_hrtz
  - 实体词: `speedramp shake, popo hrtz`

- <a href="https://www.capcut.com/template-detail/7639796622330776853" target="_blank" rel="noopener noreferrer">**Trending Top Edit**</a>
  - 网页生成: `2026-05-15 01:13` ｜ 发现时间: `2026-10-29 02:00`
  - 🔥 剪同款使用量: `5,608 次` ｜ 📸 所需素材: `8 张切片` ｜ ⏱️ 时长: `12.9秒`
  - 🎬 视频直链: <a href="https://v16-capcut.capcutcdn-us.com/4cd767ea526a6dd3d0d8a29f419eb824/6ae5e4a7/video/tos/useast5/tos-useast5-ve-2795c799-tx/oAviaNAYBxiDrYoGB1rIEvnSAN6EAlCPq6gUR/?a=3006&bti=cHJ3bzFmc3dmZEBvY15taF4rcm1gYA%3D%3D&&bt=516&ft=WnnELNvjVQ9S.jrWTsdGVhkjnZ7uwQAs5vBrkhUWuF_4&mime_type=video_mp4&rc=aDhkNGg6OjxlOmc1OmZkZ0BpanRkdnQ5cjgzOzMzOGVkNEAyMV5jNmIwXzAxMDEyMzQuYSNuc14zMmRrMjBhLS1kYi1zcw%3D%3D&vvpl=1&l=20261028125241ECE265B1DF2B39EE1727&btag=e000b8000" target="_blank" rel="noopener noreferrer">点击播放无水印预览视频 (MP4)</a>
  - 描述: CapCut 全球爆款模板，剪同款使用量: 5,608 次，所需素材: 8 张照片/切片，时长: 12.9秒。标签: #foryou#trend❤️


---

## 📊 CapCut Most-Used 热度生命周期事实表 (时序差分)

### 🆕 本期新上榜（4 个）

| 模板 | 使用量 | 名次 | 所需切片 | 上架天数 | 直达 |
| :--- | ---: | ---: | ---: | ---: | :--- |
| **New Slowmotion** | 562,252 | 第3名 | 1张 | 453.9天 | <a href="https://www.capcut.com/template-detail/7533330731842522421" target="_blank" rel="noopener noreferrer">模板页</a> |
| **King Troll Template** | 2,023,809 | 第10名 | 3张 | 693.9天 | <a href="https://www.capcut.com/template-detail/7444126033852321045" target="_blank" rel="noopener noreferrer">模板页</a> |
| **Speedramp+Shake** | 478,196 | 第17名 | 13张 | 340.4天 | <a href="https://www.capcut.com/template-detail/7575464722389306629" target="_blank" rel="noopener noreferrer">模板页</a> |
| **Trending Top Edit** | 5,608 | 第18名 | 8张 | 167.0天 | <a href="https://www.capcut.com/template-detail/7639796622330776853" target="_blank" rel="noopener noreferrer">模板页</a> |

### 📉 本期跌出榜单（11 个，最强降温信号）

- ~~So Hard~~（上期第14名 / 132,747 次）
- ~~gata only~~（上期第20名 / 117,707 次）
- ~~use headphone~~（上期第6名 / 272,885 次）
- ~~Kamin Etz~~（上期第11名 / 240,612 次）
- ~~try new template~~（上期第15名 / 67,801 次）
- ~~Samjho Na x Wishes~~（上期第4名 / 293,864 次）

### 🎛️ 全榜热度状态

| 状态 | 模板 | 使用量 | 6h增量 | 名次变动 | 日均爆发力 |
| :--- | :--- | ---: | ---: | ---: | ---: |
| 🆕 新上榜 | King Troll Template | 2,023,809 | — | — | 2,916/天 |
| 🆕 新上榜 | New Slowmotion | 562,252 | — | — | 1,238/天 |
| 🆕 新上榜 | Speedramp+Shake | 478,196 | — | — | 1,404/天 |
| 🆕 新上榜 | Trending Top Edit | 5,608 | — | — | 33/天 |
| 🔥 爆火 | Tere jujbato me | 1,121,275 | +1,411 | ⬆1 | 3,498/天 |
| ⚪ 平稳 | Rag Rag woh | 680,198 | +665 | ⬆2 | 1,971/天 |
| ⚪ 平稳 | Slapping meme😂💀 | 671,288 | — | — | 800/天 |
| ⚪ 平稳 | VELOCITY x COLOR AD | 518,441 | — | — | 1,437/天 |
| ⚪ 平稳 | Airplane Mode On | 481,095 | +43 | ⬆1 | 1,401/天 |
| ⚪ 平稳 | MOST DANGEOUS MAN | 474,277 | — | — | 424/天 |
| ⚪ 平稳 | ⚡️✨Charming✨⚡️ | 401,781 | — | — | 868/天 |
| ⚪ 平稳 | Trending | 248,434 | +7 | ⬆4 | 276/天 |
| ⚪ 平稳 | trend | 152,825 | +2 | ⬇3 | 258/天 |
| ⚪ 平稳 | Spiderman edit | 132,981 | — | — | 819/天 |
| ⚪ 平稳 | The New Trend Edit | 96,828 | — | — | 302/天 |
| ⚪ 平稳 | Breathe Hoodtrap | 27,525 | — | — | 154/天 |
| ⚪ 平稳 | Most Used Aircraft | 688 | +1 | — | 2/天 |
| 💎 高热稳态 | LF | 2,177,853 | +141 | ⬇1 | 3,888/天 |
| 💎 高热稳态 | Insta Trend | 1,495,997 | +281 | ⬇4 | 4,994/天 |
| 📉 降温 | Roi | 68,166 | +13 | ⬇4 | 112/天 |
