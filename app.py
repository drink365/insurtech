import streamlit as st
import pandas as pd
from datetime import datetime

# 載入保單資料（含快取）
@st.cache_data
def load_policies():
    policies = pd.read_csv("policies.csv")
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
        st.header("保單資料管理")

        # 快速搜尋功能
        search_term = st.text_input("快速搜尋（公司或商品名稱）")
        if search_term:
            displayed_policies = policies[
                policies["公司名稱"].str.contains(search_term) | policies["商品名稱"].str.contains(search_term)
            ]
        else:
            displayed_policies = policies

        edited_policies = st.data_editor(
            displayed_policies, num_rows="dynamic",
            column_config={
                "繳費年期": st.column_config.NumberColumn(help="單一繳費年期（數字，不含「年」）")
            },
            key="policy_editor"
        )

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("儲存修改"):
                edited_policies.to_csv("policies.csv", index=False)
                st.success("保單資料已更新！")
                st.cache_data.clear()
                st.rerun()

        with col2:
            if st.button("複製選取的保單"):
                if "selected_rows" in st.session_state["policy_editor"]:
                    selected_idx = st.session_state["policy_editor"]["selected_rows"]
                    if selected_idx:
                        rows_to_copy = edited_policies.iloc[selected_idx]
                        edited_policies = pd.concat([edited_policies, rows_to_copy], ignore_index=True)
                        edited_policies.to_csv("policies.csv", index=False)
                        st.success("已複製選取的保單！")
                        st.cache_data.clear()
                        st.rerun()
                else:
                    st.warning("請先選取要複製的保單！")

    # 用戶推薦保單
    st.header("保單推薦")
    age = st.number_input("年齡", 1, 85, 30, key="age_recommend")
    gender = st.selectbox("性別", ["男性", "女性"], key="gender_recommend")
    currency = st.selectbox("幣別", ["台幣", "美元"], key="currency_recommend")
    payment_term = st.selectbox(
        "繳費年期", sorted(policies["繳費年期"].unique()), key="payment_term_recommend"
    )

    filtered_policies = policies[
        (policies["最低年齡"] <= age) &
        (policies["最高年齡"] >= age) &
        ((policies["性別"] == gender) | (policies["性別"] == "不限")) &
        (policies["幣別"] == currency) &
        (policies["繳費年期"].astype(str) == str(payment_term))
    ].sort_values(by="保費")

    st.dataframe(filtered_policies.reset_index(drop=True))
