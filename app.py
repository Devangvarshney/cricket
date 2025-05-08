import streamlit as st
import pandas as pd
from joblib import load
import sklearn
import pyarrow as pa
import base64
from groq import Groq

# Page Config
st.set_page_config(
    page_title="IPL Match Win Predictor",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="collapsed"
)
GROQ_API_KEY = "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"

# Initialize the Groq client
client = Groq(api_key=GROQ_API_KEY)

# Function to load and encode background image
def add_bg_from_url():
    st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url("https://static.vecteezy.com/system/resources/previews/007/164/537/original/cricket-stadium-background-with-bright-stadium-lights-vector.jpg");
             background-attachment: fixed;
             background-size: cover;
             background-position: center;
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

# Function to create custom CSS styles
def apply_custom_styles():
    st.markdown(
        """
        <style>
        /* Main container */
        .main-container {
            background-color: rgba(10, 10, 20, 0.85);
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.6);
            margin-bottom: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(5px);
        }
        
        /* Header styles */
        .main-header {
            background-image: linear-gradient(135deg, #3a0CA3, #4361EE, #4CC9F0);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        }
        
        .main-title {
            font-size: 48px;
            font-weight: 800;
            color: white;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
            margin-bottom: 10px;
            font-family: 'Montserrat', sans-serif;
        }
        
        .sub-title {
            font-size: 22px;
            color: #E6F1FF;
            font-style: italic;
            font-weight: 400;
        }
        
        /* Section headers */
        .section-header {
            background-image: linear-gradient(90deg, #0077B6, #0096C7);
            color: white;
            padding: 12px 20px;
            border-radius: 10px;
            font-size: 22px;
            font-weight: 600;
            margin: 25px 0 15px 0;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        }
        
        /* Form elements */
        .stSelectbox, .stNumberInput {
            margin-bottom: 15px;
        }
        
        /* Team columns */
        .team-column {
            background-color: rgba(30, 30, 50, 0.7);
            padding: 15px;
            border-radius: 15px;
            border: 1px solid rgba(100, 100, 255, 0.2);
        }
        
        /* Predict button */
        .stButton > button {
            background-image: linear-gradient(135deg, #F72585, #B5179E);
            color: white;
            font-weight: 700;
            font-size: 18px;
            padding: 12px 30px;
            border-radius: 50px;
            border: none;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
            width: 100%;
            margin-top: 10px;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(0, 0, 0, 0.4);
        }
        
        /* Results container */
        .results-container {
            background-color: rgba(20, 20, 40, 0.8);
            border-radius: 15px;
            padding: 25px;
            margin-top: 30px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        }
        
        /* Team probability cards */
        .team-card {
            background-image: linear-gradient(135deg, #3a0CA3, #4361EE);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
        }
        
        .team-card-title {
            font-size: 18px;
            color: white;
            margin-bottom: 10px;
        }
        
        .team-card-value {
            font-size: 36px;
            font-weight: 700;
            color: white;
        }
        
        /* Progress bars */
        .custom-progress {
            height: 25px;
            border-radius: 50px;
            margin: 20px 0;
        }
        
        /* Footer */
        .footer {
            background-color: rgba(10, 10, 20, 0.7);
            padding: 20px;
            border-radius: 10px;
            margin-top: 40px;
            text-align: center;
            font-size: 14px;
            color: #CCC;
        }
        
        /* Team logos */
        .team-logo {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            object-fit: cover;
            margin: 0 auto 15px auto;
            display: block;
            background-color: white;
            padding: 5px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        }
        
        /* Match situation summary */
        .match-summary {
            background-color: rgba(25, 25, 45, 0.8);
            border-radius: 15px;
            padding: 20px;
            margin-top: 20px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        }
        
        .summary-item {
            display: flex;
            justify-content: space-between;
            padding: 10px 15px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .summary-label {
            font-weight: 600;
            color: #ADB5BD;
        }
        
        .summary-value {
            font-weight: 700;
            color: white;
        }
        
        /* Debug sections (hidden by default) */
        .debug-section {
            display: none;
        }
        
        /* Override default Streamlit markdown */
        .css-18e3th9 {
            padding-top: 0;
            padding-bottom: 0;
        }
        
        /* Team labels */
        .team-label {
            background-color: rgba(0, 0, 0, 0.3);
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: 600;
            display: inline-block;
            margin-bottom: 10px;
        }
        
        /* Batting and bowling indicator */
        .role-indicator {
            font-size: 14px;
            padding: 3px 12px;
            border-radius: 20px;
            font-weight: 600;
            display: inline-block;
            margin-left: 10px;
        }
        
        .batting-indicator {
            background-color: #4CC9F0;
            color: #000;
        }
        
        .bowling-indicator {
            background-color: #F72585;
            color: white;
        }
        /* Chatbot Styles */
        .chat-button {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 60px;
            height: 60px;
            background-image: linear-gradient(135deg, #4361EE, #3A0CA3);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
            z-index: 1000;
            transition: all 0.3s ease;
        }
        
        .chat-button:hover {
            transform: scale(1.1);
        }
        
        .chat-icon {
            color: white;
            font-size: 24px;
        }
        
        .chat-container {
            position: fixed;
            bottom: 100px;
            right: 30px;
            width: 350px;
            height: 500px;
            background-color: rgba(20, 20, 40, 0.95);
            border-radius: 15px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.6);
            z-index: 999;
            display: none;
            flex-direction: column;
            overflow: hidden;
            border: 1px solid rgba(100, 100, 255, 0.2);
        }
        
        .chat-header {
            background-image: linear-gradient(135deg, #3a0CA3, #4361EE);
            padding: 15px;
            color: white;
            font-weight: 600;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .chat-close {
            cursor: pointer;
            font-size: 18px;
        }
        
        .chat-messages {
            flex-grow: 1;
            padding: 15px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
        }
        
        .chat-input-container {
            padding: 10px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            display: flex;
        }
        
        .chat-input {
            flex-grow: 1;
            padding: 10px;
            border: none;
            border-radius: 20px;
            background-color: rgba(255, 255, 255, 0.1);
            color: white;
        }
        
        .chat-input:focus {
            outline: none;
            background-color: rgba(255, 255, 255, 0.2);
        }
        
        .chat-send {
            background-image: linear-gradient(135deg, #F72585, #B5179E);
            border: none;
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            margin-left: 10px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .user-message, .bot-message {
            max-width: 80%;
            padding: 10px 15px;
            border-radius: 15px;
            margin-bottom: 10px;
            word-wrap: break-word;
        }
        
        .user-message {
            background-image: linear-gradient(135deg, #4361EE, #3A0CA3);
            color: white;
            align-self: flex-end;
        }
        
        .bot-message {
            background-color: rgba(255, 255, 255, 0.1);
            color: white;
            align-self: flex-start;
        }
        
        /* Chatbot toggle script */
        .chat-toggle-script {
            display: none;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Import team logos dictionary
def get_team_logo_url(team_name):
    team_logos = {
        'Chennai Super Kings': 'data:image/jpeg;base64,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',
        'Mumbai Indians': 'data:image/jpeg;base64,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',
        'Royal Challengers Bangalore': 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBwgHBgkIBwgKCgkLDRYPDQwMDRsUFRAWIB0iIiAdHx8kKDQsJCYxJx8fLT0tMTU3Ojo6Iys/RD84QzQ5OjcBCgoKDQwNGg8PGjclHyU3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3N//AABEIAMAAzAMBEQACEQEDEQH/xAAbAAEAAgMBAQAAAAAAAAAAAAAABQYDBAcBAv/EADsQAAEEAQMDAgMFBwMDBQAAAAEAAgMEEQUSIQYxQRNRImFxFCMyQoEHUpGhsdHwJHLBFYLhFiY0YmP/xAAaAQEAAwEBAQAAAAAAAAAAAAAAAwQFAgEG/8QAOBEAAgIBAwEFBQcDAwUAAAAAAAECAxEEITESBRNBUWEicYGRoSMyQrHB0fAUM+FSgvEVJDRDcv/aAAwDAQACEQMRAD8A7igCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAZQHy2RjnOa1zS5pw4A9kBr3NRpUW7rluCAf/AKSBv9UBWepOrhVZDFonoWpZXxNfZMmYqzZJAwPdjv3Jx7AknweXJJ4Z6llZLTFYgkdtjnje72a4FdHhnQBAebm5xuGfbKA9QBAEAQBAEAQBAEAQBAEAQBAEAQBAEBinljgjfLM4MjY0uc49gAgOey6m2rqw6mke+tDbtxVzBguMkO0gFzR+c8OAAyAAPdU4apT1HQuMErr6YZY6j1jR9Ziuys0yxDqWmRtlit2IGj03kjYzIJOXnDdmM/F2VltThlPYj3TNyjDFILZkgqgvO2VjIgDn9x+DhxGcEj2WRY+C3ErtuHTquoj0LVarZP3kHotbHJweSCO48YXKtuh7UfA7cYtYZa+g9ct6lb1KpcuC19k2AOLA1zXEZIOPkW9/n7FammslbWpyRUtioS6UTfU2oSUNKc6qf9TK9sMPGcOccA49h3/RTTl0RcjhLLwVTVtJjj0mzMy5DWnbGXO1C457nNP73Dh8/wCXCzqb5zn1bk860kWvpS+dT0CpaJLnOZtL+cPI43A4GQcZB+a0+dyuS6AIAgCAIAgCAIAgCAIAgCAIAgCAICC6zcxvTd/e9rR6Y4P5uR8PzJ7YXMvus9XJXdGqh95zbbMhlo3qpcOdrmbex8tLiMeAWr5xzxFSi/DpfwZda5yQMUFTSNQ1izarQ2JIm3L5sOb99B6ewYa7zkOaRntythrqrjjngrZxIkujmxu6VM1KV7p5g4ull3Y9Q54APOA44+fKrah4nuiWG62IDX6EkDoWb43VY67I5opKLpS/A8PHYqOuaecc+8kkn/ET/wCzbU61OOSvLAKjX1W3Ldic7C6U7QQAezWjgZ5OCVq1ShJYg848SpNNPMjPPqz9f16F20tggHqVoHDBDTlvrP8AYuwWtb4G4/SlqrupNRexNVXjd8mLUdPo9TCKRmiWbNwZjq2pGlkbG5OXbs/h79uSu9NXdDG+xxZKLOgabVZRoV6kf4IY2sBxjOBhXyE2UAQBAEAQBAEAQBAEAQBAEAQBAEAQED1dUlnpRTQRulNWds7omd3gd8e58j6KvqqpXUyhF4bO65KMk2VjThIbGjarLExsGozObXIL/VZmN7xvycEENPGPhJCoWaV0Uc+/y+BP3vXM1LUtqLXdefTr03Pkp2JIi+uDJJLC2PaN/kBz849wFPXX9jBvzI2/aaI7Q49b1HprT3sljpsrxxSQV3DLrGHAl0p7gO5wB55XNrjGbXP82O6+prPBk1q26hQsyxvdM6KYCcueWlme7uOw7HCpxrVk0pbeWxY68RyiNbp/2kl0um0ZPVHxSS4mc4eAM+MfNeRsUPxP4bI9lhrOEb9Cxe0yKOKpEy46V7a8Dn/A9jskiOQnPADuD/fJsxrjdPD28SFyda33Oo6LROnaVVpl24wxNYT7nytVbLBTN4cL0HqAIAgCAIAgCAIAgCAIAgCAIAgCAID4ccE57ICqazcq3td0apTmhlFZ89uT03Ahm1npgHHbJm/kVT18sUteexJUsyKdobr2mdbW2zajobq1h3ryW5Gkyem4nMTHZwD8POfquX0ypWz2PeJM2usrY02tZv0bOad+mWVnRYPpTxNLoi33B24x7ge6ijBTfS1w/p4nfU4rKIy/pty1fnl1PbAX1BH9pru2h/yLTn3IwcqCVsYR9jffgnjDqe58CCeCq6vtMtZw+B7Pxwu8ceW59uw4woIShOfVxLx8n/kkl1RWOUZtPsDWtQhcLToIb1cV5GT0jPCJGOdneMjBwcB2ccYPhadGnwsSXDymVLLfIvHTVjQNDiNGtqZsSyS/eTSPLgX9sD8rR4AHH65V3K4yQNPktgOV6eHqAIAgCAIAgCAIAgCAIAgCAIAgCAICG6t9U9P3vRLgRFl23uW/mx+mVzJNppcnq53KTUsR6lpBkGlS6W2ezDUy9oa6Su6RoyD3AIcePHKxdPV06mNcp9XL+JanL7PKWC2a/UpaRpF67Sq0K8vptBlmgLm8cN+Foy484DRyScLbzgqHPdOp3r9mnS1T05pKDvUFaNuI6pJyHynJzKc5DBwM/ILOukoptePz+HoWYepI9RtJ9OIMldFJujkaG7vh29z7c4VGOE35ln0IbTLNuIsc2E2asm1zWNcBJXa5ueSTggHI9/qvZwg+X0v6Pc9Ta43RZ61Ns3qGC1YrwWOJooXYZN75GOD4Jbg/8d16q2uPQRSqhJ9Rl6gpts0Y6sVuKKOt946i12z7S0DGzcHAjzj5gZ4U+jl7WZLJFatti9UZo7FSGaFxdFIxr2E98EZGVqlYzoAgCAIAgCAIAgCAIAgCAIAgCAIAgNHV9Pj1TT56Ur3sjmbseYzh2POD4XmAVDWqEOh2HQ2DM7Rr0TY/UfIT9nnaTjLj+HfluD2DmYzlwVHUafDVlSw0TVzyumRis2LVx9NlrULM9ererOfHNpzot+XhrfjIDXEOLXfD+7leu9yWHj+fE86McGLoqIt0i8ZeZ36la3vPO7ErsH+GFX1G8l7v0Ja15kVdms6vPcgLvstWGUxPaOZZOO+ezQc+OVWk41JTfL+RNHM9vAj9O6fhpz/6J7mQlxc6tKN8Tz7kDn+a9hrt07I5EtPhey8EvPTvtit2ab2VHOi+Gtp8ZDXOB5cGuJ+LHGB/VWJamq6xdUcepF3coRe+SQ0nSZ+q5IJ9WhY/TKzZBWsFvpyWdxZtcG/iZja7OcEkjhX6aVW30vZlec+o6HGxsbGsY0Na0YAHYBTnB9IAgCAIAgCAIAgCAIAgCAIAgCAIAgPMBAVrqvULUVqpplIV99qKaZ5stzG6OPYCw/7jIOfABUN9yqj1SOox6mQtfp6K9cr6hV0zTqIqOMldsGH/AHpBbucRgYGT8I84yoLdRGaxFHajjk2bgZoWlso02utWufTGOXyHkvf+6MnJKqS9p7k0UVHV4rNmW96FA24IWxxPl9b0/UkYOQMcnuB7ZXiiopNywd9WW1ghIQzUNB9WEOpzFwGN8gLCHY2cnBOeF7/bv6W8r4b/ACH3q8rYtVnVGQXTBYnngr1o2ulkrkB7pH/hYMg5wBnAGTkKKiMIrMo5z+Xme2ZbwnjBZOmde0zT9OrUJjfhcDzNbpvja5zjnJdjaMkrXhbFrCKcovJb43BzdzSCD2IUqaayjg+16AgCAIAgCAIAgCAIAgCAIAgCAIAgCAo+tu/97ubaZkfYWmtI+QNbE0ucJNmfzud6YPyA/Whrs9Md9sk1ONxQs2dP6NoQ1GkXbMjatb1QDsc5x+JwHB2tDnED93C4S6rHlnjNS/Lr0WoUaArs9X1ZHPs7MRWWhpLQSM7HfXyFy64YlJnamzW+0SaBo0NK1EyW098hZFEc7gXF3Oe555JUVntS2eyRLVlb+JC06gmsPlt+gHPnbMYmOyGuAwOfJ45PnCgnd4QTxx8yVRWNyboaTWOsHURIXHId6QwWCQN27/fdtwP0XitkoKGN0eOO+UbHVlfTJ6McWqyTQvc7dVlJe5nrAEgbBw49zgjsD7Kzps4/Mhs59T60DVLcdeKaMlm8bnROzjP0VdWT09jjCWyJXGNkctYLlp2pR3G4/BJ5afP0WtRqoW7cMp2VuHuN4K0RnqAIAgCAIAgCAIAgCAIAgCAIAgPiR4Y0uceAuZyUE5M9SbeEUPqsM1vqLStPMTDsc6XeRy1jdrnYPz+7H6/JZP8AVSn1T/CuF7y0q1FJPx/Ql9W051qpQfStQ1Z6FlskMksXqM3lroy0tDm5yJDjkc4XtE8J9RHNZZC3+s49Ic+jreyXUmyNjYKzS1k24fC4bidnzBJ84ypnV1LMTuuCazNpJfP5HM+oOtZNce2X7HWjHpn0wY3SOY49g7dgEEZ5HyU1WlxyzuWoqjtCPVjz/ZY/NkC/UXuLnCNoDg0t4YMcDd2b5OcY7cd/M6oXmcf1kv8ATFf7f5+ZsVNZnrzMfFNLWd6h+OHAIjxx+Hbk59+PkvHQn6/z1PP6vP3oL4LD+hO6P1BXktQz35J97GmZxM7pGh3LNzg7JDgHEceH/TFK/T3KDjHj6lit6expxyn6vb5/4L9SmhsQiWGRr43c7mu7/qspxcXhks4uL3Pp+sNqXa7GHeZXBrIY4iXu8l7SDy0eePoc8GzXVLHUtsePkV5yxsXnTbgtRDkF+O48rU01/eLEuSrZDp3RujsrRGeoAgCAIAgCAIAgCAIAgCAIAgIjVrjRIItzQ0EZJP5j2Cwu0tTKc+5r8OS3RBJdcit9T6XZsRxWtLcWajG4ek7kYPuceMcEeR9FBppqOz4JJYw0c76l1HUtNjm0q3de6N1l0hEYc4skd8TS7keWuIaDx37gAbFS61lL+fzxOXGNUeqW+eP3fovqVHU9St6rals3X7pJiDI1vYkNAGP0HHzCuQioLCKLbbNVjXyODGsL3H8rAST74x/mV0eLclY+ltefHvZo9zb33GIt3fx9+/1XLsguWdKMnwjRt6fcpO226s0RHGZIy0f4f6pGcZcMOLXKNdpO5rsc5/r/AHxj6rpnJOaB1JZ0myZCQ9hcXzB7nfeDwGgDh3f2Hv4zU1GljYsrkvafU4+zt3j5+K/wdFE0NeqNZ0x8TGSYbNNPG+X7OwZ4bG0g/iwMDHJWdFNyVc/D6nd0HU8kp0PPbqQwU75hrvbG304JJgbLncl73tHA3OJOAThSyaU+qHP0Id2sHQInh8bXDsQtKuanFSRXawz7XZ4EAQBAEAQBAEAQBAEAQBAY5niNjnns1uVHbNVwc34HsVl4Oe9TSstGKpNf0ys+wS5jLrvie4dtg3N+XPPhfMaSUpTd2G8+X68l+1JJQMYv2+m+nrl+8600gNjrVZ5Gylr+eQ5vJB7gHJAB98C/FQtsSgl6vg5pg2/b4XPuOMX7Lrdt80rxK92cy7Npkyc5PJ59votuEVGOEVLrHbY5s2dB0ezrmoCrXcGBo3SzY+GNue/1Pge/6ry21VxyzmEHJ4R06tFo3ScTIY2H7SW59NpHrO+b3fl/2hZrulN5fBr6Ts527ppLzf6GKz1XceMMo144/ctJ/iSvMp+BtV9kaXG9nU/Ro0Has2wC2zXbtd32diPoopQlzFi3seP/AK38yG1zpaOeq/UNGbnALpIB5Hnb/Dt74VrTauS9iw+b1Wkdbe2GinB2cOae/bx/n98LSM5YLv8As41wVr7dPsSNMNo4HqSFz3S99xB984+qztbRt1x5Rp6azvK3W+Vuvd4ovAqSUWzVdO0eSW7bnc9+oPDCxu52d5cTuyBgBoHjA45VeM+vdywvIgaa2L3plmOxAHxPD2EkZ7cg4IPsQQeFb00mm4kU0byuEYQBAEAQBAEAQBAEAQBAEBoa1Jsovx+YgLM7Ws6NLL12J9Ms2Io1trmW7UVjQW34LGP9RlmNuMbX7uRjntkY57lYumw4RxPDXhv+n6lq1b7xK1+1O1LDX0vT2PmIhh9Z7opMFrjhjHe5wc9vBWv2dFSlKZ5Y+jTtLmTx8Fv+ePkczx4HI8Aef87hbJmnU+mYGaB0mLZY0zzASdvxPdw39AOcfVY+on3luPBGz2bpVbOMPPc2eg5ZH9Rlz3uc6SMueSfxHI5KraraMceZtdtQjGiOFxsb2l3dTuG6y+XywNcWxumaAO/b6YXUljHSUNVDT1QrlS8SfOPcVe5VfHZnMcE4riR2x5jcBt8HOFPwfR0XwdceqSzjfc2unLhhusic77uQ7f8Au8fxUdkcrJV7T06tqc1yipdb6YzTdelETQIZx6rR4bnuPoStPTW9dabPh7o9MyJozTRTAwSSNcPiBjiD3ZHIxxkcjkjt3UlkeqLR1pre6ujPyO8tlv3KtW3p9utUryQiSWSWPeW5APHIA/VYtcYLKkslq+DhNwzsmSHSNqvJFYhr6m7UgyYudYc0AEuyS1uOCMg9vdXYNxmsrBUfBZ1fIwgCAIAgCAIAgCAIAgCAICM17/4o/wB4WN25/wCN8S1pP7hQW6VQncHvltzO3iT7HftSeiC5xwQzO0cg4+ioV22pYwkvNJfmSyjDPqVP9rDA/qKNp9E7YIwzcSJO5J2DOD2Gcg/l+a1+zMd2znV/2a/936FLdW4OXcc8N/4/qFplA6lrmBoFLZ+DLOff4BhYqX2jyfWdiY71+486CBOvg4OBEc/LkKHVbxXvLHbbXdRT5yTul6janrWotT9Qurzva1xGDt9v0Xs3gx9RVXW4Sqf3km/eV5+u39O1N7Xti9Nj+YiNwc3wcnk5z/49pe7jjKNmvs2i7Tpxby/HfkiInmTUGSAfE6YOA9sldYwsGk4d3p3BvOEeftQhElyicjd6T+Plu4/z3VnQfdZ8FqvvIp1eqJLEIY2WUueBsjkET3ZOMbj+HIyM+FfZUbfgdo0CtT1LpfRYNTg+0h8bHNaW5ALeQ4j2HHdYico2ScTW1uO9ZP8AS9iGUzwVbE74awbE2OaD0zHguHBwNwOMcccfNWo56k2UGWZXyMIAgCAIAgCAIAgCAIAgCAj9bYX0jj8rgf5rK7Yh16R+mCxpXi053t0yPUbL7MWpavqEUmWxei6RsXcsa0YDBgO7n4uc5WZW7XXFxxGLXp/yTz6VLfdkL+1WAvn0+6PVZHYr7XMEO5xcxwcG57t79/8A6+VqdmSSUoi9dVCf+l/mv3X1KEckDHOcDDT3zzx/UfwWsZx0jQ5f+v8ASor5DrMQDR7F7fw49twWTqI93a35m12XqlVZGT44fxIHa6OQg7mOHDuSCPquWkz7JxrsxJrJaelLzDSsVZXbpQ71AXDccEYP1wo7cJ5Pn+19O4WRsS2wl8jBLBqV3Nc0qTm5+GyM4aPcEk49z9eyRda3gySmzSUJWQnL/wCfU1NGoh2rna8SQQOyJA04efH917OW2PEs6zWNab2liUvD0K11pqLdR1x5jIfDAPSafDj5/Qnj5EBaelr6K0fF3S657EGWMkc1jvQe5wdiOwSPU4xgAEEu57Z7tH0U8nhHlVbssjBeLO2/Z7VLSqUFWZ9eatAP9SYvUjaQACHtyCQee3ssSnEpNsu6qSlY5LzJjpBzrVU3ZNTg1CSfH3leP04mNHZrW5J8kkkknP0AtxX2iSWCpLgsyvkYQBAEAQBAEAQBAEAQBAEBisx+rC9n7zcKK6vvK5Q80dReJJlV+7ous2LE3pxj45TIcNaQAN2foB/BfH1qTkq8brb3mk+lLqIjqFlTq3pyYaXK+SaH76EgPic7Gc43AHBBIzjH1WtpuqixOZxXJPMZcPb9jjTmbHmLY1mRkRtlDywdw0kdne2cEEYOMr6BPKyjOsg65OD5RJaHq9jR7gmhHqsdxJEDtEg78ex8g+/HlR3VK2PT4iFjhLJ0CNuk9UQixXnInLeZmMy4Z7CWMcj/AHDhZ3dSg+mRu6LtadC6VvHyNU9MapXkbLWsU3gcsljnxj6gjj+aPY2f+r6WccWJ7+h8zQ3yHR3b+WAfFHGc/wASoJvH3Y7lWWs0lbzTVv5sh9W6iiq1HUdIcC8jDpgeAD7fXkZ8cKzpdLJy65mFrNc7JvMssqJP6jt8X/P17H2OCtUzizdC6RNe1aN8jZ2wRls0okjAa8DlhHOck9/BAVHW3KMeleJf0celO5+qXvfj8EXu3Pod+899rXKb/R+7+w2Jm+kxzTyXNyCXeOTjjsqdasjHHT8cEcsPfJedIZJ9ljM7ImSBoyyL8LeOwVvTxzJsimyRVwjCAIAgCAIAgCAIAgCAIAgPCMoCvdS6a2zE5u0Oa9zXFruxcCCAfrhYOup7nUK6Oylz7/Mt1T6o9L8CItayz/qlGnRb6+ph2XV2SDbEwjn1HDgcAkN7kgHGAvKK2otyeF4Pz9x5OSzgqf7R+kSI5tZ0ljn1vjfYhhDcskwBvPnaMDI8d/crR0triumR24rULp/Gvr/ny8+OTnDiC8sLonuB2kRvyHO84Pz7j5q+nlFCUXHKfJkhlkilE0Er2yYwHxOLHHPsRyM/1C9aTPFsS0fVmvBgYdUlfwMF7WnPtyR5/qo3TB8o7VklwzQt6levDFm1LKzuWl2GnPbgcc9vkQvY1Qjwjxzk+WajiMbjyByXO4AB9/YHz7ED3XZybem6fY1K1DHWiDy7bIzc0PZI3dh2/B+EYzn3worbo1RbbLWm07ubbeIrlnSA2DpTRmQ1WthaQTJbfCXRMd3+LHYE8Z7BY8f+4m2/kWrrNko8InNKY7U7hls6a2CRu31opS2UPyNzXMcOO45PyXe8cRW+eCu8PdF5hjEcbR5xz8ytSqtQgoleTyzIpDwIAgCAIAgCAIAgCAIAgCAIDHNG2Vha4cFR21qyDg/E9jLpllFW1vRpPQnhouiqCzMH25ms+MgADe3H5wGjB+We4WRGMqbOmzfyLDakso19Mt1tOu6ZpGjUCyG0ZJZJJc7nMa3LpeeSS8sbk85crSTcXKbInyQnUnRWla7JaOjziCxA58b4DuMLZHN5IaCAHcg5HkDPsvY2yr5LHXG3aznzXPx8zn+qdJ6xppcZKcsjW7eYxv3k/jOR2A79lZhqoSOHo5S/tNP6P6/uRJrzNl9OT025ldHl2W5xn48Y4a7A575Uqth5nP8ARXr8DPqCjbsR7oonHdG92Npdh4yNrvbdgH5ZyuZaiuK3Z0tDqH+HHvwTum9KyySCazIYWDZI1z8b2OAO75YPHf8AdCo29pRW1e7LENFXBdVjz6L9y0UTVpVZ4NDjEtoBsjmt+F0jS4bi1x4Jxux4yqbjOUuq7g7su61iPHgTujXX2w+vZp2K8jWjLbAad7Txn4Tjn2XM6+ndPJEpdSw0WfpzRaulU2RVYGwxDJZG0YAyc/58sLU09Um+8nyVbJL7qJodlcIj1AEAQBAEAQBAEAQBAEAQBAEAQGOSNrx8QGfB9lHZXGxYkeptcERd0l32ifUKDmR6k6sa8c0mXMaCQeW59x47+c4Cqd1KvZ7o6zkrWqxSaZ0m3Sa7JoLNmRlY2c875HD1J9w7Yy52TjkBF7U+rOyOuEe61fkpz6dDTk3QyGQyvcHTu9NjTyDuBJzgZyfKrKCkm5LyJctYRH3dQlq3Y69yKMRviYDOwna2U5+EjwCQcH9FE604txfwJVZKLwyIdqMlixLDhsD4q0czzjd+PdgDtwNvJ+fGFDZUkk+d8fkSKbbwakNojVIN0zZoLMAmrlxIDSwgPDQO+Q4EZ+fPhSqtd28LDTw/j4/A5bxP3klpehWpNQcaU9mBgLXQ7HA/AeXRljstwCTgjBGV33neR6MZfj++Thx6XlvCOiaLocNIb3RMa8u3bWjgH3PuVdo0mPas39CvZbnaJNADHZXiE9QBAEAQBAEAQBAEAQBAEAQBAEAQBAEBgmrsmaQ4cHuFBOiEjpSaIS503DNMyYBoljYWMewmMtaeSAW+OFA9PYvuvJIrI+KI210pPOyeN7WyRzxiN0bpPhwO2OM+T57qD+lvWMY2JO9rfJp/+h55HREmON0Ufptk9Rwds9jt7/RcrSalt7pePxOndVhbErpfRlWoGCWYuawYayNm0AfXkqWPZ+XmyTZy9S8Yiix1asNVmyCNrB8vKv11wgsRRXlJyeWbC7OQgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgP/Z',
        'Kolkata Knight Riders': 'data:image/jpeg;base64,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',
        'Delhi Capitals': 'data:image/jpeg;base64,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',
        'Punjab Kings': 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBwgHBgkIBwgKCgkLDRYPDQwMDRsUFRAWIB0iIiAdHx8kKDQsJCYxJx8fLT0tMTU3Ojo6Iys/RD84QzQ5OjcBCgoKDQwNGg8PGjclHyU3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3N//AABEIAMAAzAMBEQACEQEDEQH/xAAcAAABBQEBAQAAAAAAAAAAAAAAAQQFBgcCAwj/xABNEAABAwMBBQMIBQgHBQkAAAABAgMEAAURBhIhMUFRE2FxBxQiM4GRobEjMkJSwRU1YnJzdNHwJDRDgqKy4TaDktLxFhclJidEY2TD/8QAGwEBAAIDAQEAAAAAAAAAAAAAAAMEAQIGBQf/xAA7EQACAgEBBQMLAgUEAwEAAAAAAQIDBBEFEiExQRNRcQYUIjIzYYGRobHRQsEjUnLh8DQ1YoIWJPEV/9oADAMBAAIRAxEAPwDDaAKAKAKAKAWgHkC3yJx2WG8jms7gPbWspRjzLWNh3ZMtKl+CyQdNxWQFS1dqrpwSP41Vlka8EdLi7Bqhxter+hdrDou73FCfMoAixz/aOp7NJ7wOJ/nfWirnMtW7RwsKO5H5RLpbvJdHBC7ncHHTzQwnYHvO+po4yXM8i7yhm/ZQ08eJY4eh9OxAMW1Dyh9p4lfwO74VKqoR6Hm2bVzLOc38OBMRrVbowAjQIrWPuMpT8hW+iKk77ZvWUm/iOg02BgISPZWSPefecORY7ow4w0sdFIBrGiMqclyZGytMWKUMP2iEf0kspSfeMGsOEXzRYhnZMPVsfzIKf5NrFJSrzbt4q+RQ5tAew1G6Isv1bdy4etpJFVu3k0ukYbVvfamIH2Fegv8AgagePJcUerj+UFE+Fsd3w4ooN608hD5ZucBceQeBUjZUfbwPxrVTnDmXJ4WFmx3opa96/wA+5WLjpx5gFyKQ83937Q/jViF6fPgeBmbEuq9Kr0l9SCUCkkEYIqc8VprgzmhgKAKAKAKAKAKAKAKAKA7QCTgAkk4AHOhlJvkWO06dyA9cMpTxDQ5+NVrL9OEeZ0eBsNz0syOC7l1NF0voyfem0KispiwhweWnA/ugcaijXOb1Z6mTtHFwY9nFce5dDUdP6KtFl2XUsmVKHGRIwog/ojgn2b6tQqjHkcxl7VycnhKWi7l/nEsyRgAVIecLQBQBQBQBQBQBQBQDO4QIlyZVHnxWpDKuKXE5rDSa0ZJXbZVLerejM91D5MwgKfsLqv3V45/4Vcff76rzx/5TocPb79XIXxX7mW3ywJVIWzOYXGmI3EkYV7eoqKNkq+DPTyMDGzodpDn0aKXcbdIt7my8n0T9VY4Kq3CamuByeXhW4kt2xeDGOD0rcpiUAUAUAUAUAUAUB6sNOOOpbbSVLVuAA41htLizaEZSkoxXFlzsVjTE7Na09pMc3JwM7JPIDmap2WuT3YnY7O2VXirtLuMvojYNH+TwDs5+oEbazvTD+ynvX1PdyqSujTjI8/aO23LWvG4LvNIaSEICUpCUjgAMYqyc5q3zO6AKAKAKAKAKAKAKAKAKAKAKAhNQ6cgX+N2U5o9okHs30bloPcfwrSVanzLWJm3Yk96t8Oq6MxjVmlJVmWYtxbD0V3c08keiv/lNU5RlU9Udhj5ONtKlxkvFdfgZrerQ5b1FSCVx1H0VdO41aqsU/E5naWzJ4ctVxg+T/JElJAzjdUp5YlAFAFAFAFAdtoWpYSgZUTgDrWNTaMW3oi62CzGJsEpUuY6QkJSMkE8EjxqnbY5vdR2WzNnxxIdrb63v6G66G0W3aGUTrggLuKhlI5Mg8h39TU9NW4tXzPE2ptR5L7Ov1PuXRIxmpjxjqgCgCgCgCgCgCgDNAFAFAFAFAFAFANLjAj3GG5FmNJdZWMKSr5+NYlFSWjJKrZ0zVlb0aMR1ppN2xSVNOpL9vf3NOHn+irvHxqlZB1vVHaYWbVtCncmlr1X4/wA4eBlV7tS7e96GVR1nKCeXcatV2b6OZ2js+WJZw9V8iLIxUh5olAFAFAKniKAtWmLYEATpCd5GWgeQ61Vvs/SjqNibP4ecTXh+TdPJppTzdpF4uCMyHBmO2oerSefifhW1FW76TK+2tpdrJ0VP0evv/saGkYqwc+LQBQBQBQBQBQCEgcaAjbre4dsW03IX6bigNkcQOp7q0lNR5m8a5S5D9pxDiQpCgpKhlJB4itk9TQ7BzWQLQBQBQBQBQAeFAMbtbY10gPQ5jYWy6MEcweRB5EViS3loyWm6dE1ZXzRgerdOuW2Y9bJ420K9Jt0D66eSh31RalVI7aE6tp4vHwfuZmNwiOw5C2HRvSePUdauxkpLVHF5NE8e11z5oakYrYgEoAoCRs1vM6alCvVp9JZ7q0snux1L2zsTzq9R6dTZfJ3pxN6ugceb/oUIhS8jctX2U/ifAdaq1Q7SW8zp9r5nmtCrhwk+Hgja0p2Rjd7KunFHVAFAeEiU1HIDpIzzxUU7owejN41yktUK3JZc+o4g9wUM1upxlyZq01zPXNbGAzWNQeLsplofSOJHdmtZTiubNlGT5Igp2oC6hYtyU7A3KkLICEd+eFa70pLhwRvGpN6c33Iz65apixpBTEaauTi1fTyJAJQofdRzH6/GoHeq+Fa8X3nTYvk/O6G9kvd7kuniWfS9/adRi2vKdb+3EdV9K14feHeK3g0+NfD3fg8jNwLsWWly1XSS/cuMW4x5CCpCxuOCDyPQ1L2iT0lwPN3HzXFDtK0qGUkEd1bpp8jUXNNQcrcShJUtQSBzJxTXQcyOl3+3RdzkhKlcko9LNaStjFcSRVTfQk0naSCOYzUhGLQCEZFAVzW+nU32zrQ2B52zlbCu/wC7noajsrU0X9m5jxLdf0vn4HztqW3ecxi4EFL7I3p54HEeyq9M917rOk2zhdvT2sOLX1RS1dauHGHNAKKAvOmLetqG0ltvakSVDCee84SKpXy3pbp2ux8eONi9pP8AVxfh0PpDSdmbsVljwkYKwNt1f33D9Y/zyAq1CKjHgcpm5Lyb3Y/8XQma3KoUAUBDX9tDrsRDiUrQXN6VDIPjUEnpdHwZLH1H8DL06yb7RSZVr9MKIK40pbYxnkhW0mq6yF+qC+x1UvJtOKddrXDqtR4xrK1s/V/LKD/uVD8K2V1T/Q/m/wAlZ+TeV0nH6/gcL1/DDZCRdTjmUsJ+e1WHbV/I/n/czHycyus4/X8ERN1y48D5vbmQd/py3lPf4RspB9lPON31IpF6ryaguN1jfhwRA3K8z7ooGdLcdSB6KDhKE+CRgfCoZ2Tn6zPaxsDHxuFUNH39fmMk4A4+6tC1o+oqFrbcSpteytO9KgcEU8DDipLSS11+RPQ9ZXSPgSFszUjcC+PpEjoHEkKHtJqaORNLR8fE8bJ2Bh2tyinB+78EzH15GV6+NPZ5BLD7bo9607Xxrftq3zh8jzZ+Td0fUtT8Ue6tb29QxtXfHQNtf834VntKf5X8yH/x7M/mj9fwMpOrrfn6OJcZB+6/IQ2P8CSfjWvbVLlAmr8nch+val4IdWy4NXW1zXhb40csSGEtqQVLcwSc5Woknh3VLCxzrlw00KG0tmxwbK0pOTevM1lv1afAVaR4J1QBQCK4UDMd8p9jFvu4uLLeI8364A3B3n7xv8c9ap5EN2W8jsNh5fa1djPi4/b+xiN9hCFcHG0+rV6TZ6g/yasVT3onPbSxfNshx6PivAjqkKA8tUTzucy1jKSrKvAca0nLdiy3hUdvkRrS/wDht/kvtHn+oEyXB9BCRt4x9o7k/jVaiO9LVnT7cyFTjKqP6vsbMBjnVw40WgCgCgIi9f1iH+0qvP20fBksPUfwMBe9c5+ur51QPqdfqR8Ec7ugobDm2AflOIDjBfRuI3cRWGV8pvsJtdxY5T8H8rebLWwtzz9pKEJj7OwntBkE4wd1FyPChC/slak9N168Vx4cOo5jQeyNxU/E2Qq6NhoqRgbBXjd3Vk0tyN5V7stfQevHroRk+Gw8JzkNCBtvhvs8gbCwopPgDuPtoienJsrnVG3otfFNHvBszq7MxEkM9m8bxsFak/2Yayd/TcaG12bBZErIPVbn110HE5mLKuFvlR/NVtpkrjupYwU43lGd3HGc01IKrLa6ba5ap7uq1+pEXhOYZVsYV5zsgqaDZAxyxxHfWC3s+UnkJa8HHv14kKTnNZPbXIBuoC26Q/MV0/eY/wAzVmn2czlPKP21PgzaG/Vp8BV5HIHVAFABoCC1laE3fTsuMBl0I22u5Sd4rSyO9EubPyfNsmNnTr4HzXqqL20FL6U+mwd46Dgfw+NVqJaPdOj29jb9KtX6f3/z7lPVxq4cgWXSDHpPSCPq+gmq2Q+Gh0nk/TrOdj8D6K8lkDzXTSJKk4XMcU4f1R6KfgM+2t6I6QKe3Lu0y3FcopIuVTHjhQBQBQERev6xD/aVXn7aPgyWHqP4GMabsn5fvbkHt+wztrC8A4welU4Q35aI+hZ2c8LGjZpry+xK3jQ7lvvNstjEpT6521lZRjYCcZPxradMoyUe8pYu3VbRZdOOm5p8ddRNWaQZ03FjvflNTr7zoQ2jswnxPspZV2fMzs/bE86co9nokm+Y61HoT8i2Z+6flJx4t7Ktko3kkgcc99J0uEd5keDtx5WRGjs9E/sPE+T+dLtbctq9PrU4yHW2llWMkZAzmt1jycdUVFt+qFu66VprpqRmlNFu36PJeenPRHGXy2trZydocc7+Oa1rqdiehd2jtmOJOKjBSTWqfuPWx6RkXmZco4vD7f5Pf7IKyTtcd/HdwNYrp321ryI8va0caFcuyT31r9T2a0RbRO8wRqpoS9vHYJwF7WOmeOKz2S3t3e4kctt3OvtXj+j3vu+Q0vGin4N7tlvcuRebnOFKXFA5QQOhO+sSpcZKL6k+NtmuzHsujWk49O8ez/J9AtgQbjqNqMF52e1QE564ya2lSoetIgp8oL7npXRvd+h4Xzyfm22Zy5xrkmQhtIXsqb2dpPcc1idLjDeTJcTygd96pnXo3w+I20f+Yrn+8x/ma3p9nMg8o/bU/E2hv1afAVeRyB1QBQBQHK+FB7z5/wBcWtMPUF0g7GGlrKmx+isbQ+ePZVCa3LTu8SSysCKfHVafIyJ5BQ6pKuKTg1eXE4aUXFuL6F002ypFoRsJytxRKQOZJwKpXvWeh2mxYKvD3n11Z9P2qImDbYkRG5LDKGx7ABV2K0SRx11jsslN9XqPKyRBQBQBQERev6xD/aVXn7aPgyWHqP4GYeTEf+cj+zd+dVsf2h2m3/8AQR+H2NUdjR13tmS4UF9qOtLSSd+CobR+CffV7dTnqcWrJqpwXJsyrylypL+qG230KbaZSkMJJ+sCd6v56VRvbc+J2ewa644MpR5vXUvHlGynQ8rqQ38xVjI9ic/sT/cYfH7Ei5P/ACVpJieUbYYitqUkcxgZrfe3a0ymqHflOpdWx5akw3ULnwCktTdl0qT9o4xn3Y91bQUdN6PUgudifZ2c46oregN901Mf/vfxqDG9aR622PZY/wDSVpNvg3LX1zZlznokkv4jdgSFFWN+/wAKi3VKxps9Tzm7H2ZU4QUo6cdeXuPa/wANzTOpbHKn3OTMhpeKh252i3yOO7ePdScOysi29TTDsjnYd1dVajLRcupMaqTZNWsxm279FZ7FRVvUN+RjnU1rjZp6RQ2fLL2bOUnS3qR+ooWpbbpl1JuUabbQyEKAawoI3AEHnyqKcLIrnqi3gXYF+YnuOM9defUgtH/mG5/vMf5ms0+zmTeUXtafBm0N+rT4CryORZ1QBQBQCGgMo8r8Ps7rb5qR69lTSj3pOR/mPuqnkrimdX5OWN1zr7uP+fQwW/NdjdZCcYBVtAeNWanrBM8PadfZ5U0aDoqL2s6xxsD0nWSRjvCj8qpvjavE6qP8HZf/AF+6/ufSAGNwq+cMLQBQBQBQERev6xD/AGlV5+2j4Mlh6j+BmXkv/wBsV/s3PnVaj2iO02//AKCPw+xddQTRB1xYCo4S+0+yfaUfiBViyW7dE5vFp7XBua5xcX99SH8rVv2k224oT9R3sXD3HePiDWmVHTSR6Hk7fo7aX1TfyJjylf7FS/Fv/MK3v9kUtif7jD4nrqEf+nr37kj5CsTf8D4GmF/uUf6iL8kbqzYH0LcJQ3IIQFHckYB3UxX6Jb8pK4xy011R7eT5QN01InaG0Z2cc8b6xjNb8iPa/scd/wDEYo05dUeUMXYxx5kXyrtAreBs44VrGuat3uhYltDHlsrzbX0tP3HeuoTFy1JpyFKSSw846laQcZGz1rbJSlOKZBsm6dGNfZB6NJfcqflG0vb9PsxnYCnR5wtSVIcVtAYG7FQ5Fca+R7mxNp35s5Qta4IvV/A/7uFgcPMG/wDKKs2exOaw/wDco/1fuULR/wCYbn+8x/mahp9nM9vyj9tT8TaG/Vp8BV5HIM6oAoAoAoCheWBgKsMR4AZakj3FJH8Kr5C9E97yfnpkyj3o+eNVs/8AiaVD7TSSfHJH4VmiXoGNu0t5eq6pfg0byeozqmyJHALHwbNV4cbF4nt5z3dmv+lfdG/VfOHCgCgCgCgIi9f1iH+0qCfto+DJYeo/gZZ5O5ceFqh5+W6lppLTmVrOBxqpTJKerO323VO3CjGC1fA99fakhXO622RaXFOGEVkr2cA5KSMHnwNZutU5JroQ7G2bdTRZC9ab/wCGMtQa5ul7imK7GhtR1KSrCUlSsg5GCT+FYndKa0ZYw9g0Ys1Pebl8kRly1FeLmwpidPccZVjabISlJ6bgBWjk5cGy9j7MxKJKVcOPf1Om3ZE1gNv39CEEY7N15WAOnDFaakclXVLejQ2+9JHQtE5tOIcttxB34ZdIBrOpDLaWM5aW1tP3oa9hc4Snnf6S0tPrFJyCB1O/h30LnaYtqjHg0ds368s4LV1lp/3xNZUmuons/El61a+R7f8Aae8rmw5r8vzl6IoqZ7ZAIGRg5xisuUm0yL/8rEVc4QjopcHoWqN5S0vo7K92dp5B4qaOR/wq/jUyyW+Eo6ni2eTcoPXHsafv/KJi9aosd20pNjW+SELDGEsLGwrA5YredsJV6I8/G2Zl42ZXKyPDXmVPR/5huf7zH+ZrWn2cz0PKP21PxNob9WnwFXkcgzqgCgCgCgKf5VU50g8r7rzR/wAYqDI9Q9fYb0zY+D+xgF7YLktBHJsD4moanwPa2nUpXJ+792XHyfKxqexr6r//ADNaw4WfEsZ3pbNf9K/Y36r5wwUAUAUAUBEXn18P9p+FV5e3j4Mlh6j+BgDwBec/XV86oH1Ov1I+C+wlDI6gxWnnEmS/2LajjCUlbij0SkfOhVyb5VQ/hx1fv4L5mjWixWKFCMmTDCAN/azinPjvO74UOTyM/Mus3Iy190ddPpz/AM4kNd71b0SOwh2+JMC9ySy6D8NmsF/GwciUd+yxw8U/yQIfZXJBiW6XDdJ/9uc7/wBUgCsl51zjHSdsZx/5fkuVlmXBTANwscmSpGQl1vswVJPVKlDHhvFYfA8TIox1L+Daku7j+Cm6ot7UOaXYseTHju+l2T7ZSW1dM8COmCedNTotmZMra9yclJrquv7kMd3GsnphQMQigRbtH/mK6fvMf5mrNPs5nKeUftqvBm0N+rT4CryOQOqAKAKAKAp/lVUBpB5P3nmh/jFQZHqHr7DX/ux+P2MAvL/ZyGx1bB+JqKpcD29p2KNyXu/dk/oqSWp9ikA8HWUk+JCT860fC34k8f42y/8Ap9j6PyKvnDC0AUAUAUBEXndIhftfwNQSX8ePgyWL9B/AwF7c84P01fOvPPqdfqR8ECELcWlDaStajhKUjJJ6UEpKKcpPgWOK2bc8IVqaTJuh9a7xQz3Z/n21lHgZD85XbZMt2roushldFxTJbbmTXJz4cCXpIPoNDPpBA5kCsFzGjb2blXBQWnBdX3a/gkrgbGlL7LkERVIUTFeayQ6n7JChzoVKFmycZRnrr6yfR+DONOyXJKkl2Y84pHFCk7k+3nWGVtq1Rq00rS166/t0LXKj3lxDL1jkoQQkoWysblDqO8dO+sHm4tmLFNXx17n+3geQi35uMpqa5DuCXeT2UbHuBB/ChM7cNzU69Yad3H8FMuGmbhGUtxDbTqCSdllW8dwBrY9+ja+LPSMm0/eQqgUkhYKSOIUMEeND1YtNaoKGS26Q/MVzHWTH+ZqzT7OZyflH7an4m0N+rT4CryOSZ1QwFAFAFAULywSNiwxGR/ayhkdwST8wKr5D9HQ97yfhrkyl3I+eNVvH8qBIONloD4mlC9Ebdtfnei6JEzpx5Tlob2FYcbJCSORByKhuWk9UexsWSsw919NUfT9rlInW+LLbOUvsocSe4jP41djxWpxt0HXZKD6Nr6jyskYUAUAUBE6g9Flp3h2biVE9ACM/DNQz4WQZJDjGSMKvMYxLxOjkY7KQtO/xqhNaSaPpmDZ2uNXPvSOLcp1EtIjJJkr9BnH2VHdn3ZrRmclRdes/V6+/QvDNpYgQBFSpe/e8pH13Dz39/wAq2icZfmzvye07vV7l8CD1DDYjJaZUhPnroyiO3ubjNjf7TuJJ7jWD39n3TnrPX0Fwb6yZWkHCOJxQ9trj7yf05KbbiusjZDwKlpB3Z3UOf2tjzndCa4rTQ0PTMpubb2pDStoKTv7jzB761Oey6ZU2yhJEWm/OStQS7aG05bWoAE4whOzknqSTw5AVkuTwVDFje3z0+b/B7S/S2htbzv3cqwUkmuhQL8y+iWsurC0gjZcKQknOdxxxrY6/Zltcq1uLRvoRVD1S66QjZsrY37Uy4gY6pQnj71VaqX8F+9nG+UNieZGP8sTYQMADpV05cWgCgCgEJxQamU+V+X2l0t0MH1TKnVDvUcD/ACmqmS+KR1fk7VpCdne0jBL87291fVnOFbPuqeqOkEeHtSztMubJXR74C345PHCxUWTHqer5PW+lKt9T6K8ls8S9MtxirachuKaO/wCyfST8Dj2VvRLWBS25T2eW5LlLj+fqXOpjyAoAoAoBpdGEyYbrShkFNQ3x3oe83rek0YzrqGpE5m4YJTJb7N49HmwEn3pCVe2quRxamup23k5kb+O6Jc4P6MibHKRCniSobTiEFLSTzcOEgnwzn2VA0ennVu2rc6Pn4IvrkhDb6m3lElhtK3FE9c5+VZhyOInS5NOP6noiBt8CTeIE24pT/Sbk8IrG1wbbzlR9wx/1rGp0Vt1eJZXR+mtav3vp9SOdhRWpE91kbUW2p7NKj/avdT4Hl3ULcb7ZRhGT9Kx/KJCOtOMK2HU+nshSh93IyPbgj30PThOFkU48vwT+j72bMm5LWQW+w20oVwKwcDHec1hnl7WwvOnXpz10+A4149FmXJBgs5kIaC5LyOAB+qD/AB8KyR7FjOut9pL0W9EvuRk6dGZcbYgxISkNoTtrXHSorXjec8aIs0YllicrZNat6JPTQaXV1Dkr6BZLYSnKSokA434yd1CbBrcafSWj/YZYUcBKdok4CUjnyFC62lq3yRrmlbYGZsKFxTbGMOH/AOVR2l/4iB/dq/GOm7Du4s+bZ2T5xdZf/M9F4IvlWDzwoAoAoBFcKA+ftd3RMy/3ScF5abWW2znglAwPeQT7aoT9O07nDisTZ63uGibfxMidVtuKWeKiTV5cjiJNybkxzapXmc5p3gnOFb+R41rZHei0WcG/sMiNnzNx8l13EDUBiLV9FNTs8ftjeD8xVWmW7LQ6fbuP2uOrY/p+zNkBq6caLQBQBQHKk5oCk6usyJHbxF7KGpeFNuY3Nuj6p+OD3EdKrdnrrU/FHo4WZLFtjfHpwfgZM4y5Dm9jJQUOtOYcQeIIPCqUlo9D6Gpxtp1g+DX3JyXdPOY18ebV9dTSU9yScfLNYXA8aOJ2d+NFrlr81xL5p4CDpNlWBhqOXCe8Ak1g8HMfbZste/Qq2moQf002p7f2kjtXCeKsdfbQ9Pad7rynp0WiIS/tFsOur9Y/LVn9VOQPlWT0NmWqclBcoxXzZEMsqkPIZbGVrOAKHr2TjXFzlyRLSHUNaVaabVmRJmL85VneQgbgfeDWDz64SlnN6cIxWnx5/uQ2MkDd141k9LwA9eXPuoZ1LNo23fSqu0hvKI6tmOhQ9Y94cwnj41PRBJ9pLkjndu5+5X5tW/Slz9yNZ05bTb4H0ue3eO26Vbznp/PMmrlafOXNnFTab0XJExUhoFAFAId1AQmsrumzaelys4cKNhrfvKjuFaWS3Y6lzBx/OMiNfTr4HzVqqV2UFMfa9N5W/fvwN5qtjx1ep0u38js6VUub+xTjVw44Ad9AXrTFwceiNLQspkxVABWd+76pqldHclvI7XZGQsrG7KfNcH4H0hpa8N3yzxpzZAUpOy6jmhY3KHvq3CSlHU5PMxpY18q305eBMVsVgoAoAoBnc4Lc+MtlziR6J6HrWko7yMxejM01Tp56cvARs3RgbIJ4SkDgD+mOR+0O8boLa3bxXNfU9/Y21PNJdjb7N/RlE2lstvsLSpO3hKwdxBSrPDruPvqn4na7sbJQsT5fuXix3hMppu2FzBkWxbQGeDgB3e0H4Vqcxl4UqpSv04KevwE0e6F6dbSTvS4pOM9eFYI9tQ/9tv3EXq5G1GQtIzsOb+7I/wBayT7Dnu3uL5tfYgbVJTDuUaUpJUlpwKI7uB/GsnRZNbtplCPVFnZ04yiU/IW8p2M7tOQylsqQraHFRGcEdO4b6weDPaU3XGtLSS03uOj4EBdIDNtbRGDqnpKlBSl7BQlKRyGd5J/CsnrYuRPInvqOkfudWGyu3d5SlqLMJogvSMZ2e5I+0o8hUldTm/cabR2lXhQ1fGb5I1jTloSvsXlMdjFYGzGYznZHUnmep61dilJ8OS/zU4C66cm5TesnzLVjdUpWFrICgCgEVwoDH/KjfRPuwtsdeWIXrOhcPH3Dd456VTvlvPdR1+wsPsqXfPnLl4GH3yb55cFrTvbT6KM9Bz9pzViqO7HQ5/aWV5zkykuXJEcTmpCgIONASVln+YzUrVvbV6Kx3VpZFSiX9nZnmt6k+XU2XycajFmunYvrHmMzAUo8EL4BX4GqtM9x7rOk2xhedUq2HrR+qNqSra8KunGHVAFAFAJigGdytzE9rZcSNofVVzFaSjrxXNGU+jKHqvSiZiFOOKDMsDAlEeiv9oB/nHDnUE4K16PhL7+B7ezdrWYnoy9Kv6rwM8kR5tmuCUPtqjymlJWjJ49FA8CKpyi4vR8ztKraMyluD3ovn/ccwbsqMiUltAb23A8gcgoHePccVqQX4Ks3Nei0fyHtwnMyEh0lXmstvYV1acHUfzwrJ52LiTqe7+uD1Xviyv4KeJGRzSedDoOfFosEPWFxiRvN3EsOgYwtSdk+3HGh5N2xMeye8tUelrsEq9SfylcwqPHeUSAhOHH+5A5D9I7h7amrpcuM+CRXy9q04Naox/SkvkvFml2awoS0yFtJZitD6JhHDxzxJPU1ait5aJaROOuvnObnN6yZZUpCUhIGAOAHKpysdUAUAUAh4UBXdaahTYLSt1JBku+gwk/e6+A41HZNQRf2dhSy7lHouZ866luJjRigLKn5GSVE79/EnxqtTDelqzpdsZkcansoc2uHgUtVXTizmgCgOkk5oC0aYuIWjzF9Q3erJ6dKq318d5HU7E2hw83sfh+Dd/JvqwzGk2i4uf0ptP0C1f2qBy/WHxram3eW6yrtnZvYy7etei+fuf4NASc1YPAOqAKAKATFAcrbStJSoZBrWUVLmZTa5FYvWn0PxVNGOmVF3nsV/Y70Eb0nw3d1RSTS0mtV9S1j5M6Z79Ut1/T5GfXPR52iq0SNpWd8aSQlfglXBXwNQPH141vX7nU4nlDF+jlLdfeuRWJTEiA4pmYy7GcJ3odSU8PHjVZ+i9GdBVbXalOtp+9D62aeuNzSlxpjsoxP9Zf9Bv2E71eypIVSnyRUy9qYuJwnLV9y4l709oqNHUhwt+dvjg8+j0E96Uc/73uqeNcIcPWkcpm7byMhOMfQh9S7wrY0w52rhLjp4qVvzU+45aOR4jn0RIgAVKaC0AUAUAh4UAzulwjWyA9MmOhtlpO0onj4Dqaw2orVklVU7rFXBatmC6v1Ku6THbpN+jaQMMM5zsJ6eJ51Rbdszt6q6dmYvHn197MsnylzJK33D6Szw6DkKuxjurQ4vJyJZFrtlzY2rYgCgCgCgO21qSsKSSCN4IrDRmMnF6ou+n7wZWwe0U1NZwoKScHd9oVTtrcHquR2mzdoQzK+yt9bk/ejddDazavTKIc5SW7ikc9we709/UVPVap8GeDtPZcsWTsr4w+xckHIqY8g6oAoAoAoBCBjhQDC4WqHcEkPsjaIxtDcf9ajcIvj1N42SXAg39O3FooRCuAUyk7kyEJXsdMBQOPZisemuHB+JJG2K4rVeBIQrAltYenyFyn/ALyuXh0HcMDupuylwk+Hcab6XqomW0IQnZQkJHQVvFJLRI0bb4s7xWxgKAKAKAKAZ3CdHt8NyVMeDLKBlS1GjaS1ZvXVO2argtWzFNbatcvj5Wolq3R/Vtq3Z/TV39ByqjZY7HojtMHBq2fV2k36XV93uRlF7ui7g7hBIYSfRHXvNWa61BHN7R2hLLs4cIrkRealPMEoAoAoAoAoD0YdW06HG1FKxwIrDWvBm9dkq5KUXo0XSx31MkthSuxloIKSg4z3p6GqdlTg9Y8jsdn7Ury49lbwl9zZNH+UBD2xBvq0od+qiVwSvoFdD38Klrv14SPN2jsSUNbMdarqu40VtQUnKSCDzFWDneXA6oAoAoAoAoAoAoAoAoAoAoAoCGv+oLfYYvbT3sKP1Gk71rPcK1nOMFqyziYd2VPdrXx7jGNXatlXlzzicsMQ2yS0wFbk956qqnKUrZaLkdjjYmPs2rfb49ZfsjM71d1zyUIyhgHcnmrvNWa6lBHNbS2nPLlux4QREmpTyhKAKAKAKAKAKAKA7bUUK2gcEcDWGZTaeqZZLTqIJCWp5JA3dqOneKr2Ua8YnR4G3N3SGRy7zRtLa1uFmQhDDglwT9VlasgD9FXKoo2Sr4M9PK2ZjZi7SL0fev3NT09rGz3xIQw+GZX2o7x2VZ7uSvZVqFsZnL5ezMjF4yWse9FiBGBvqQoC5FAFAFAFAFAFAGRQCZHWgG02ZFgsKkTH2mGk7ytxYSKw2lzNq652S3YLVmfah8paPSYsDSnDjBlPJwkfqp4n24qvPIX6TosPYE36WS9Pcufx7jK79qFKZC5E6QuTNXxBOT/oKijCdj1Z6l+bi7Pr7OHPuX7lKuVyfnubTyvRHBA4CrcIKK4HJ5edblT3pvh3DGtymJQBQBQBQBQBQBQBQBQHSTigHcK5SIKwWHMDmk7wa0lXGS4lvFzr8aW9WyyQdSRpGyiUCyvkriM/hVaeO48YnTYu3arPRtWj+herFri8W9KfNZolxxj0HztgDx4itFbOHMmt2ZhZa3ocPD8Fzt3lRhubKbnCdZPNbB2058ONTxyIvmjyLvJ+5PWqaZZIetNOy8bF0ZbUeTxKPnuqVWwfJnmz2Zlw51v7/YmI9xgyQDGmR3QeHZupV8jW28irKqyHrRa+A42hyOfCs6ojOVutt/XWlPicVjVGVFvkiOl6issQZkXWEjHIvpz7s5rDnFc2WIYeRP1YP5EDP8otgjg9g89KXy7JsgH2nFRyvguXEu1bEy7HxW74lWu3lNuL+03bIrUVP33DtqA8OFQvIk/VPXx/J+qPG6WvgUC9ajDrpfutwXIf5BStojwA3D2YrVRss5l2eVhYEd2Oi9yKpcdRvSMojAst8M/aNTwoUeZ4OXty230avRX1IRSyo5Ksk8STk1MeJKTk9W+JxWTAUAUAUAUAUB//2Q==',
        'Rajasthan Royals': 'data:image/png;base64,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',
        'Sunrisers Hyderabad': 'data:image/jpeg;base64,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',
        'Lucknow Super Giants': 'data:image/jpeg;base64,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',
        'Gujarat Titans': 'data:image/jpeg;base64,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'
    }
    return team_logos.get(team_name, '')

# Apply background and styles
add_bg_from_url()
apply_custom_styles()

st.markdown("""
<script class="chat-toggle-script">
document.addEventListener('DOMContentLoaded', function() {
    // Create chat button element
    const chatButton = document.createElement('div');
    chatButton.className = 'chat-button';
    chatButton.innerHTML = '<div class="chat-icon">💬</div>';
    document.body.appendChild(chatButton);

    // Create chat container
    const chatContainer = document.createElement('div');
    chatContainer.className = 'chat-container';
    chatContainer.innerHTML = `
        <div class="chat-header">
            Cricket Expert Assistant
            <span class="chat-close">✕</span>
        </div>
        <div class="chat-messages" id="chat-messages"></div>
        <div class="chat-input-container">
            <input type="text" class="chat-input" placeholder="Ask about cricket...">
            <button class="chat-send">➤</button>
        </div>
    `;
    document.body.appendChild(chatContainer);

    // Toggle chat container visibility
    chatButton.addEventListener('click', function() {
        if (chatContainer.style.display === 'flex') {
            chatContainer.style.display = 'none';
        } else {
            chatContainer.style.display = 'flex';
        }
    });

    // Close chat on X click
    document.querySelector('.chat-close').addEventListener('click', function() {
        chatContainer.style.display = 'none';
    });
});
</script>
""", unsafe_allow_html=True)

# Initialize chatbot session state
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "system",
         "content": "You are a highly knowledgeable and experienced cricket analyst. Your understanding of cricket is deep and insightful, especially when it comes to the Indian Premier League (IPL). No one knows more about cricket strategy, team dynamics, and player performance than you. Give your personal expert opinion, based on your deep cricket knowledge and patterns you've seen in past IPL seasons."}
    ]

# Teams and Cities
teams = ['Chennai Super Kings', 'Mumbai Indians', 'Royal Challengers Bangalore',
         'Kolkata Knight Riders', 'Delhi Capitals', 'Punjab Kings',
         'Rajasthan Royals', 'Sunrisers Hyderabad', 'Lucknow Super Giants', 'Gujarat Titans']
cities = ['Hyderabad', 'Bangalore', 'Mumbai', 'Indore', 'Kolkata', 'Delhi',
          'Chandigarh', 'Jaipur', 'Chennai', 'Cape Town', 'Port Elizabeth',
          'Durban', 'Centurion', 'East London', 'Johannesburg', 'Kimberley',
          'Bloemfontein', 'Ahmedabad', 'Cuttack', 'Nagpur', 'Dharamsala',
          'Visakhapatnam', 'Pune', 'Raipur', 'Ranchi', 'Abu Dhabi',
          'Sharjah', 'Mohali', 'Bengaluru']
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@700&display=swap');

    .main-header1 {
        background: linear-gradient(135deg, #3a0CA3, #4361EE, #4CC9F0);
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
        animation: floatHeader 2s ease-in-out;
    }

    .main-title {
        font-family: 'Poppins', sans-serif;
        font-size: 50px;
        font-weight: 800;
        color: white;
        text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.3);
        margin: 0;
    }

    @keyframes floatHeader {
        from { transform: translateY(-20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    </style>

    <div class="main-header1">
        <h1 class="main-title">🏏 IPL MATCH WIN PREDICTOR</h1>
    </div>
    """,
    unsafe_allow_html=True
)
# Custom header
st.markdown(
    """
    <style>
    .main-header {
        background-image: url("https://hellohyderabad.org/wp-content/uploads/2025/02/IPL-2025.jpg");
        background-size: cover;
        background-position: center;
        padding: 150px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    .main-title {
        font-size: 48px;
        font-weight: 800;
        color: white;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        margin-bottom: 10px;
        font-family: 'Montserrat', sans-serif;
    }
    .sub-title {
        font-size: 22px;
        color: #E6F1FF;
        font-style: italic;
        font-weight: 400;
    }
    </style>
     
     <div class="main-header">
      
    </div>
  
    """,
    unsafe_allow_html=True
)


# Main container


# Load model with enhanced error handling
try:
    pipe = load('finepipe.pkl')

    # Optional: silent internal validation
    if not hasattr(pipe, 'predict_proba'):
        raise ValueError("Loaded object is not a scikit-learn pipeline with predict_proba method!")

except Exception as e:
    # Log the error silently or handle it without frontend display
    # Example: write to a log file or raise
    raise RuntimeError(f"Error loading model: {str(e)}")

# Input Section
st.markdown('<div class="section-header">🏟️ MATCH SETUP</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:

    batting_team = st.selectbox("Batting Team", sorted(teams), key="batting_team")
    batting_logo_url = get_team_logo_url(batting_team)
    if batting_logo_url:
        st.markdown(f'<img src="{batting_logo_url}" class="team-logo" alt="{batting_team}">', unsafe_allow_html=True)
    st.markdown(f'<div class="team-label">{batting_team} <span class="role-indicator batting-indicator">Batting</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:

    # Default to a different team than batting team
    default_bowling_idx = 1 if sorted(teams)[0] == batting_team else 0
    bowling_team = st.selectbox("Bowling Team", sorted(teams), index=default_bowling_idx, key="bowling_team")
    bowling_logo_url = get_team_logo_url(bowling_team)
    if bowling_logo_url:
        st.markdown(f'<img src="{bowling_logo_url}" class="team-logo" alt="{bowling_team}">', unsafe_allow_html=True)
    st.markdown(f'<div class="team-label">{bowling_team} <span class="role-indicator bowling-indicator">Bowling</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-header">🏆 MATCH DETAILS</div>', unsafe_allow_html=True)

col3, col4 = st.columns(2)
with col3:
    selected_city = st.selectbox('Match Venue', sorted(cities))

with col4:
    target = st.number_input('Target Score', min_value=1, max_value=300, value=180)

st.markdown('<div class="section-header">🎯 CURRENT SITUATION</div>', unsafe_allow_html=True)

col5, col6, col7 = st.columns(3)
with col5:
    score = st.number_input('Current Score', min_value=0, max_value=target, value=0)
with col6:
    overs = st.number_input('Overs Completed', min_value=0.0, max_value=20.0, value=0.0, step=0.1, format="%.1f")
with col7:
    wickets = st.number_input('Wickets Fallen', min_value=0, max_value=9, value=0)

# Validation
if batting_team == bowling_team:
    st.warning("⚠️ Batting and bowling teams cannot be the same!")
    st.stop()

if overs > 20 or overs < 0:
    st.warning("⚠️ Overs must be between 0 and 20")
    st.stop()

# Cricket ball animation for the button (pure CSS)
ball_animation = """
<style>
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
.cricket-ball {
  display: inline-block;
  width: 20px;
  height: 20px;
  background-color: #d32f2f;
  border-radius: 50%;
  position: relative;
  margin-right: 10px;
  vertical-align: middle;
  animation: spin 2s linear infinite;
}
.cricket-ball::before {
  content: '';
  position: absolute;
  width: 100%;
  height: 2px;
  background-color: white;
  top: 50%;
  left: 0;
  transform: translateY(-50%);
}
</style>
"""

st.markdown(ball_animation, unsafe_allow_html=True)

# Prediction Button
predict_button = st.button('PREDICT MATCH OUTCOME', type="primary", use_container_width=True)

# Prediction Logic
if predict_button:
    try:
        # Show loading spinner
        with st.spinner("Calculating win probabilities..."):
            import time
            time.sleep(1)  # Simulate calculation time for better UX

            # Calculate match metrics
            runs_left = target - score
            balls_left = max(120 - int(overs * 6), 0)
            wickets_left = 10 - wickets
            crr = score / max(overs, 0.1)  # Avoid division by zero
            rrr = (runs_left * 6) / max(balls_left, 1)  # Avoid division by zero

            # Create input DataFrame for prediction
            input_df = pd.DataFrame({
                'batting_team': [batting_team],
                'bowling_team': [bowling_team],
                'city': [selected_city],
                'total_run_left': [float(runs_left)],
                'ball_left': [float(balls_left)],
                'is_wicket': [float(wickets_left)],
                'total_runs_x': [float(target)],
                'crr': [float(crr)],
                'rrr': [float(rrr)]
            })

            # Make prediction
            try:
                result = pipe.predict_proba(input_df)
                prediction_method = "Full Pipeline"
            except Exception as pipeline_error:
                st.warning(f"Full pipeline prediction failed: {str(pipeline_error)}")
                try:
                    # If that fails, try manually preprocessing and then predicting
                    preprocessor = pipe.steps[0][1]
                    classifier = pipe.steps[-1][1]
                    transformed_data = preprocessor.transform(input_df)
                    result = classifier.predict_proba(transformed_data)
                    prediction_method = "Manual Pipeline Steps"
                except Exception as manual_error:
                    st.error(f"Manual pipeline steps failed: {str(manual_error)}")
                    st.error("Cannot process prediction. Please check model compatibility.")
                    st.stop()

            # Get prediction results
            loss_prob = result[0][0]
            win_prob = result[0][1]

        # Display results
        st.markdown('<div class="results-container">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">🎯 MATCH PREDICTION</div>', unsafe_allow_html=True)

        col8, col9 = st.columns(2)

        # Batting team probability
        with col8:
            batting_logo = get_team_logo_url(batting_team)
            st.markdown(f"""
                <div class="team-card" style="background-image: linear-gradient(135deg, #4361EE, #3A0CA3);">
                    <img src="{batting_logo}" class="team-logo" alt="{batting_team}">
                    <div class="team-card-title">{batting_team}</div>
                    <div class="team-card-value">{round(win_prob * 100)}%</div>
                </div>
            """, unsafe_allow_html=True)

        # Bowling team probability
        with col9:
            bowling_logo = get_team_logo_url(bowling_team)
            st.markdown(f"""
                <div class="team-card" style="background-image: linear-gradient(135deg, #F72585, #B5179E);">
                    <img src="{bowling_logo}" class="team-logo" alt="{bowling_team}">
                    <div class="team-card-title">{bowling_team}</div>
                    <div class="team-card-value">{round(loss_prob * 100)}%</div>
                </div>
            """, unsafe_allow_html=True)

        # Progress bar visualization

        st.markdown('<div class="section-header">Win Probability</div>', unsafe_allow_html=True)

        # Custom styled progress bar
        st.markdown(f"""
            <div style="position: relative; height: 30px; background: #333; border-radius: 15px; overflow: hidden; margin: 20px 0;">
                <div style="position: absolute; left: 0; top: 0; height: 100%; width: {round(win_prob * 100)}%; background-image: linear-gradient(to right, #4361EE, #3A0CA3); border-radius: 15px;"></div>
                <div style="position: absolute; right: 0; top: 0; height: 100%; width: {round(loss_prob * 100)}%; background-image: linear-gradient(to left, #F72585, #B5179E); border-radius: 15px;"></div>
                <div style="position: absolute; left: {round(win_prob * 100) - 5}%; top: 50%; transform: translateY(-50%); color: white; font-weight: bold; text-shadow: 1px 1px 2px black;">
                    {batting_team[0:3].upper()}
                </div>
                <div style="position: absolute; right: {round(loss_prob * 100) - 5}%; top: 50%; transform: translateY(-50%); color: white; font-weight: bold; text-shadow: 1px 1px 2px black;">
                    {bowling_team[0:3].upper()}
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Match situation summary


        st.markdown('<div class="section-header">🎯 Match Summary</div>', unsafe_allow_html=True)

        # Display key metrics in a clean manner
        summary_col1, summary_col2 = st.columns(2)

        with summary_col1:
            st.markdown("**Target:**  " + str(target))
            st.markdown("**Current Score:**  " + f"{score}/{wickets}")
            st.markdown("**Overs Completed:**  " + f"{overs}/20.0")
            st.markdown("**Runs Needed:**  " + str(runs_left))

        with summary_col2:
            st.markdown("**Balls Remaining:**  " + str(balls_left))
            st.markdown("**Current Run Rate:**  " + f"{crr:.2f}")
            st.markdown("**Required Run Rate:**  " + f"{rrr:.2f}")
            st.markdown("**Wickets in Hand:**  " + str(wickets_left))

        st.markdown('</div>', unsafe_allow_html=True)

        # Commentary analysis
        commentary = ""
        if rrr > 12:
            commentary = f"{bowling_team} has the upper hand with a challenging required run rate of {rrr:.2f}."
        elif rrr < 7:
            commentary = f"{batting_team} is cruising with a comfortable required run rate of {rrr:.2f}."
        else:
            commentary = f"It's a balanced game with a moderate required run rate of {rrr:.2f}."

        if wickets_left <= 3:
            commentary += f" With only {wickets_left} wickets remaining, every ball is crucial."
        elif wickets_left >= 8:
            commentary += f" With {wickets_left} wickets in hand, {batting_team} has good batting resources."

        if balls_left < 36:  # Last 6 overs
            commentary += " We're heading into the death overs, where every run counts."

        st.markdown(f"""
            <div style="background-color: rgba(20, 20, 40, 0.7); padding: 15px; border-radius: 10px; margin-top: 20px; border-left: 5px solid #4CC9F0;">
                <h4 style="margin-top: 0; color: #4CC9F0;">Expert Analysis</h4>
                <p style="color: white; font-style: italic;">{commentary}</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Prediction failed: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        st.write("Please check your input values and try again.")

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown(
    """
    <div class="footer">
        <p>© 2025 IPL Match Win Predictor | Powered by Machine Learning</p>
        <p>Created by Devang Varshney | Made with ❤️ for cricket fans</p>
        <p style="font-size: 12px; color: #888;">This prediction is based on historical IPL match data and machine learning algorithms.</p>
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("""
<div class="chat-widget">
    <div id="chat-popup"></div>
</div>
""", unsafe_allow_html=True)

# Add JavaScript to handle chatbot functionality with Groq API
st.markdown("""
<script>
// We'll need to communicate with Streamlit via component events and callbacks
// This is a simplified mock-up of what would be implemented with a proper Streamlit component

// Function to add message to chat UI
function addMessage(message, sender) {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = sender === 'user' ? 'user-message' : 'bot-message';
    messageDiv.innerText = message;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Initial bot message
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        const chatMessages = document.getElementById('chat-messages');
        if (!chatMessages) return;

        addMessage("Hello! I'm your cricket expert assistant. Ask me anything about IPL, cricket strategies, or player performances!", 'bot');

        // Set up input and send button functionality
        const chatInput = document.querySelector('.chat-input');
        const chatSend = document.querySelector('.chat-send');

        if (chatInput && chatSend) {
            // Send message on button click
            chatSend.addEventListener('click', function() {
                sendMessage();
            });

            // Send message on Enter key
            chatInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
        }
    }, 1000);
});

// Function to send message
function sendMessage() {
    const chatInput = document.querySelector('.chat-input');
    if (!chatInput || !chatInput.value.trim()) return;

    const userMessage = chatInput.value.trim();
    addMessage(userMessage, 'user');
    chatInput.value = '';

    // Display typing indicator
    const chatMessages = document.getElementById('chat-messages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'bot-message typing';
    typingDiv.id = 'typing-indicator';
    typingDiv.innerText = 'Typing...';
    chatMessages.appendChild(typingDiv);

    // This would normally trigger a Streamlit callback, but for the mockup we'll simulate a response
    setTimeout(() => {
        // Remove typing indicator
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) typingIndicator.remove();

        // Custom responses based on message content
        let botResponse = "";
        const lowerMsg = userMessage.toLowerCase();

        if (lowerMsg.includes('hello') || lowerMsg.includes('hi') || lowerMsg.includes('hey')) {
            botResponse = "Hello! How can I help you with cricket today?";
        } 
        else if (lowerMsg.includes('ipl winner') || lowerMsg.includes('who will win') || lowerMsg.includes('champion')) {
            botResponse = "Based on current form and team balance, Mumbai Indians and Chennai Super Kings always have strong chances due to their consistent performances and experienced players. But T20 cricket is unpredictable - that's what makes it exciting!";
        }
        else if (lowerMsg.includes('best batsman') || lowerMsg.includes('top scorer')) {
            botResponse = "In IPL history, Virat Kohli holds the record for most runs scored. His technical prowess combined with aggressive intent makes him one of the greatest batsmen in the format.";
        }
        else if (lowerMsg.includes('best bowler') || lowerMsg.includes('top wicket')) {
            botResponse = "Lasith Malinga has been one of the most effective bowlers in IPL history with his unique slinging action and deadly yorkers at the death. His ability to adapt to different conditions makes him exceptional.";
        }
        else if (lowerMsg.includes('strategy') || lowerMsg.includes('tactics')) {
            botResponse = "T20 cricket strategy revolves around identifying key match-ups, managing resources through different phases, and situational awareness. Power play utilization and death over execution are critical components of a winning strategy.";
        }
        else {
            botResponse = "That's an interesting cricket question! In my experience, the best approach is to analyze both historical data and current form. Would you like me to elaborate on any specific aspect of IPL cricket?";
        }

        addMessage(botResponse, 'bot');
    }, 1500);
}
</script>
""", unsafe_allow_html=True)

# For Streamlit sharing, we add a dummy chatbot interface that works without requiring API connectivity
# This is a fallback since JavaScript integration with Groq API would need a backend
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant",
         "content": "Hello! I'm your cricket expert assistant. Ask me anything about IPL, cricket strategies, or player performances!"}
    ]

# Hidden chat widget to use as fallback if JavaScript doesn't work
with st.expander("Chat with Cricket Expert", expanded=False):
    st.subheader("🏏 Cricket Expert Assistant")

    # Display chat history
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Chat input
    user_question = st.chat_input("Ask about cricket...")

    if user_question:
        # Add user message to history
        st.session_state.chat_messages.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.write(user_question)

        # Process the query and generate response
        try:
            # If Groq API is available and works
            try:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system",
                         "content": "You are a highly knowledgeable cricket analyst specializing in IPL."},
                        {"role": "user", "content": user_question}
                    ],
                    model="llama-3.3-70b-versatile"
                )
                response = chat_completion.choices[0].message.content
            except:
                # Fallback responses if API is not available
                query = user_question.lower()
                if "hello" in query or "hi" in query:
                    response = "Hello! How can I help you with cricket today?"
                elif "ipl winner" in query or "who will win" in query:
                    response = "Based on current form and team balance, GT,RCB,PBKS,MI based on ipl point table always have strong chances due to their consistent performances and experienced players. But T20 cricket is unpredictable - that's what makes it exciting!"
                elif "best batsman" in query:
                    response = "In IPL history, Virat Kohli holds the record for most runs scored. His technical prowess combined with aggressive intent makes him one of the greatest batsmen in the format."
                elif "best bowler" in query:
                    response = "Lasith Malinga has been one of the most effective bowlers in IPL history with his unique slinging action and deadly yorkers at the death. His ability to adapt to different conditions makes him exceptional."
                else:
                    response = "That's an interesting cricket question! In my experience, the best approach is to analyze both historical data and current form. Would you like me to elaborate on any specific aspect of IPL cricket?"

            # Add assistant response to history
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.write(response)

        except Exception as e:
            st.error(f"Error: {str(e)}")