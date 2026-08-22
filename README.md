# QQ 机器人 - 星辰落

基于 botpy 的轻量级 QQ 官方机器人，支持群聊和私聊文字消息。

## 功能

- **ping** - 测试连通性
- **帮助** - 查看可用命令
- **echo** - 复读消息
- **运势** - 随机生成今日运势（运势等级、幸运数字、幸运颜色、每日建议）

## 快速开始

### 1. 配置机器人

编辑 `run.bat` 顶部的两个变量：

```batch
set APPID=你的机器人APPID
set SECRET=你的机器人SECRET
```

### 2. 启动

双击 `run.bat`，首次运行会自动：
- 创建虚拟环境
- 安装依赖（qq-botpy、pyyaml）
- 启动机器人

### 3. 使用

**群聊**：@机器人 + 命令（如 `@机器人 ping`、`@机器人 运势`）  
**私聊**：直接发送命令（如 `ping`、`运势`）

## 依赖

- Python 3.8+
- qq-botpy
- pyyaml

## 项目结构

```
xclofficial/
├── bot.py          # 机器人主程序
├── config.yaml     # 配置文件（由 run.bat 自动生成）
├── run.bat         # 一键启动脚本（Windows）
├── requirements.txt # Python 依赖
└── README.md       # 本文档
```

## 注意事项

1. **必须 @机器人** 才能触发群消息（QQ 官方机器人平台限制）
2. **openid 体系**：用户 ID 是 `openid` 而非 QQ 号
3. 机器人需在 [QQ 开放平台](https://q.qq.com/) 创建并获取 APPID/SECRET

## 许可

MIT License
