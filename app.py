import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================
# 初始化 session state 變數
# ==========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None  # "admin" 或 "user"
    st.session_state.creds = None

# ==========================
# 讀取 secrets 憑證設定
# ==========================
admin_creds = st.secrets.admin
user_creds = st.secrets.user

def is_within_date_range(start_date_str, end_date_str):
    """檢查目前日期是否在允許使用期間內"""
    current_date = datetime.now().date()
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    return start_date <= current_date <= end_date

# ==========================
# 初始化商品資料（存放於 Session State）
# ==========================
if "df_products" not in st.session_state:
    st.session_state.df_products = pd.DataFrame(
        columns=["公司名", "商品名", "幣別", "年期", "年繳保費", "總繳保費", "90歲現價", "90歲保額", "內含豁免"]
    )

# ==========================
# 登入介面（未登入時顯示）
# ==========================
def login_ui():
    st.title("insurtech 用戶登入系統")
    # 身份選擇（管理者或一般用戶）
    role = st.sidebar.selectbox("請選擇您的身份", options=["admin", "user"])
    
    st.subheader("請輸入您的登入資訊")
    input_login_account = st.text_input("登入帳號")
    input_login_password = st.text_input("登入密碼", type="password")
    
    if st.button("登入"):
        # 根據所選身份讀取對應的憑證
        creds = admin_creds if role == "admin" else user_creds
        # 驗證帳號與密碼
        if input_login_account == creds.login_account and input_login_password == creds.login_password:
            if is_within_date_range(creds.start_date, creds.end_date):
                st.success(f"{role} 登入成功！")
                st.write("歡迎，", creds.username)
                st.write("使用期間：", creds.start_date, "到", creds.end_date)
                st.session_state.logged_in = True
                st.session_state.user_role = role
                st.session_state.creds = creds
                # 登入成功後重新執行，直接進入後續介面
                st.experimental_rerun()
            else:
                st.error("登入失敗：目前不在允許的使用日期範圍內。")
        else:
            st.error("登入失敗：請確認登入帳號及登入密碼是否正確。")

# ==========================
# 管理者專區：商品管理介面
# ==========================
def admin_ui():
    st.subheader("管理者專區 - 商品管理")
    action = st.selectbox("選擇操作", options=["新增商品", "修改商品", "刪除商品"])
    
    if action == "新增商品":
        st.markdown("### 新增商品")
        with st.form("新增商品表單"):
            company = st.text_input("公司名")
            product = st.text_input("商品名")
            currency = st.selectbox("幣別", options=["USD", "TWD"])
            term = st.number_input("年期", min_value=1, max_value=100, value=10)
            annual_premium = st.number_input("年繳保費", min_value=0.0, value=0.0)
            total_premium = st.number_input("總繳保費", min_value=0.0, value=0.0)
            value_90 = st.number_input("90歲現價", min_value=0.0, value=0.0)
            coverage_90 = st.number_input("90歲保額", min_value=0.0, value=0.0)
            waiver = st.checkbox("內含豁免")
            submitted = st.form_submit_button("新增")
            if submitted:
                new_row = {
                    "公司名": company,
                    "商品名": product,
                    "幣別": currency,
                    "年期": term,
                    "年繳保費": annual_premium,
                    "總繳保費": total_premium,
                    "90歲現價": value_90,
                    "90歲保額": coverage_90,
                    "內含豁免": waiver
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
                format_func=lambda x: f"{st.session_state.df_products.loc[x, '公司名']} - {st.session_state.df_products.loc[x, '商品名']}"
            )
            current_data = st.session_state.df_products.loc[selected_index]
            with st.form("修改商品表單"):
                company = st.text_input("公司名", value=current_data["公司名"])
                product = st.text_input("商品名", value=current_data["商品名"])
                currency = st.selectbox("幣別", options=["USD", "TWD"],
                                        index=0 if current_data["幣別"]=="USD" else 1)
                term = st.number_input("年期", min_value=1, max_value=100, value=int(current_data["年期"]))
                annual_premium = st.number_input("年繳保費", min_value=0.0, value=float(current_data["年繳保費"]))
                total_premium = st.number_input("總繳保費", min_value=0.0, value=float(current_data["總繳保費"]))
                value_90 = st.number_input("90歲現價", min_value=0.0, value=float(current_data["90歲現價"]))
                coverage_90 = st.number_input("90歲保額", min_value=0.0, value=float(current_data["90歲保額"]))
                waiver = st.checkbox("內含豁免", value=bool(current_data["內含豁免"]))
                submitted = st.form_submit_button("修改")
                if submitted:
                    st.session_state.df_products.loc[selected_index] = {
                        "公司名": company,
                        "商品名": product,
                        "幣別": currency,
                        "年期": term,
                        "年繳保費": annual_premium,
                        "總繳保費": total_premium,
                        "90歲現價": value_90,
                        "90歲保額": coverage_90,
                        "內含豁免": waiver
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
                format_func=lambda x: f"{st.session_state.df_products.loc[x, '公司名']} - {st.session_state.df_products.loc[x, '商品名']}"
            )
            if st.button("刪除商品"):
                st.session_state.df_products = st.session_state.df_products.drop(selected_index).reset_index(drop=True)
                st.success("商品刪除成功！")
    
    st.markdown("### 目前商品資料")
    st.dataframe(st.session_state.df_products)

# ==========================
# 用戶專區：商品搜尋與瀏覽介面
# ==========================
def user_ui():
    st.subheader("用戶專區 - 商品資訊")
    search_term = st.text_input("請輸入商品名稱關鍵字以搜尋")
    if search_term:
        filtered_df = st.session_state.df_products[
            st.session_state.df_products["商品名"].str.contains(search_term, case=False, na=False)
        ]
    else:
        filtered_df = st.session_state.df_products
    st.dataframe(filtered_df)

# ==========================
# 主程式流程
# ==========================
if not st.session_state.logged_in:
    login_ui()
else:
    # 登入後側邊欄提供登出選項
    st.sidebar.write("已登入：", st.session_state.creds.username)
    if st.sidebar.button("登出"):
        st.session_state.logged_in = False
        st.experimental_rerun()
    
    # 根據身份顯示對應介面
    if st.session_state.user_role == "admin":
        admin_ui()
    else:
        user_ui()
