import os
import json
import logging
from app.services.analytics import get_financial_summary, get_all_time_stats

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are "FinBot", an expert AI Personal Finance Advisor tailored for individuals managing their personal finances in Indian Rupees (₹ INR).
Your tone is professional, encouraging, analytical, and actionable.

You have access to the user's real-time financial data provided in JSON format in the prompt context.
Always follow these rules:
1. Always refer to amounts in Indian Rupees (₹ or INR) and use Indian numbering formatting (e.g. ₹50,000, ₹1,25,000) when appropriate.
2. Directly reference their actual numbers, categories, overspending status, and savings goals from the context.
3. Apply sound financial principles (like the 50/30/20 rule, emergency fund creation, debt snowball/avalanche, SIP/mutual funds, prudent lifestyle spending).
4. Provide structured, bullet-pointed, and actionable advice.
5. If the user asks general financial questions, give expert explanations with relatable Indian context (PPF, EPF, NPS, Fixed Deposits, Index Funds, GST, Tax Saving under 80C/New Tax Regime, etc.).
6. Keep recommendations realistic, positive, and clear.
"""

def generate_ai_response(user, user_prompt, conversation_history=None):
    """
    Generates a response from Gemini API given user financial context and conversation history.
    If no API key is provided or API is unreachable, provides a smart local rule-based financial analysis.
    """
    api_key = os.getenv('GEMINI_API_KEY', '').strip()
    model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash').strip() or 'gemini-2.5-flash'
    
    # Gather live financial snapshot
    financial_summary = get_financial_summary(user.id)
    lifetime_stats = get_all_time_stats(user.id)
    
    context_data = {
        "user_name": user.full_name or user.username,
        "occupation": user.occupation or "Professional",
        "current_month": f"{financial_summary['month_name']} {financial_summary['year']}",
        "monthly_summary": {
            "total_income_INR": financial_summary['total_income'],
            "total_expenses_INR": financial_summary['total_expenses'],
            "net_savings_INR": financial_summary['net_savings'],
            "savings_rate_pct": financial_summary['savings_rate'],
            "category_expenses": financial_summary['category_breakdown'],
            "income_sources": financial_summary['income_sources'],
            "budget_compliance": financial_summary['budget_status'],
            "over_budget_count": financial_summary['over_budget_count']
        },
        "savings_goals": financial_summary['goals'],
        "lifetime_stats": lifetime_stats
    }

    if api_key and api_key != 'your_gemini_api_key_here':
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            
            # Format prompt with system context and history
            full_prompt = f"""{SYSTEM_PROMPT}

USER REAL FINANCIAL CONTEXT (JSON):
```json
{json.dumps(context_data, indent=2)}
```

"""
            if conversation_history:
                full_prompt += "RECENT CONVERSATION HISTORY:\n"
                for msg in conversation_history[-6:]:
                    role = "User" if msg.role == 'user' else "FinBot (Advisor)"
                    full_prompt += f"{role}: {msg.message}\n"
                full_prompt += "\n"

            full_prompt += f"USER QUERY: {user_prompt}\n\nFinBot's Response:"

            response = client.models.generate_content(
                model=model_name,
                contents=full_prompt,
            )
            
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            # Fall back to rule-based response if API key fails or network error
            return _generate_fallback_response(user_prompt, context_data)

    # Fallback when no Gemini API key is configured
    return _generate_fallback_response(user_prompt, context_data)


def generate_comprehensive_audit(user):
    """
    Generates a full structured financial diagnostic report for the user.
    """
    api_key = os.getenv('GEMINI_API_KEY', '').strip()
    summary = get_financial_summary(user.id)
    
    prompt = f"Please provide a comprehensive 360-degree Financial Health Audit for {summary['month_name']} {summary['year']}. Analyze my income vs expenses, category spending distribution, budget leakages, savings rate against benchmarks (target 20-30%), and evaluate my progress towards active savings goals. Conclude with 3 high-impact action items for this month."
    
    return generate_ai_response(user, prompt)


def _generate_fallback_response(prompt, context):
    """
    Rule-based intelligent financial analysis fallback when Gemini API key is not configured.
    Provides detailed, data-driven financial advice based on actual numbers.
    """
    summary = context["monthly_summary"]
    income = summary["total_income_INR"]
    expenses = summary["total_expenses_INR"]
    savings = summary["net_savings_INR"]
    rate = summary["savings_rate_pct"]
    categories = summary["category_expenses"]
    budgets = summary["budget_compliance"]
    goals = context["savings_goals"]
    user_name = context["user_name"]

    prompt_lower = prompt.lower()
    
    # 1. Budget / Spending Analysis
    if "budget" in prompt_lower or "overspend" in prompt_lower or "leak" in prompt_lower:
        over_budgets = [b for b in budgets if b["is_over_budget"]]
        res = f"### 📊 Budget & Spending Analysis for {context['current_month']}\n\n"
        res += f"Hello **{user_name}**, here is your budget breakdown:\n\n"
        
        if over_budgets:
            res += "⚠️ **Over-Budget Alerts Identified:**\n"
            for b in over_budgets:
                excess = round(b['spent_amount'] - b['budget_amount'], 2)
                res += f"- **{b['category']}**: Spent **₹{b['spent_amount']:,.2f}** against budget of **₹{b['budget_amount']:,.2f}** (Over by ₹{excess:,.2f} / {b['percentage_used']}% used)\n"
            res += "\n**Recommended Action:** Cap non-essential spending in these categories for the rest of the month.\n\n"
        else:
            res += "✅ **Great job!** All your tracked categories are currently within their assigned budget limits.\n\n"

        if categories:
            top_cat = categories[0]
            res += f"📌 **Top Spending Category:** **{top_cat['category']}** with **₹{top_cat['total']:,.2f}** ({top_cat['percentage']}% of total monthly expenses).\n"

        return res

    # 2. Savings and Goals Analysis
    if "save" in prompt_lower or "goal" in prompt_lower or "invest" in prompt_lower:
        res = f"### 💰 Savings & Financial Goals Diagnostic\n\n"
        res += f"- **Current Month Savings:** ₹{savings:,.2f} ({rate}% savings rate)\n"
        if rate >= 30:
            res += "- 🌟 **Rating:** **Excellent!** You are saving above the recommended 30% threshold.\n"
        elif rate >= 20:
            res += "- 👍 **Rating:** **Healthy!** You are meeting the standard 20% savings rule.\n"
        else:
            res += "- ⚠️ **Rating:** **Needs Improvement.** Try reducing discretionary spending to reach at least a 20% savings rate.\n"

        if goals:
            res += "\n#### 🎯 Active Savings Goals:\n"
            for g in goals:
                res += f"- **{g['title']}**: ₹{g['current_amount']:,.2f} / ₹{g['target_amount']:,.2f} ({g['progress_percentage']}%) | Needs **₹{g['required_monthly_savings']:,.2f}/month** until {g['deadline']}\n"
        else:
            res += "\n💡 **Tip:** You haven't set any savings goals yet. Create an **Emergency Fund** (3-6 months expenses) under the Goals tab to build financial security.\n"

        return res

    # 3. Default Comprehensive Audit
    res = f"### 💡 FinBot Financial Overview for {user_name}\n\n"
    res += f"Here is your financial status for **{context['current_month']}**:\n\n"
    res += f"- 💵 **Total Inflow:** ₹{income:,.2f}\n"
    res += f"- 💳 **Total Outflow:** ₹{expenses:,.2f}\n"
    res += f"- 📈 **Net Savings:** ₹{savings:,.2f} (**{rate}%** savings rate)\n\n"

    if categories:
        res += "#### 🔍 Top Expense Drivers:\n"
        for cat in categories[:3]:
            res += f"1. **{cat['category']}**: ₹{cat['total']:,.2f} ({cat['percentage']}%)\n"
        res += "\n"

    res += "#### 🎯 Key Actionable Insights:\n"
    if rate < 20:
        res += "1. **Cut Discretionary Costs:** Focus on trimming Dining Out, Entertainment, or Impulse Shopping by 10-15%.\n"
    else:
        res += "1. **Optimize Surplus:** Allocate your ₹{:,.2f} monthly surplus towards your savings goals or automated SIPs.\n".format(savings)
    
    res += "2. **Review Budget Limits:** Check the Budget Planner tab to adjust category limits that frequently get exceeded.\n"
    res += "3. **Automate Goal Contributions:** Ensure consistent monthly deposits towards your active goals before making lifestyle purchases.\n\n"
    res += "> *Note: To activate generative AI responses with live Google Gemini, add your `GEMINI_API_KEY` in the `.env` file.*"

    return res
