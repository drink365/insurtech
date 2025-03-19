import streamlit as st
import pandas as pd

# 標題
st.title("壽險保單推薦引擎")

# 加載保單數據
policies = pd.read_csv("policies.csv")

# 管理界面
st.sidebar.title("保單管理")
action = st.sidebar.selectbox("選擇操作", ["新增保單", "修改保單", "刪除保單"], key="action_select")

if action == "新增保單":
    st.sidebar.header("新增保單")
    new_policy = {
        "policy_id": st.sidebar.number_input("保單編號", value=len(policies) + 1, key="policy_id_input"),
        "company": st.sidebar.text_input("公司名稱", key="company_input"),
        "product_name": st.sidebar.text_input("商品名稱", key="product_name_input"),
        "term_options": st.sidebar.text_input("年期選擇（用斜杠分隔）", key="term_options_input"),
        "policy_type": st.sidebar.text_input("保單類型", key="policy_type_input"),
        "min_age": st.sidebar.number_input("最低年齡", min_value=18, max_value=100, key="min_age_input"),
        "max_age": st.sidebar.number_input("最高年齡", min_value=18, max_value=100, key="max_age_input"),
        "gender": st.sidebar.selectbox("性別", ["男性", "女性"], key="gender_input"),
        "currency": st.sidebar.selectbox("幣別", ["台幣", "美元"], key="currency_input"),
        "term": st.sidebar.number_input("保障年期", min_value=1, max_value=50, key="term_input"),
        "coverage": st.sidebar.number_input("保額", min_value=100000, key="coverage_input"),
        "premium": st.sidebar.number_input("保費", min_value=0, key="premium_input")
    }
    if st.sidebar.button("新增", key="add_button"):
        policies = policies.append(new_policy, ignore_index=True)
        policies.to_csv("policies.csv", index=False)
        st.success("保單新增成功！")

elif action == "修改保單":
    st.sidebar.header("修改保單")
    policy_id = st.sidebar.number_input("輸入要修改的保單編號", min_value=1, max_value=len(policies), key="policy_id_edit_input")
    policy = policies[policies["policy_id"] == policy_id]
    if not policy.empty:
        st.sidebar.write("當前保單資訊：", policy)
        updated_policy = {
            "policy_id": policy_id,
            "company": st.sidebar.text_input("公司名稱", value=policy["company"].values[0], key="company_edit_input"),
            "product_name": st.sidebar.text_input("商品名稱", value=policy["product_name"].values[0], key="product_name_edit_input"),
            "term_options": st.sidebar.text_input("年期選擇（用斜杠分隔）", value=policy["term_options"].values[0], key="term_options_edit_input"),
            "policy_type": st.sidebar.text_input("保單類型", value=policy["policy_type"].values[0], key="policy_type_edit_input"),
            "min_age": st.sidebar.number_input("最低年齡", min_value=18, max_value=100, value=policy["min_age"].values[0], key="min_age_edit_input"),
            "max_age": st.sidebar.number_input("最高年齡", min_value=18, max_value=100, value=policy["max_age"].values[0], key="max_age_edit_input"),
            "gender": st.sidebar.selectbox("性別", ["男性", "女性"], index=0 if policy["gender"].values[0] == "男性" else 1, key="gender_edit_input"),
            "currency": st.sidebar.selectbox("幣別", ["台幣", "美元"], index=0 if policy["currency"].values[0] == "台幣" else 1, key="currency_edit_input"),
            "term": st.sidebar.number_input("保障年期", min_value=1, max_value=50, value=policy["term"].values[0], key="term_edit_input"),
            "coverage": st.sidebar.number_input("保額", min_value=100000, value=policy["coverage"].values[0], key="coverage_edit_input"),
            "premium": st.sidebar.number_input("保費", min_value=0, value=policy["premium"].values[0], key="premium_edit_input")
        }
        if st.sidebar.button("修改", key="edit_button"):
            policies.loc[policies["policy_id"] == policy_id] = pd.Series(updated_policy)
            policies.to_csv("policies.csv", index=False)
            st.success("保單修改成功！")
    else:
        st.sidebar.error("找不到該保單編號！")

elif action == "刪除保單":
    st.sidebar.header("刪除保單")
    policy_id = st.sidebar.number_input("輸入要刪除的保單編號", min_value=1, max_value=len(policies), key="policy_id_delete_input")
    if st.sidebar.button("刪除", key="delete_button"):
        policies = policies[policies["policy_id"] != policy_id]
        policies.to_csv("policies.csv", index=False)
        st.success("保單刪除成功！")

# 用戶輸入
st.header("保單推薦")
age = st.number_input("年齡", min_value=18, max_value=100, value=30, key="age_input")
gender = st.selectbox("性別", ["男性", "女性"], key="gender_recommend_input")
currency = st.selectbox("幣別", ["台幣", "美元"], key="currency_recommend_input")
term = st.number_input("保障年期", min_value=1, max_value=50, value=20, key="term_recommend_input")
coverage = st.number_input("保額", min_value=100000, value=1000000, key="coverage_recommend_input")

# 篩選適合的保單
filtered_policies = policies[
    (policies["min_age"] <= age) &
    (policies["max_age"] >= age) &
    (policies["gender"] == gender) &
    (policies["currency"] == currency) &
    (policies["term"] == term)
]

# 計算推薦順序（按保費低到高排序）
recommended_policies = filtered_policies.sort_values(by="premium")

# 顯示推薦結果
st.write("推薦保單", recommended_policies)
