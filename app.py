import streamlit as st
from datetime import datetime

# 讀取 secrets 檔案中的設定值
creds = st.secrets.credentials

# 定義檢查目前日期是否在使用期間內的函數
def is_within_date_range(start_date_str, end_date_str):
    current_date = datetime.now().date()
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    return start_date <= current_date <= end_date

# 頁面標題
st.title("insurtech 用戶登入系統")

# 輸入登入資訊
st.subheader("請輸入您的登入資訊")
input_username = st.text_input("用戶名稱")
input_login_account = st.text_input("登入帳號")
input_login_password = st.text_input("登入密碼", type="password")

# 登入按鈕
if st.button("登入"):
    # 檢查用戶名稱、登入帳號與登入密碼是否正確
    if (input_username == creds.username and 
        input_login_account == creds.login_account and 
        input_login_password == creds.login_password):
        
        # 檢查目前日期是否在允許使用期間內
        if is_within_date_range(creds.start_date, creds.end_date):
            st.success("登入成功！")
            st.write("歡迎, ", input_username)
            st.write("系統使用期間：", creds.start_date, "到", creds.end_date)
        else:
            st.error("登入失敗：目前不在允許的使用日期範圍內。")
    else:
        st.error("登入失敗：請確認用戶名稱、登入帳號及登入密碼是否正確。")
