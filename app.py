import streamlit as st
import pandas as pd
from datetime import datetime

# 加載保單數據
policies = pd.read_csv("policies.csv")

# 檢查 payment_term 欄位
if "payment_term" not in policies.columns:
    policies["payment_term"] = "20年"

# 讀取 secrets
admin = st.secrets["users"]["admin"]
user = st.secrets["users"]["user"]

# 登入功能
def login(username, password):
    current_date = datetime.now()
    if username == admin["login_account"] and password == admin["login_password"]:
        return "admin" if datetime.strptime(admin["start_date"], "%Y-%m-%d") <= current_date <= datetime.strptime(admin["end_date"], "%Y-%m-%d") else "expired"
    elif username == user["login_account"] and password == user["login_password"]:
        return "user" if datetime.strptime(user["start_date"], "%Y-%m-%d") <= current_date <= datetime.strptime(user["end_date"], "%Y-%m-%d") else "expired"
    return None

# 初始化 session_state
if "role" not in st.session_state:
    st.session_state["role"] = None

# 登入界面
if st.session_state["role"] is None:
    st.header("登入")
    username = st.text_input("用戶名")
    password = st.text_input("密碼", type="password")

    if st.button("登入"):
        role = login(username, password)
        if role == "expired":
            st.error("您的帳號已過期！")
        elif role:
            st.session_state["role"] = role
            st.success("登入成功！")
            st.rerun()
        else:
            st.error("用戶名或密碼錯誤！")
else:
    st.title("壽險保單推薦引擎")

    # 管理界面（僅限 admin）
    if st.session_state["role"] == "admin":
        st.sidebar.title("保單管理")
        action = st.sidebar.selectbox("選擇操作", ["新增保單", "修改保單", "刪除保單"], key="admin_action")

        if action == "新增保單":
            st.sidebar.header("新增保單")
            new_policy = {
                "policy_id": int(st.sidebar.number_input("保單編號", value=int(policies.policy_id.max())+1, key="new_policy_id")),
                "company": st.sidebar.text_input("公司名稱", key="new_company"),
                "product_name": st.sidebar.text_input("商品名稱", key="new_product_name"),
                "term_options": st.sidebar.text_input("年期選擇（用斜杠分隔）", key="new_term_options"),
                "policy_type": st.sidebar.text_input("保單類型", key="new_policy_type"),
                "min_age": int(st.sidebar.number_input("最低年齡", 1, 85, key="new_min_age")),
                "max_age": int(st.sidebar.number_input("最高年齡", 1, 85, 85, key="new_max_age")),
                "gender": st.sidebar.selectbox("性別", ["所有性別", "男性", "女性"], key="new_gender"),
                "currency": st.sidebar.selectbox("幣別", ["台幣", "美元"], key="new_currency"),
                "payment_term": st.sidebar.text_input("繳費年期", key="new_payment_term"),
                "term": int(st.sidebar.number_input("保障年期", 1, 50, key="new_term")),
                "coverage": int(st.sidebar.number_input("保額", 100000, 120000000, key="new_coverage")),
                "premium": int(st.sidebar.number_input("保費", 0, key="new_premium"))
            }
            if st.sidebar.button("新增", key="add_policy"):
                policies = pd.concat([policies, pd.DataFrame([new_policy])], ignore_index=True)
                policies.to_csv("policies.csv", index=False)
                st.success("保單新增成功！")

    # 用戶推薦保單
    st.header("保單推薦")
    age = st.number_input("年齡", 1, 85, 30, key="age_recommend")
    gender = st.selectbox("性別", ["男性", "女性"], key="gender_recommend")
    currency = st.selectbox("幣別", ["台幣", "美元"], key="currency_recommend")
    payment_term = st.text_input("繳費年期", key="payment_term_recommend")
    term = st.number_input("保障年期", 1, 50, 20, key="term_recommend")

    filtered_policies = policies.query(
        "min_age <= @age <= max_age and (gender == @gender or gender == '所有性別') and currency == @currency and payment_term == @payment_term and term == @term"
    ).sort_values(by="premium")

    st.dataframe(filtered_policies)
