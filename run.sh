#!/bin/bash

sudo docker build -t streamlit-app .
sudo docker run -p 8501:8501 --rm -it streamlit-app