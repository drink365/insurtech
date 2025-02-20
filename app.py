import streamlit as st
import pandas as pd

# 建立範例保險產品資料庫
data = [
    {
        "Product": "安心保障A",
        "Company": "公司A",
        "Gender": "All",    # All 表示不限性別
        "Min Age": 18,
        "Max Age": 65,
        "Currency": "USD",
        "Term": 10,
        "Premium": 1000,
        "Coverage": 100000,
        "Cash Value": 5000
    },
    {
        "Product": "安心保障B",
        "Company": "公司B",
        "Gender": "Female",
        "Min Age": 25,
        "Max Age": 60,
        "Currency": "USD",
        "Term": 20,
        "Premium": 800,
        "Coverage": 150000,
        "Cash Value": 8000
    },
    {
        "Product": "安康計劃C",
        "Company": "公司C",
        "Gender": "All",
        "Min Age": 30,
        "Max Age": 70,
        "Currency": "TWD",
        "Term": 15,
        "Premium": 20000,
        "Coverage": 3000000,
        "Cash Value": 150000
    }
]

df = pd.DataFrame(data)

# 設定 Streamlit 頁面標題
st.title("insurtech 保險科技推薦系統")

# 側邊欄輸入條件
st.sidebar.header("輸入基本條件")
age = st.sidebar.number_input("請輸入年齡", min_value=0, max_value=100, value=30, step=1)
gender = st.sidebar.selectbox("請選擇性別", options=["Male", "Female"], index=1)
currency = st.sidebar.selectbox("請選擇幣別", options=["USD", "TWD"])
term = st.sidebar.number_input("請輸入年期", min_value=1, max_value=100, value=10, step=1)

# 定義依條件篩選產品的函數
def filter_products(age, gender, currency, term):
    filtered = df.copy()
    # 篩選性別：若產品設定為 All 或符合使用者選擇的性別
    filtered = filtered[(filtered["Gender"] == "All") | (filtered["Gender"] == gender)]
    # 篩選年齡：使用者年齡必須介於產品適用的最小與最大年齡之間
    filtered = filtered[(filtered["Min Age"] <= age) & (filtered["Max Age"] >= age)]
    # 篩選幣別
    filtered = filtered[filtered["Currency"] == currency]
    # 篩選年期（示範中以精確匹配為例，實際上可依需求做範圍比對）
    filtered = filtered[filtered["Term"] == term]
    return filtered

# 根據用戶輸入條件進行篩選
results = filter_products(age, gender, currency, term)

st.header("推薦產品")
if results.empty:
    st.write("找不到符合條件的產品，請嘗試其他條件。")
else:
    st.write(results)
