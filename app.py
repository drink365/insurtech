import streamlit as st
import pandas as pd
from datetime import datetime

# 快取讀取保單資料
@st.cache_data
def load_policies():
    return pd.read_csv("policies.csv")

policies = load_policies()

# 登入功能
admin = st.secrets["users"]["admin"]
user = st.secrets["users"]["user"]

def login(username, password):
    current_date = datetime.now()
    if username == admin["login_account"] and password == admin["login_password"]:
        return "admin" if datetime.strptime(admin["start_date"], "%Y-%m-%d") <= current_date <= datetime.strptime(admin["end_date"], "%Y-%m-%d") else "expired"
    elif username == user["login_account"] and password == user["login_password"]:
        return "user" if datetime.strptime(user["start_date"], "%Y-%m-%d") <= current_date <= datetime.strptime(user["end_date"], "%Y-%m-%d") else "expired"
    return None

# 初始化登入
if "role" not in st.session_state:
    st.session_state["role"] = None

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

    # 管理介面（僅限 admin）
    if st.session_state["role"] == "admin":
        st.header("保單資料管理")

        col1, col2 = st.columns([3, 1])

        # 主編輯表格
        with col1:
            edited_policies = st.data_editor(
                policies, num_rows="dynamic", use_container_width=True,
                column_config={
                    "繳費年期": st.column_config.NumberColumn(help="單一繳費年期（數字，不含「年」）")
                },
                key="policy_editor",
            )

            if st.button("儲存修改"):
                edited_policies.to_csv("policies.csv", index=False)
                st.success("保單資料已更新！")
                st.cache_data.clear()
                st.rerun()

        # 側邊欄複製功能
        with col2:
            st.subheader("複製保單功能")
            policy_options = policies["商品名稱"] + " (" + policies["公司名稱"] + ") - " + policies["繳費年期"].astype(str) + "年"
            selected_policy = st.selectbox("選擇要複製的保單", policy_options)

            if st.button("複製此保單"):
                policy_to_copy = policies[policy_options == selected_policy].iloc[0].copy()
                edited_policies = pd.concat([policies, pd.DataFrame([policy_to_copy])], ignore_index=True)
                edited_policies.to_csv("policies.csv", index=False)
                st.success(f"成功複製保單：{selected_policy}")
                st.cache_data.clear()
                st.rerun()

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
