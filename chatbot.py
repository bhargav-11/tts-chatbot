
import streamlit as st

from chat_interface import render_chat_interface
from sidebar import configure_sidebar, set_sidebar_width


def main():
    st.title("AI Bot")
    set_sidebar_width()
    configure_sidebar()
    render_chat_interface()


if __name__ == "__main__":
    main()
