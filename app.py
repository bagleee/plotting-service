import streamlit as st
import sqlite3

# DataBase SetUp

DATABASE = 'users.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

def register_user(username, password):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                    (username, password))
    conn.commit()
    conn.close()
    return True

def verify_user(username, password):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data and user_data[2]==password:
        return True
    return False


# Main block

def main():
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = None
    
    if not st.session_state.logged_in:
        auth_type = st.sidebar.radio("Choose the action", ["Login", "Register"])
        
        if auth_type == "Login":
            with st.form("login_form"):
                username = st.text_input("User name")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login")
                
                if submit:
                    if verify_user(username, password):
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.experimental_rerun()
                    else:
                        st.error("Invalid username or password")
        else:
            with st.form("register_form"):
                username = st.text_input("User name")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Create account")
                
                if submit:
                    if register_user(username, password):
                        st.success("Registration was successful! Now you can log in.")
                    else:
                        st.error("This username is unavailable!")
    else:
        st.sidebar.title(f"Welcome, {st.session_state.username}!")
        if st.sidebar.button("Log out"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.experimental_rerun()

if __name__ == '__main__':
    main()