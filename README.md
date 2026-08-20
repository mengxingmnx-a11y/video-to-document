# video-to-document

把在线视频（B 站等）转成整理好的文档版的 **Codex Skill**：下载音频 → 本地语音转写（whisper.cpp）→ 校对整理为 Markdown / Word 文档 + 逐字稿。

适用于：无官方字幕的视频、需要逐字稿/文字版/笔记的场景。

## 安装

把本仓库内容放到 ~/.codex/skills/video-to-document/（Windows 为 C:\\Users\\<你>\\.codex\\skills\\video-to-document\\），重启 Codex 即可自动发现。

## 使用

直接对 Codex 说：“把这个视频转成文档版”并附上视频链接/BV 号。

## 内容

- SKILL.md — 工作流指令（含国内网络镜像、沙箱权限、whisper.cpp 等踩坑经验）
- scripts/fetch_bilibili.py — 获取 B 站视频信息/字幕 + 下载音频
- scripts/transcribe_whisper.py — 封装 whisper.cpp 转写调用
- scripts/md_to_docx.py — Markdown → Word 转换

## 说明

- 语音转写可能存在同音字误差，整理时按上下文修正。
- 视频中的商业推广内容会如实标注。
