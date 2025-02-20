import streamlit as st
import pandas as pd
from datetime import datetime

# --------------------------
# 初始化 Session State 變數
# --------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None  # "admin" 或 "user"
    st.session_state.creds = None

# --------------------------
# 讀取 secrets 憑證設定
# --------------------------
admin_creds = st.secrets.admin
user_creds = st.secrets.user

def is_within_date_range(start_date_str, end_date_str):
    """檢查目前日期是否在允許使用期間內"""
    current_date = datetime.now().date()
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    return start_date <= current_date <= end_date

# --------------------------
# 初始化保險商品比較表資料（存放於 Session State）
# --------------------------
if "df_products" not in st.session_state:
    st.session_state.df_products = pd.DataFrame(
        columns=["公司", "商品", "幣別", "年期", "保戶年齡", "保戶性別", "首年保費", "總繳保費", "90歲保額", "CP值%"]
    )

# --------------------------
# 登入介面 (未登入時顯示)
# --------------------------
def login_ui():
    st.title("保險商品比較表 登入")
    # 身份選擇 (在側邊欄)
    role = st.sidebar.selectbox("請選擇您的身份", options=["admin", "user"])
    
    st.subheader("請輸入您的登入資訊")
    input_login_account = st.text_input("登入帳號")
    input_login_password = st.text_input("登入密碼", type="password")
    
    if st.button("登入"):
        # 根據所選身份讀取對應的憑證
        creds = admin_creds if role == "admin" else user_creds
        if input_login_account == creds.login_account and input_login_password == creds.login_password:
            if is_within_date_range(creds.start_date, creds.end_date):
                st.success(f"{role} 登入成功！")
                st.session_state.logged_in = True
                st.session_state.user_role = role
                st.session_state.creds = creds
            else:
                st.error("登入失敗：目前不在允許的使用日期範圍內。")
        else:
            st.error("登入失敗：請確認登入帳號及登入密碼是否正確。")

# --------------------------
# 管理者專區：商品管理介面
# --------------------------
def admin_ui():
    st.title("保險商品比較表 - 管理者專區")
    st.write("歡迎，", st.session_state.creds.username)
    # 提供登出按鈕
    if st.sidebar.button("登出"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.creds = None
        st.experimental_rerun()
        
    # 選擇操作項目
    action = st.selectbox("選擇操作", options=["新增商品", "修改商品", "刪除商品", "讀取商品"])
    
    if action == "新增商品":
        st.markdown("### 新增商品")
        with st.form("新增商品表單"):
            company = st.text_input("公司")
            product = st.text_input("商品")
            currency = st.selectbox("幣別", options=["USD", "TWD"])
            term = st.number_input("年期", min_value=1, max_value=100, value=10)
            insured_age = st.number_input("保戶年齡", min_value=0, value=30)
            insured_gender = st.selectbox("保戶性別", options=["Male", "Female"])
            first_premium = st.number_input("首年保費", min_value=0.0, value=0.0)
            total_premium = st.number_input("總繳保費", min_value=0.0, value=0.0)
            coverage_90 = st.number_input("90歲保額", min_value=0.0, value=0.0)
            cp_value = st.number_input("CP值%", min_value=0.0, value=0.0)
            submitted = st.form_submit_button("新增")
            if submitted:
                new_row = {
                    "公司": company,
                    "商品": product,
                    "幣別": currency,
                    "年期": term,
                    "保戶年齡": insured_age,
                    "保戶性別": insured_gender,
                    "首年保費": first_premium,
                    "總繳保費": total_premium,
                    "90歲保額": coverage_90,
                    "CP值%": cp_value
                }
                new_row_df = pd.DataFrame([new_row])
                st.session_state.df_products = pd.concat(
                    [st.session_state.df_products, new_row_df], ignore_index=True
                )
                st.success("商品新增成功！")
                
    elif action == "修改商品":
        st.markdown("### 修改商品")
        if st.session_state.df_products.empty:
            st.warning("目前沒有商品資料可供修改。")
        else:
            selected_index = st.selectbox(
                "選擇要修改的商品",
                options=st.session_state.df_products.index,
                format_func=lambda x: f"{st.session_state.df_products.loc[x, '公司']} - {st.session_state.df_products.loc[x, '商品']}"
            )
            current_data = st.session_state.df_products.loc[selected_index]
            with st.form("修改商品表單"):
                company = st.text_input("公司", value=current_data["公司"])
                product = st.text_input("商品", value=current_data["商品"])
                currency = st.selectbox("幣別", options=["USD", "TWD"],
                                        index=0 if current_data["幣別"]=="USD" else 1)
                term = st.number_input("年期", min_value=1, max_value=100, value=int(current_data["年期"]))
                insured_age = st.number_input("保戶年齡", min_value=0, value=int(current_data["保戶年齡"]))
                insured_gender = st.selectbox("保戶性別", options=["Male", "Female"],
                                              index=0 if current_data["保戶性別"]=="Male" else 1)
                first_premium = st.number_input("首年保費", min_value=0.0, value=float(current_data["首年保費"]))
                total_premium = st.number_input("總繳保費", min_value=0.0, value=float(current_data["總繳保費"]))
                coverage_90 = st.number_input("90歲保額", min_value=0.0, value=float(current_data["90歲保額"]))
                cp_value = st.number_input("CP值%", min_value=0.0, value=float(current_data["CP值%"]))
                submitted = st.form_submit_button("修改")
                if submitted:
                    st.session_state.df_products.loc[selected_index] = {
                        "公司": company,
                        "商品": product,
                        "幣別": currency,
                        "年期": term,
                        "保戶年齡": insured_age,
                        "保戶性別": insured_gender,
                        "首年保費": first_premium,
                        "總繳保費": total_premium,
                        "90歲保額": coverage_90,
                        "CP值%": cp_value
                    }
                    st.success("商品修改成功！")
    
    elif action == "刪除商品":
        st.markdown("### 刪除商品")
        if st.session_state.df_products.empty:
            st.warning("目前沒有商品資料可供刪除。")
        else:
            selected_index = st.selectbox(
                "選擇要刪除的商品",
                options=st.session_state.df_products.index,
                format_func=lambda x: f"{st.session_state.df_products.loc[x, '公司']} - {st.session_state.df_products.loc[x, '商品']}"
            )
            if st.button("刪除商品"):
                st.session_state.df_products = st.session_state.df_products.drop(selected_index).reset_index(drop=True)
                st.success("商品刪除成功！")
    
    elif action == "讀取商品":
        st.markdown("### 目前商品資料")
        st.dataframe(st.session_state.df_products)

# --------------------------
# 使用者專區：僅讀取商品列表
# --------------------------
def user_ui():
    st.title("保險商品比較表 - 使用者專區")
    st.write("歡迎，", st.session_state.creds.username)
    if st.sidebar.button("登出"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.creds = None
        st.experimental_rerun()
    st.markdown("### 商品列表")
    search_term = st.text_input("請輸入商品名稱關鍵字以搜尋")
    if search_term:
        filtered_df = st.session_state.df_products[
            st.session_state.df_products["商品"].str.contains(search_term, case=False, na=False)
        ]
    else:
        filtered_df = st.session_state.df_products
    st.dataframe(filtered_df)

# --------------------------
# 主程式流程
# --------------------------
if not st.session_state.logged_in:
    login_ui()
else:
    if st.session_state.user_role == "admin":
        admin_ui()
    else:
        user_ui()
