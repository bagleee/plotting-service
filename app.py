import streamlit as st
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import matplotlib.pyplot as plt
import numpy as np

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
    password_hash = generate_password_hash(password)
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                     (username, password_hash))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def verify_user(username, password):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data and check_password_hash(user_data[2], password):
        return True
    return False

def get_user_id(username):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user_id = cursor.fetchone()[0]
    conn.close()
    return user_id


# Plotting

def plot_function(func_str, x_range=(-10, 10), num_points=1000):
    try:
        x = np.linspace(x_range[0], x_range[1], num_points)
        y = eval(func_str, {'np': np, 'x': x})
        
        fig, ax = plt.subplots()
        ax.plot(x, y)
        ax.set_title(f"Function: {func_str}")
        ax.grid(True)
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Plotting error: {e}")
      


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
            
        st.title("Function plotter")
                
        with st.form("function_form"):
            func_str = st.text_input("Enter the expression of x (e.g., np.sin(x) or x**2 + 3*x + 2)", "np.sin(x)")
            x_min = st.number_input("Min x", value=-10.0)
            x_max = st.number_input("Max x", value=10.0)
            submit = st.form_submit_button("Make plot")
            
            if submit:
                user_id = get_user_id(st.session_state.username)
                plot_function(func_str, (x_min, x_max))

if __name__ == '__main__':
    main()