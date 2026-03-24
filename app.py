import streamlit as st
import pandas as pd
import transformers
from transformers import pipeline
st.write("Transformers version:", transformers.__version__)
@st.cache_resource
def load_model():
    return pipeline("text2text-generation", model="google/flan-t5-base")

chatbot_ai = load_model()

st.title("Business Finance Chatbot")

df = pd.read_csv("data1.csv")

st.subheader("Upload your file")
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("File uploaded successfully")
else:
    df = pd.read_csv("data1.csv")

st.subheader("Data Preview")

st.write(df)

revenue = df[df['Type'] == 'income']['Amount'].sum()
expense = df[df['Type'] == 'expense']['Amount'].sum()
profit = revenue - expense

category_expense = df[df['Type'] == 'expense'].groupby('Category')['Amount'].sum()
st.subheader("Expense by Category")
st.write(category_expense)

highest_category = category_expense.idxmax()
highest_value = category_expense.max()

st.warning(f"Highest spending is on {highest_category}: {highest_value}")

st.subheader("Business Insight")

if highest_value > (expense * 0.5):
    st.error("Too much spending on {highest_category} !")
else:
    st.success("Spending is under control")

if profit < 10000:
    st.warning("Profit is low, improve business")

st.subheader("Financial Summary")
st.write("Revenue:", revenue)
st.write("Expenses:", expense)
st.write("Profit:", profit)


if profit > 0:
    st.success("Business is in Profit")
else:
    st.error("Business is in Loss")

def detect_intent(text):
    text = text.lower()

    if "increase" in text and "profit" in text:
        return "increase_profit"
    elif "profit" in text:
        return "show_profit"
    elif "expense" in text and ("reduce" in text or "decrease" in text):
        return "reduce_expense"
    elif "expense" in text:
        return "show_expense"
    elif "revenue" in text or "income" in text:
        return "show_revenue"
    elif "highest" in text or "spending" in text:
        return "highest_expense"
    else:
        return "unknown"

st.subheader("Smart Finance Chatbot")
user_input = st.text_input("Ask your business question...")

if user_input:
    st.write("You:", user_input)
    intent = detect_intent(user_input)

    if intent == "show_profit":
        response = f"Your profit is {profit}"

    elif intent == "show_expense":
        response = f"Your expense is {expense}"
    elif intent == "show_revenue":
        response = f"Your revenue is {revenue}"
    elif intent == "highest_expense":
        response = f"Highest spending is on {highest_category}: {highest_value}"
    elif intent == "increase_profit":
        response = f"""To increase profit
- Reduce expenses {expense}
- Increase revenues {revenue}
- Focus on {highest_category}"""
    else:
        ai_output = chatbot_ai(f"You are the finance expert.Answer clearly: {user_input}",
                               max_length=50,
                               num_return_sequences=1,
                               truncation=True
                               )
        # response = ai_output[0]['generated_text'].split(".")[0]
        prompt = f"""
        You are a smart business advisor AI.

        User Question: {user_input}

        Give a clear, helpful, and practical answer in simple points.
        """

        response = chatbot_ai(prompt, max_length=200, do_sample=True)
        print(response[0]['generated_text'])
        # response = f"I can help with profit, expense, and business insights!"

    st.write("AI:", response)


