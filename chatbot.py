
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st

from chat_interface import render_chat_interface
from sidebar import configure_sidebar, set_sidebar_width
from dotenv import load_dotenv

load_dotenv()

def main():
    st.title("AI Bot")
    set_sidebar_width()
    configure_sidebar()
    render_chat_interface()


if __name__ == "__main__":
    main()
