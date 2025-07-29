# Kieran NLP

## 项目简介

Kieran NLP 是一个基于 PyQt5 的桌面 GUI 对话系统，专为 AI 大模型对话设计。项目已集成硅基流动 API，支持多种大模型（如 DeepSeek、Qwen 等），支持 Markdown 格式输出，并通过 `.env` 文件私有化管理敏感信息。

## 功能特色

- **多模型支持**：支持多种大语言模型，包括 DeepSeek-V3、Qwen 系列等
- **流式对话**：支持流式输出，实时显示 AI 回复
- **对话管理**：支持创建、重命名、删除多个对话历史
- **IM 风格界面**：对话界面仿主流即时通讯软件，支持头像、气泡显示
- **便捷操作**：支持 Enter 键发送消息、复制回复等功能
- **主题切换**：提供多种界面主题（浅色、深色、粉色、科技风格）
- **Markdown 渲染**：支持 Markdown 格式输出，提升阅读体验
- **安全认证**：通过授权码机制保护应用安全
- **API 管理**：通过 `.env` 文件管理 API 密钥等敏感信息
- **异步响应**：友好的加载提示与异步响应机制

## 安装与运行

1. 安装依赖

   ```bash
   pip install -r requirements.txt
   ```

2. 配置 `.env` 文件（项目根目录，内容如下）

   ```env
   API_KEY=你的apikey
   API_URL=https://api.siliconflow.cn/v1/chat/completions
   ```

3. 配置授权码
   
   在首次运行时，系统会提示输入授权码。预设的授权码保存在 `authorized/auth_code.txt` 文件中。

4. 运行主程序

   ```bash
   python main.py
   ```

## 界面截图

### 项目基本框架
![项目启动，基本框架](./mdfile/image.png)

### 模型切换与主题切换
![增加api切换功能](./mdfile/image4.png)
![增加api切换功能](./mdfile/image5.png)

### 对话历史管理
![增加流式输出，修复若干ui问题，重构渲染逻辑，增加对话列表](./mdfile/image7.png)
![增加流式输出，修复若干ui问题，重构渲染逻辑，增加对话列表](./mdfile/image6.png)

### 用户界面
![私有化api等敏感信息到env文件,支持markdown输出](./mdfile/image3.png)
![s s](./mdfile/image8.png)
![ss](./mdfile/image9.png)






## 目录结构

```
kieran-nlp/
├── main.py                 # 主程序入口
├── chat_widget.py          # 聊天界面组件
├── chat_interface.py       # 聊天核心逻辑
├── requirements.txt        # 项目依赖
├── .env                    # API 配置文件
├── README.md               # 项目说明文档
├── asset/                  # 资源文件（头像等）
├── authorized/             # 授权码相关文件
├── database/               # 数据库相关文件
├── mdfile/                 # 说明文档图片
├── style/                  # 界面主题样式
└── test/                   # 测试文件
```

## 更新日志

- 2025-7-24 ：项目启动，基本框架
- 2025-7-25 ：接入硅基流动API，实现deepseek对话
- 2025-7-26 ：私有化api等敏感信息到env文件,支持markdown输出
- 2025-7-27 ：增加api修改功能，你现在可以切换api了
- 2025-7-28 ：增加新的大模型api，增加主题功能，增加切换提醒，修复了“复制”多次出现的问题，接入langchain实现对话记忆功能
- 2025-7-28 ：增加使用 Enter 键发送消息功能，发送新消息后自动滚动到对话列表最底部,增加授权码机制，现在你需要输入授权码才能登录
- 2025-7-28 ：增加流式输出，修复若干ui问题，重构渲染逻辑，增加对话列表，你现在可以保存多个对话列表了，增加了对话列表的删除，重命名功能
- 2025-7-29 ：增加了用户界面，轨迹流动余额查询,修复了生成回答时切换对话会闪退，修复了流式输出会导致记忆失效问题

## 免责声明

本项目仅供学习与交流，API 密钥请妥善保管，勿泄露或滥用。
