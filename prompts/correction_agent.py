"""
修正智能体Prompt模板
用于根据问题清单对详细剧情进行智能修正
"""

def get_correction_agent_prompt(content: str, issues: list, user_prompt: str = "") -> str:
    """
    获取修正智能体的prompt
    
    Args:
        content: 原始详细剧情内容
        issues: 问题清单列表
        user_prompt: 用户修正要求
    
    Returns:
        格式化的prompt字符串
    """
    
    # 构建问题列表
    issues_text = ""
    if issues:
        for i, issue in enumerate(issues, 1):
            issues_text += f"""
问题 {i}:
- 分类: {issue.get('category', '未知')}
- 严重程度: {issue.get('severity', '未知')}
- 问题描述: {issue.get('description', '无描述')}
- 问题位置: {issue.get('location', '未知位置')}
- 修改建议: {issue.get('suggestion', '无建议')}
"""
    else:
        issues_text = "无问题"
    
    # 构建用户修正要求
    user_requirements = ""
    if user_prompt.strip():
        user_requirements = f"""
## 用户修正要求：
{user_prompt.strip()}

请特别注意用户的修正要求，在修正过程中优先考虑用户的具体需求。
"""
    
    return f"""你是一位专业的修仙小说修正专家，专门负责修正剧情中的逻辑问题。

## 原始详细剧情内容：
{content}

## 需要修正的问题：
{issues_text}
{user_requirements}
## 修正要求：
1. **精准修正**：只修正上述问题，不要改变其他内容
2. **保持风格**：修正后的内容必须保持原文的写作风格和语调
3. **逻辑严密**：修正后的内容必须逻辑严密，无任何漏洞
4. **自然流畅**：修正后的内容必须自然流畅，无生硬感
5. **角色一致**：角色行为必须与其设定完全匹配
{f"6. **用户要求**：优先考虑用户的修正要求：{user_prompt.strip()}" if user_prompt.strip() else ""}

## 输出格式：
请直接输出修正后的详细剧情内容，不要包含任何其他格式或说明文字。"""
