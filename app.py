from pathlib import Path

import streamlit as st

from services.storage import save_uploaded_file, list_uploaded_files
from services.parser import parse_log_file
from utils.helpers import safe_key, escape_html


st.set_page_config(
    page_title="Log Viewer",
    layout="wide",
    initial_sidebar_state="expanded",
)

UPLOAD_DIR = Path("data/uploads")


def init_session_state():
    if "selected_file" not in st.session_state:
        st.session_state.selected_file = None
    if "selected_user" not in st.session_state:
        st.session_state.selected_user = None


def inject_styles():
    st.markdown(
        """
        <style>
        .log-card {
            border: 1px solid #3a3a3a;
            border-radius: 12px;
            padding: 14px;
            margin-bottom: 18px;
            background-color: #111111;
        }

        .log-header-row {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-bottom: 12px;
        }

        .log-chip {
            border-radius: 8px;
            padding: 6px 10px;
            font-size: 13px;
            font-weight: 700;
            border: 1px solid #444;
            background-color: #1a1a1a;
            font-family: monospace;
            display: inline-block;
        }

        .chip-timestamp {
            background: #1a1a1a;
            border-color: #444;
            color: #e6e6e6;
        }

        .chip-module {
            background: #1a1a1a;
            border-color: #444;
            color: #e6e6e6;
        }

        .chip-info {
            background: #0b3d2e;
            border-color: #0e8f6a;
            color: #9fffdc;
        }

        .chip-debug {
            background: #1f2a44;
            border-color: #3a5bbf;
            color: #9fbaff;
        }

        .chip-warning {
            background: #4d3b00;
            border-color: #c59d00;
            color: #ffe28a;
        }

        .chip-error {
            background: #4a0d0d;
            border-color: #c53030;
            color: #ffb3b3;
        }

        .log-message-wrapper {
            border: 1px solid #4a4a4a;
            border-radius: 10px;
            overflow: hidden;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def sidebar_file_uploader():
    st.sidebar.header("Upload Log File")

    uploaded_file = st.sidebar.file_uploader(
        "Choose a .log file",
        type=["log", "txt"],
        accept_multiple_files=False,
    )

    if uploaded_file is not None:
        saved_path = save_uploaded_file(uploaded_file, UPLOAD_DIR)
        st.sidebar.success(f"Saved: {saved_path.name}")
        st.session_state.selected_file = saved_path.name
        st.session_state.selected_user = None


def build_file_user_tree():
    file_map = {}
    uploaded_files = list_uploaded_files(UPLOAD_DIR)

    for file_path in uploaded_files:
        parsed_logs = parse_log_file(file_path)
        users = sorted({entry["user"] for entry in parsed_logs if entry["user"]})
        file_map[file_path.name] = {
            "path": file_path,
            "users": users,
            "logs": parsed_logs,
        }

    return file_map


def sidebar_navigation(file_map):
    st.sidebar.markdown("---")
    st.sidebar.header("Logs")

    if not file_map:
        st.sidebar.info("No uploaded log files yet.")
        return

    for file_name, info in file_map.items():
        with st.sidebar.expander(
            file_name,
            expanded=(st.session_state.selected_file == file_name)
        ):
            if not info["users"]:
                st.caption("No users found")
                continue

            for user in info["users"]:
                if st.button(
                    user,
                    key=safe_key(f"{file_name}_{user}"),
                    use_container_width=True,
                ):
                    st.session_state.selected_file = file_name
                    st.session_state.selected_user = user


def get_level_class(level: str) -> str:
    level = (level or "").upper()

    if level == "DEBUG":
        return "chip-debug"
    if level == "WARNING":
        return "chip-warning"
    if level == "ERROR":
        return "chip-error"
    if level == "CRITICAL":
        return "chip-error"

    return "chip-info"


def render_log_entries(entries):
    if not entries:
        st.info("No log entries to display.")
        return

    for i, entry in enumerate(entries):
        timestamp = entry.get("timestamp", "")
        level = entry.get("level", "")
        module = entry.get("module", "")
        message = entry.get("message", "")

        level_class = get_level_class(level)

        st.markdown('<div class="log-card">', unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="log-header-row">
                <div class="log-chip chip-timestamp">{timestamp}</div>
                <div class="log-chip {level_class}">{level}</div>
                <div class="log-chip chip-module">{module}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="log-message-wrapper">', unsafe_allow_html=True)
        st.code(message, language=None)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)


def main():
    init_session_state()
    inject_styles()

    st.title("Log Viewer")

    sidebar_file_uploader()
    file_map = build_file_user_tree()
    sidebar_navigation(file_map)

    selected_file = st.session_state.selected_file

    if not selected_file:
        st.info("Upload a log file from the left sidebar to begin.")
        return

    if selected_file not in file_map:
        st.warning("Selected file is not available.")
        return

    info = file_map[selected_file]
    logs = info["logs"]

    st.subheader(selected_file)

    selected_user = st.session_state.selected_user
    if selected_user:
        st.markdown(f'<div class="user-label">User: {selected_user}</div>', unsafe_allow_html=True)
        filtered_logs = [entry for entry in logs if entry["user"] == selected_user]
    else:
        st.markdown('<div class="user-label">Select a user from the left sidebar</div>', unsafe_allow_html=True)
        filtered_logs = []

    render_log_entries(filtered_logs)


if __name__ == "__main__":
    main()