AI对话系统：多角色·多模型智能交互平台
 
项目介绍
 
这是一个支持多角色切换、多模型调用、搜索增强、音频交互的智能对话系统，可实现个性化中文对话、信息查询等功能，适配日常聊天、知识检索等场景。
 
核心特点：
 
- 角色定制：支持12+差异化角色（如程序员、育儿妈妈、旅行博主），可自定义角色描述
- 多模型兼容：集成OpenAI、DeepSeek、Google等12+主流大模型
- 搜索增强：对接DuckDuckGo搜索引擎，支持文本/新闻搜索并整合结果
- 多模态交互：支持语音输入（语音转文字）、语音输出（文字转语音）
- 可视化界面：通过Gradio构建直观操作界面，支持参数调节（记忆长度、创造力）
 
环境依赖
 
需安装Python 3.8+，并执行以下命令安装依赖：
 
bash
  
pip install gradio openai func_timeout duckduckgo-search tiktoken requests
 
 
文件结构
 
plaintext
  
AI对话系统/
├── gpts.py               # 大模型调用核心逻辑（OpenRouter代理、超时重试、流式响应）
├── gradio_ui.py          # Gradio可视化界面（组件布局、事件绑定、功能集成）
├── persona.json          # 角色配置文件（12+预设角色，支持自定义）
├── models.txt            # 支持的模型列表（OpenAI/DeepSeek/Google等）
├── region.txt            # 搜索地区代码（40+地区可选）
├── user.json             # 用户画像模板（可扩展个性化对话）
└── README.md             # 项目说明文档
 
 
快速启动
 
1. 配置API密钥：
打开 gpts.py ，替换 api_key 为你的OpenRouter API密钥：
python
  
api_key='你的OpenRouter API密钥'  # 需注册OpenRouter获取
 
2. 启动程序：
在终端执行：
bash
  
python gradio_ui.py
 
3. 访问界面：
浏览器打开 http://127.0.0.1:19001 ，即可使用系统。
 
功能说明
 
1. 角色切换：
在“选择角色”下拉框中选择预设角色（如“黑咖卷卷”），系统会加载对应角色描述，对话风格自动适配。
2. 模型选择：
在“选择模型”下拉框中切换不同品牌模型（如 deepseek/deepseek-chat 、 openai/gpt-4o-mini ）。
3. 交互模式：
- 聊天模式：直接与AI对话
- 搜索模式：基于DuckDuckGo搜索结果生成回复
- 新闻模式：获取指定地区的新闻并整合回复
4. 参数调节：
- 记忆条数：控制对话历史的保留长度
- 温度值：调节AI回复的创造力（0=严谨，1=灵活）
 
常见问题
 
1. 界面无响应：
- 检查终端是否有报错（如API密钥无效、网络问题）
- 确认依赖库已安装（执行 pip list 查看 gradio / openai 等是否存在）
2. 消息格式错误：
- 检查 persona.json 是否为英文引号、JSON语法正确（可通过JSON校验工具验证）
3. 模型调用失败：
- 确认 models.txt 中的模型名称与OpenRouter支持的一致
- 检查网络是否能访问 https://openrouter.ai/api/v1 
 
扩展方向
 
- 安全性优化：通过环境变量存储API密钥，添加用户登录认证
- 性能优化：集成本地音频模型，提升语音交互速度
- 功能扩展：增加文件上传（如PDF解析）、多轮对话记忆优化等能力