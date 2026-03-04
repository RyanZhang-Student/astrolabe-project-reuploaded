import os
import certifi
import time

# 加上这两行，强制 VS Code 使用 certifi 提供的证书
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['SSL_CERT_DIR'] = os.path.dirname(certifi.where()) 

from google.genai import Client

# API Key 配置
GEMINI_API_KEY = "YOUR_API"

def generate_and_append_analysis_1(html_file_path):
  

    print("⏳ 为了规避 API 频率限制，等待 5 秒后启动 AI...")
    time.sleep(5)
    if not os.path.exists(html_file_path):
        print(f"❌ 找不到文件: {html_file_path}")
        return

    # 1. 读取 HTML 内容
    try:
        # 初始化客户端 (移入 try 块以捕获初始化错误)
        client = Client(api_key=GEMINI_API_KEY)

        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except Exception as e:
        print(f"❌ 读取 HTML 失败: {e}")
        return

        print("🤖 正在调用 Gemini 2.0 API 分析星盘数据，请稍候...")
    # 2. 初始化客户端 (单独捕获以区分错误)
    try:
        client = Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"❌ 初始化 AI 客户端失败: {e}")
        return

    print("🤖 正在调用 Gemini 2.5 API 分析星盘数据，请稍候...")

    try:
        # 简化的 Prompt 逻辑
        # 注意：不要使用 f-string (f"...") 包裹 html_content，因为 HTML 中的 CSS 花括号 {} 会导致格式化错误
        prompt_intro = """
    你是一个专业的占星师。请仔细阅读以下占星报告 HTML 代码中的数据表格，提取关于**第1宫的所有相关信息。
    
    请严格按照以下模板的格式和分点结构，为我生成第1宫的深度分析报告 。
    不要擅自改变编号和标题，不要加入如 * # - 的符号
    直接给出分析，不要说如“这是你的报告”之类的废话
    根据 HTML 中的真实数据填写“事实”部分，并凭借你的占星学知识补充“含义”部分：

    1. 上升星座 (Ascendant)
    事实：上升点落在 [星座] [度数]。
    含义：[给出解读]


    === 以下是提取自星盘报告的数据 ===
    """
        
        full_prompt = prompt_intro + "\n" + html_content

        # 调用 Gemini 2.0 模型
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=full_prompt
        )
        
        if not response.text:
            return
            
        analysis_text = response.text
        formatted_text = analysis_text.replace('\n', '<br>')
        
        # 构造 HTML 插入块
        html_analysis_block = f"""
        <details style="max-width: 800px; margin: 40px auto; padding: 20px; background-color: #f8f9fa; border-left: 5px solid #4B0082; border-radius: 8px;">
            <summary style="cursor: pointer; font-weight: bold;">
                <h2 style="color: #333; display: inline;">🔮 深度分析：第1宫</h2>
            </summary>
            <div style="line-height: 1.8; color: #444; font-size: 13px; margin-top: 15px;">{formatted_text}</div>
        </details>
        """

        with open(html_file_path, 'r', encoding='utf-8') as f:
            full_content = f.read()
        
        # 在 </body> 前插入
        new_content = full_content.replace("</body>", f"{html_analysis_block}</body>")
        
        with open(html_file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ 1宫分析已成功")

    except Exception as e:
        print(f"❌ AI 调用出错: {e}")