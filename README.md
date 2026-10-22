# 浙大课程笔记 Skill

帮助浙江大学同学逐节整理课程课件和字幕。每节课单独处理，重点清晰、公式规范、代码有语法高亮；复杂图示只在能够准确还原时重绘。

## 两种方式任选

### 1. 生成 ZIP，手动上传给网页版 ChatGPT

适合希望自己在 ChatGPT 网页中提交材料并检查笔记的同学。把同一节课的课件、字幕放进一个本地文件夹，然后运行：

```bash
python scripts/package_lesson.py --course "课程名" --date 2026-10-22 --lesson "第3-4节" --materials-dir "./materials/lesson-03" --output-dir "./packages"
```

脚本会生成单课 ZIP，里面有已填好的 `prompt.md` 和 `materials/`。PPT/PPTX/PDF 不设大小上限；视频、安装包、常见凭据文件和隐藏目录默认跳过，并在终端报告。检查 ZIP 后，将这一节的 ZIP 手动上传给网页版 ChatGPT，再处理下一节。

### 2. 让 Codex 直接解析并整理到 Notion

适合希望 Codex 读取本地课件和字幕、生成笔记并写入 Notion 的同学。选择此方式后，Codex 会逐节处理，并使用已连接的 Notion 工具查找、创建或更新页面。Codex 与网页版 ChatGPT 在 Notion 上的操作范围一致，前提是连接到相同工作区并具备相同权限。页面归属不清时会先报告并请求指定位置，避免误写或重复。

两种方式都遵循本技能的笔记格式标准。Codex 模式不需要先生成 ZIP，也不会自动操作网页版 ChatGPT。

## 安装

把本仓库克隆或下载到 Codex skills 目录：

```text
~/.codex/skills/zju-course-notes/
```

Windows 默认位置通常是：

```text
%USERPROFILE%\.codex\skills\zju-course-notes\
```

新开 Codex 任务后，可直接说“用 zju-course-notes 整理这节课”，并说明选择 ZIP 手动上传，还是 Codex 写入 Notion。

## 权限与隐私

本仓库不包含任何学生的课件、字幕、课程清单、笔记或账号配置。Skill 遵守课程平台的下载权限；不会使用私有接口、预览地址、Cookie 或浏览器自动化绕过拒绝下载的设置。不会下载视频、安装包或软件，除非学生明确要求。
