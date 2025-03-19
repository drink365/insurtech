import streamlit as st
import pandas as pd
from datetime import datetime

# 保單資料載入函數 (確保資料為最新)
@st.cache_data
def load_policies():
    policies = pd.read_csv("policies.csv")
    if "policy_id" in policies.columns:
        policies = policies.drop(columns=["policy_id"])
    return policies

policies = load_policies()

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
        st.header("現有全部保單清單")
        edited_policies = st.data_editor(policies, num_rows="dynamic", key="policies_editor")

        if st.button("儲存修改"):
            edited_policies.to_csv("policies.csv", index=False)
            st.success("保單資料已更新！")
            st.cache_data.clear()
            st.rerun()

    # 用戶推薦保單
    st.header("保單推薦")
    age = st.number_input("年齡", 1, 85, 30, key="age_recommend")
    gender = st.selectbox("性別", ["男性", "女性"], key="gender_recommend")
    currency = st.selectbox("幣別", ["台幣", "美元"], key="currency_recommend")
    payment_term = st.text_input("繳費年期", key="payment_term_recommend")

    filtered_policies = policies[
        (policies["最低年齡"] <= age) &
        (policies["最高年齡"] >= age) &
        ((policies["性別"] == gender) | (policies["性別"] == "不限")) &
        (policies["幣別"] == currency) &
        (policies["繳費年期"].astype(str).str.split('/').apply(lambda x: payment_term in x))
    ].sort_values(by="保費")

    st.dataframe(filtered_policies)
