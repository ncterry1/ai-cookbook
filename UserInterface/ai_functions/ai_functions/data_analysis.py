# ----------------------------------------------------------------------------
# Example ai_functions/data_analysis.py (in ai_functions folder)
# ----------------------------------------------------------------------------
"""
ai_functions/data_analysis.py

Data Analysis mode: prepends data analysis instructions and calls the LLM.
This function can handle a variety of data formats provided as text:
  - Numeric datasets or statistical summaries
  - CSV or TSV tables pasted as text
  - JSON logs or structured data snippets
  - Plain text descriptions of data trends
"""

# Import the OpenAI client to send API requests
import openai  # Assumes same API key from ai_chat_gui.py

def run(prompt: str) -> str:
    """
    Run a data analysis prompt by instructing the model to analyze provided data.

    Args:
        prompt (str): The data or query to analyze. Can include CSV tables, JSON blocks, numeric lists, or natural-language descriptions of data.
    Returns:
        str: The model's analysis and insights.
    """
    # Prepare a system message with analysis instructions
    system_content = (
        "You are a data analyst. Analyze the following data and provide insights:" 
        + prompt
    )
    # Send the ChatCompletion request
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": system_content}],
        temperature=0.3,    # Lower randomness for consistent analysis
        max_tokens=1024,     # Allow longer analytical responses
    )
    # Return the analysis from the assistant
    return response.choices[0].message.content.strip()

# Example data pasted in to entry
'''
Date,Region,Sales,Expenses,Profit
2025-01-01,North,1200,800,400
2025-01-02,South,950,600,350
2025-01-03,East,1100,750,350
2025-01-04,West,1300,900,400
2025-01-05,North,1250,780,470
2025-01-06,South,980,620,360
2025-01-07,East,1150,700,450
2025-01-08,West,1400,950,450
2025-01-09,North,1280,820,460
2025-01-10,South,1020,640,380

'''
# Example return from GPT 3.5
'''
To analyze the provided data on sales, expenses, 
and profit for different regions on different dates, 
we can derive the following insights:

1. **Overall Performance**:
   - Total Sales: $11,130
   - Total Expenses: $7,970
   - Total Profit: $3,160

2. **Average Daily Performance**:
   - Average Daily Sales: $1,113
   - Average Daily Expenses: $797
   - Average Daily Profit: $316

3. **Regional Performance**:
   - North Region:
     - Total Sales: $3730
     - Total Expenses: $2400
     - Total Profit: $1330
   - South Region:
     - Total Sales: $2950
     - Total Expenses: $1860
     - Total Profit: $1090
   - East Region:
     - Total Sales: $3250
     - Total Expenses: $2150
     - Total Profit: $1100
   - West Region:
     - Total Sales: $2700
     - Total Expenses: $1850
     - Total Profit: $850

4. **Trend Analysis**:
   - Overall, the profit margin seems to be consistent across 
   the days with slight fluctuations.
   - The North region has the highest total profit, followed by the East region.
   - The South region has the lowest total profit among all regions.

5. **Key Takeaways**:
   - The North region is the top-performing region in terms of total profit.
   - The South region has the lowest total profit, indicating potential 
   areas for improvement.
   - The East region has the highest total sales, but the profit margin is 
   not the highest, suggesting a need to optimize expenses.

These insights can help in understanding the performance of each region 
and identifying areas that may require attention or improvement to enhance 
overall profitability.

'''