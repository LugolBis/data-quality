from pathlib import Path

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
DOC_EN: Path = ROOT_DIR / "doc" / "en" / "paper.pdf"
DOC_FR: Path = ROOT_DIR / "doc" / "fr" / "paper.pdf"


def render_en() -> None:
    st.title("data-quality documentation")
    st.divider()
    st.pdf(DOC_EN, height="stretch")


def render_fr() -> None:
    st.title("data-quality documentation")
    st.divider()
    st.pdf(DOC_FR, height="stretch")
