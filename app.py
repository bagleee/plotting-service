import streamlit as st

def main():
    
    auth_type = st.sidebar.radio("Choose the action", ["Login", "Register"])
    
    if auth_type == "Login":
        with st.form("login_form"):
            username = st.text_input("User name")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                print('LogIn',username, password)
    else:
        with st.form("register_form"):
            username = st.text_input("User name")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Create account")
            
            if submit:
                print('Register',username, password)

if __name__ == '__main__':
    main()