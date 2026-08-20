---
name: video-to-document
description: 把在线视频（如 B 站）转成整理好的文档版：下载音频 → 本地语音转写 → 校对整理为 Markdown/Word 文档 + 逐字稿。适用于无官方字幕、或用户要求"把视频转成文档/逐字稿/文字版/笔记"的场景。
---

# Video To Document

把一段在线视频变成可读的文档版。目标产物：
- 整理版文档：Markdown（主）+ Word（docx，用 python-docx 渲染）
- 完整逐字稿 txt（语音转写原文）
- 均保存到项目 outputs 目录，回复时给出绝对路径链接。

## 工作流

### 1. 获取视频信息与字幕
用 B 站 API（Python urllib，必须带 UA + Referer 头）：
- https://api.bilibili.com/x/web-interface/view?bvid=<BV号> → data.title、data.duration、data.cid、data.owner、data.stat
- https://api.bilibili.com/x/player/v2?bvid=<BV号>&cid=<cid> → data.subtitle.subtitles（官方/AI 字幕列表）
若有字幕（subtitles 非空），直接下载字幕 JSON 整理，跳过第 2-4 步。
B 站 AI 总结接口（iew/conclusion/get）游客访问返回 403，不要依赖。

### 2. 下载音频
- https://api.bilibili.com/x/player/playurl?bvid=<BV号>&cid=<cid>&qn=0&fnval=16&fnver=0&fourk=1
- 取 data.dash.audio 中带宽最大的 aseUrl（m4s），用 urllib 下载到 outputs/_tmp/audio.m4s
- 优先用 scripts/fetch_bilibili.py <BV号> --out outputs/_tmp

### 3. 转 wav
用 Python + PyAV（av 包）：把 m4s 解码为 16kHz 单声道 s16 PCM wav：
out.add_stream("pcm_s16le", rate=16000, layout="mono")，逐帧 ncode/mux。
（2h20m 视频约产生 270MB wav，属正常。）

### 4. 语音转写：用 whisper.cpp，不要用 faster-whisper
- **faster-whisper/ctranslate2 在 Codex Windows 沙箱内加载模型会空指针崩溃并弹 Windows 错误框，不要用。**
- 用 whisper.cpp 独立 exe：
  - 下载 GitHub release（ggml-org/whisper.cpp）的 whisper-bin-x64.zip，解压后 Release/whisper-cli.exe
  - 模型：中文推荐 ggml-small.bin（约 488MB），从 https://hf-mirror.com/ggerganov/whisper.cpp/resolve/main/ 下载
  - 转写命令（需在 Release 目录运行，DLL 相对路径）：
    whisper-cli.exe -m <ggml-small.bin> -f <audio.wav> -l zh -t 16 -bs 3 -otxt -oj -of <out_prefix>
  - 产物：<prefix>.txt（带时间戳逐句）和 <prefix>.json（	ranscription 数组，含 offsets.from/to 毫秒与 	ext）
  - 也可用 scripts/transcribe_whisper.py 封装此调用。

### 5. 整理成文档
- 读 JSON，把相邻短句（间隔 <3s）合并成段落，按 20-30 分钟音频一批分批通读全文
- 按主题组织文档：视频信息、一句话速览、核心观点、逐段详解（标注时间点）、关键数据/金句表、观众反响（如有）、说明与免责
- 用 scripts/md_to_docx.py 把 Markdown 渲染成 Word（标题/段落/列表/表格/粗体）
- 逐字稿 txt 一并放入 outputs

## 环境要点（易踩坑，务必遵守）
- 沙箱默认只读/断网：动手前先 
equest_permissions 申请 network + 写 outputs 目录；权限是 turn 级，必要时每个 turn 重新申请
- 写文件用 Python（open/shutil），不要用复杂 PowerShell（可能触发沙箱拒绝）
- Python 输出前设置 PYTHONIOENCODING=utf-8，否则中文乱码
- 国内网络：PyPI 用 -i https://pypi.tuna.tsinghua.edu.cn/simple；HuggingFace 用 HF_ENDPOINT=https://hf-mirror.com 且 HF_HUB_DISABLE_XET=1；GitHub 直连通常可用
- Python site-packages（av 等二进制包）在沙箱内跨命令可能失效（import 成空包/权限拒绝）；关键链路尽量一个 exec 内完成，或优先独立 exe
- 长视频：whisper-cli small 16 线程约 5 倍实时（2h 视频约 25-30 分钟）；不要默认 32 线程吃满机器
- 语音转写有同音字错别字，整理文档时按上下文修正；不确定的公司名/人名/数字标注"转录可能有误"
- 视频末尾可能含商业推广，整理时如实标注但不下结论
