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

# 初始化登入狀態
if "role" not in st.session_state:
    st.session_state["role"] = None
if "edit_mode" not in st.session_state:
    st.session_state["edit_mode"] = False

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

        if st.button("進入編輯模式"):
            st.session_state["edit_mode"] = True
            st.rerun()

        if st.session_state["edit_mode"]:
            # 編輯模式
            if "複製" not in policies.columns:
                policies["複製"] = False

            edited_policies = st.data_editor(
                policies,
                num_rows="dynamic",
                column_config={
                    "繳費年期": st.column_config.NumberColumn(help="單一繳費年期（數字，不含「年」）"),
                    "複製": st.column_config.CheckboxColumn(help="勾選欲複製的保單資料")
                },
                use_container_width=True,
                key="policy_editor"
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("儲存修改"):
                    edited_policies.drop(columns=["複製"]).to_csv("policies.csv", index=False)
                    st.success("保單資料已更新！")
                    st.cache_data.clear()
                    st.session_state["edit_mode"] = False
                    st.rerun()

            with col2:
                if st.button("複製勾選的保單"):
                    rows_to_copy = edited_policies.loc[edited_policies["複製"] == True].copy()
                    if not rows_to_copy.empty:
                        rows_to_copy["複製"] = False
                        updated_policies = pd.concat([edited_policies, rows_to_copy], ignore_index=True)
                        updated_policies.drop(columns=["複製"]).to_csv("policies.csv", index=False)
                        st.success("成功複製勾選的保單！")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.warning("請至少勾選一筆欲複製的保單！")

            with col3:
                if st.button("退出編輯模式"):
                    st.session_state["edit_mode"] = False
                    st.rerun()

        else:
            # 一般顯示模式（可排序，隱藏序號且無提示字）
            policies_display = policies.drop(columns=["複製"], errors='ignore')
            st.dataframe(
                policies_display,
                hide_index=True,  # 隱藏序號欄位
                use_container_width=True
            )

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

    st.dataframe(filtered_policies.reset_index(drop=True), use_container_width=True, hide_index=True)
