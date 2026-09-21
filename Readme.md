# 🎮 Gaming4free 自动续期机器人

[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Automated-blue?logo=githubactions)](https://github.com/features/actions)
[![Python](https://img.shields.io/badge/Python-3.10-green?logo=python)](https://www.python.org/)
[![SeleniumBase](https://img.shields.io/badge/SeleniumBase-UC%20Mode-orange)](https://github.com/seleniumbase/SeleniumBase)

基于 **GitHub Actions + SeleniumBase + Xray Proxy** 开发的 Gaming4free 免费服务器自动续期脚本。自动模拟浏览器点击续期、绕过人机验证，并通过 Telegram 发送续期结果与实时截图。

---

## ✨ 功能特性

- ⏰ **定时自动运行**：默认每 30 分钟自动运行一次，确保服务器时刻保持在线。
- 🌐 **代理隧道支持**：内置 Xray-core 启动 SOCKS5 代理，轻松绕过 GitHub Actions 机房 IP 风控。
- 🖥️ **多服务器支持**：支持配置单台或多台服务器，自动依次完成批量续期。
- 📲 **Telegram 消息推送**：每次续期成功或失败均会发送 TG 通知，并附带网页渲染截图。
- 🧹 **日志自动清理**：内置自动打扫机制，始终保持 Actions 历史记录简洁不占空间。

---
## 📌 最近更新日志 (Changelog)

### 🛠️ 自动化逻辑深度重构 (`gaming4free.py`)
- **解决 Cloudflare “假成功”提交问题**：
  - 增加 Turnstile Token 长度校验（要求 `Token 长度 > 50`）。
  - 彻底防止未通过人机验证时提取空凭证并误点击提交，导致服务端静默丢弃请求的问题。
- **强化验证码识别与破解**：
  - 优化 iframe 与 Shadow DOM 深度定位逻辑，增强对 Cloudflare Turnstile 验证框的点击穿透能力。
- **多账号/服务器轮询间隔优化**：
  - 多个服务器间的续期等待间隔由 60 秒调整为 **15 秒**，在兼顾防风控防刷机制的同时大幅提升 Actions 执行效率。
## ⚙️ Environment Secrets 配置指南

请在 GitHub 仓库的 **Settings** -> **Secrets and variables** -> **Actions** -> **Repository secrets** 中添加以下变量：

| Secret 名称 | 是否必填 | 说明与示例 |
| :--- | :---: | :--- |
| `SERVERS` | **是** | 服务器编号与区域备注。格式：`编号,备注`。多台服务器用 `\|` 分隔。<br>示例：`caaad3bc,Europe` 或 `caaad3bc,Europe\|a1b2c3d4,US` |
| `XRAY_CONFIG` | **是** | 你的 Xray/V2Ray 节点完整 JSON 配置文件内容 |
| `TG_TOKEN` | 选填 | Telegram Bot API Token |
| `TG_CHAT_ID` | 选填 | 接收通知的 Telegram 个人/群组 Chat ID |
| `PRIVATE_REPO_TOKEN` | 选填 | 具有 `actions:write` 权限的 GitHub Personal Access Token (PAT)，用于自动清理 Actions 历史运行日志 |

---

## 🚀 部署步骤

### 1. Fork 仓库
点击页面右上角的 `Fork` 按钮，将本仓库复制到你的个人 GitHub 账号下。

### 2. 配置 Secrets
参照上方的配置表格，在你的仓库设置中将所有需要的 Secrets 依次添加完毕。

### 3. 开启 Actions 权限
1. 进入仓库的 **Settings** -> **Actions** -> **General**。
2. 找到 **Workflow permissions**，将其修改为 **`Read and write permissions`** 并保存。
3. 切换到 **Actions** 标签页，点击启用按钮（`I understand my workflows, go ahead and enable them`）。

### 4. 手动测试运行
1. 在 **Actions** 页面左侧选择 `Gaming4free Auto Renew` 工作流。
2. 点击右侧的 `Run workflow` 按钮手动触发一次运行。
3. 查看日志或检查 Telegram 消息，确认续期成功。

---

## ⚠️ 注意事项

1. **站点冷却限制**：Gaming4free 拥有投票冷却机制。如果在几分钟内频繁手动触发，脚本会检测到时间未增加并提示 `❌ 时间未增加`，这属于正常现象，静待定时轮询即可。
2. **代理节点说明**：建议配置稳定的住宅或高质量节点，以避免因 IP 被拒绝导致页面模态框加载超时。

---

## 📄 免责声明

本项目仅供个人自动化运维与学习交流使用，请勿用于商业用途。
