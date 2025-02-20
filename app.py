import streamlit as st
import pandas as pd
from datetime import datetime

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
# 模擬商品資料庫
# ==========================
product_data = [
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

df_products = pd.DataFrame(product_data)

# ==========================
# 登入系統介面
# ==========================
st.title("insurtech 用戶登入系統")

# 身份選擇 (管理者或一般用戶)
role = st.sidebar.selectbox("請選擇您的身份", options=["admin", "user"])

# 輸入登入資訊 (僅有帳號與密碼)
st.subheader("請輸入您的登入資訊")
input_login_account = st.text_input("登入帳號")
input_login_password = st.text_input("登入密碼", type="password")

if st.button("登入"):
    # 根據所選身份讀取對應的憑證
    if role == "admin":
        creds = admin_creds
    else:
        creds = user_creds

    # 驗證帳號與密碼
    if input_login_account == creds.login_account and input_login_password == creds.login_password:
        # 驗證使用期間
        if is_within_date_range(creds.start_date, creds.end_date):
            st.success(f"{role} 登入成功！")
            st.write("歡迎, ", creds.username)
            st.write("使用期間：", creds.start_date, "到", creds.end_date)
            
            # ==========================
            # 登入成功後展示不同內容
            # ==========================
            if role == "admin":
                st.subheader("管理者專區")
                st.write("這裡您可以新增、修改、刪除商品資料。")
                # 管理者可以看到完整的商品資訊與管理操作提示
                st.dataframe(df_products)
                st.write("（管理功能示意：請進一步擴充管理表單）")
            else:
                st.subheader("用戶專區")
                st.write("這裡僅供搜尋和閱讀商品資料。")
                
                # 用戶可透過簡單搜尋功能來篩選商品
                search_term = st.text_input("請輸入商品名稱關鍵字以搜尋")
                if search_term:
                    # 以不區分大小寫方式進行關鍵字搜尋
                    filtered_df = df_products[df_products["Product"].str.contains(search_term, case=False)]
                else:
                    filtered_df = df_products
                st.dataframe(filtered_df)
        else:
            st.error("登入失敗：目前不在允許的使用日期範圍內。")
    else:
        st.error("登入失敗：請確認登入帳號及登入密碼是否正確。")
