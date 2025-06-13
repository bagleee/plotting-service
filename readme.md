# Function Plotter with User Authentication

### General Description  

This is a web application for plotting mathematical functions, featuring user registration and the ability to save query history. Users can input functions using Python syntax (e.g., `sin(x)` or `x**2 + 3*x + 2`), set the range of values for the $x$-axis, and visualize the results using an interactive graph.  

Supported elementary functions: 
`abs, sin, cos, tan, exp, log, sqrt`.

## Technical Description  

User data is stored in an `SQLite` database. Passwords are stored in hashed form. Graph plotting history is recorded in a separate table within the database.  

The web interface is built using `Streamlit`. Graphs are rendered using `Plotly`.  

The application is written in `Python` and deployed in a `Docker` container. A dedicated `bash` script is used for this purpose.

### Project Files:  

1. **app.py** - The main application file. Implements user authentication system, SQLite database operations, and graph plotting logic.  

2. **Dockerfile** - Configuration for Docker image build. Installs Python 3.9 and dependencies, sets up working directory, exposes port 8501 for Streamlit.  

3. **requirements.txt** - List of Python dependencies.  

4. **run.sh** - Application launch script that builds Docker image, configures environment variables and runs container with mounted database directory.  

### How to Run:  
1. Execute the command:  
   ```bash
   chmod +x run.sh && ./run.sh
   ```  
2. Open http://localhost:8501 in your browser
