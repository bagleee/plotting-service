import streamlit as st
import sqlite3
import plotly.graph_objects as go
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash
import matplotlib.pyplot as plt
import numpy as np
import os

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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_plots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            function TEXT NOT NULL,
            x_min REAL NOT NULL,
            x_max REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
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

def save_plot_to_history(user_id, func_str, x_range):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO user_plots (user_id, function, x_min, x_max) VALUES (?, ?, ?, ?)",
        (user_id, func_str, x_range[0], x_range[1])
    )
    conn.commit()
    conn.close()

def get_user_plots(user_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, function, x_min, x_max, timestamp FROM user_plots WHERE user_id = ? ORDER BY timestamp DESC",
        (user_id,)
    )
    plots = cursor.fetchall()
    conn.close()
    return plots

# Plotting

def simple_to_latex(func_str):
    replacements = {
        "sin": r"\sin",
        "cos": r"\cos",
        "tan": r"\tan",
        "exp": r"\exp",
        "log": r"\log",
        "sqrt": r"\sqrt",
        "**": "^",
        "*": r"\cdot ",
    }
    result = func_str
    for k, v in replacements.items():
        result = result.replace(k, v)
    return f"${result}$"

def plot_function(func_str, x_range=(-10, 10), num_points=1000):
    try:
        x = np.linspace(x_range[0], x_range[1], num_points)
        y = eval(func_str, {
            'np': np,
            'x': x,
            'sin': np.sin,
            'cos': np.cos,
            'tan': np.tan,
            'exp': np.exp,
            'log': np.log,
            'sqrt': np.sqrt,
        })
        
        df = pd.DataFrame({'x': x, 'y': y})
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['x'],
            y=df['y'],
            mode='lines',
            name=func_str,
            line=dict(width=2)
        ))
        
        fig.update_layout(
            title=f'{simple_to_latex(func_str)}',
            xaxis_title='X',
            yaxis_title='Y',
            hovermode='x unified',
            template='plotly_white',
            margin=dict(l=40, r=40, t=40, b=40),
            height=600
        )
        
        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1x", step="all", stepmode="backward"),
                    dict(count=5, label="5x", step="all", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Plotting error: {e}")
        
# Main block

def main():
    st.set_page_config(page_title="Function plotter", layout="wide")
    
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
        
        if st.sidebar.checkbox("Display the request history"):
            user_id = get_user_id(st.session_state.username)
            plots = get_user_plots(user_id)
            
            if plots:
                st.sidebar.subheader("Request history")
                for plot in plots:
                    if st.sidebar.button(f"{plot[1]} [{plot[2]}, {plot[3]}]", key=f"hist_{plot[0]}"):
                        plot_function(plot[1], (plot[2], plot[3]))
            else:
                st.sidebar.write("The request history is empty")
        
        with st.form("function_form"):
            func_str = st.text_input("Enter the expression of x (e.g., sin(x) or x**2 + 3*x + 2)", "sin(x)")
            x_min = st.number_input("Min x", value=-10.0)
            x_max = st.number_input("Max x", value=10.0)
            submit = st.form_submit_button("Make plot")
            
            if submit:
                user_id = get_user_id(st.session_state.username)
                save_plot_to_history(user_id, func_str, (x_min, x_max))
                plot_function(func_str, (x_min, x_max))

if __name__ == '__main__':
    main()