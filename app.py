import streamlit as st
from datetime import datetime

# 讀取 secrets 中的兩組憑證
admin_creds = st.secrets.admin
user_creds = st.secrets.user

def is_within_date_range(start_date_str, end_date_str):
    """檢查目前日期是否在允許使用期間內"""
    current_date = datetime.now().date()
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    return start_date <= current_date <= end_date

# 頁面標題
st.title("insurtech 用戶登入系統")

# 身份選擇 (管理者或一般用戶)
role = st.sidebar.selectbox("請選擇您的身份", options=["admin", "user"])

# 輸入登入資訊 (僅有帳號與密碼)
st.subheader("請輸入您的登入資訊")
input_login_account = st.text_input("登入帳號")
input_login_password = st.text_input("登入密碼", type="password")

# 登入按鈕
if st.button("登入"):
    # 根據所選身份讀取對應的憑證
    if role == "admin":
        creds = admin_creds
    else:
        creds = user_creds

    # 檢查登入帳號與密碼是否正確
    if (input_login_account == creds.login_account and 
        input_login_password == creds.login_password):
        
        # 檢查目前日期是否在允許的使用期間內
        if is_within_date_range(creds.start_date, creds.end_date):
            st.success(f"{role} 登入成功！")
            st.write("歡迎, ", creds.username)
            st.write("使用期間：", creds.start_date, "到", creds.end_date)
            
            # 根據身份顯示不同的介面內容
            if role == "admin":
                st.subheader("管理者專區")
                st.write("這裡您可以新增、修改、刪除商品資料。")
            else:
                st.subheader("用戶專區")
                st.write("這裡僅供搜尋和閱讀商品資料。")
        else:
            st.error("登入失敗：目前不在允許的使用日期範圍內。")
    else:
        st.error("登入失敗：請確認登入帳號及登入密碼是否正確。")
