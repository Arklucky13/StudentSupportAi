
import html
import os
from pathlib import Path

import httpx
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client


# --------------------------------------------------
# 1. Page configuration — must be the first Streamlit call
# --------------------------------------------------

st.set_page_config(
    layout="wide",
    page_title="Student Support | Fieldnotes",
    page_icon="S",
)


# --------------------------------------------------
# 2. Centralized visual system
# --------------------------------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&display=swap');

    :root {
        --paper: #F5F1E8;
        --paper-deep: #EAE3D6;
        --ink: #202820;
        --forest: #34483C;
        --rust: #C84F32;
        --olive: #85866A;
        --rule: #CFC7B8;
        --muted: #66695F;
        --white: #FFFEFA;
        --danger: #9F3529;
        --success: #315A42;
    }

    /* Page and background texture */
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        color: var(--ink);
        background-color: var(--paper);
        background-image:
            repeating-linear-gradient(
                0deg,
                rgba(32, 40, 32, 0.018) 0px,
                rgba(32, 40, 32, 0.018) 1px,
                transparent 1px,
                transparent 5px
            );
    }

    .stApp, .stApp p, .stApp label, .stApp li {
        color: var(--ink);
    }

    .main .block-container {
        max-width: 1440px;
        padding: 2rem clamp(1rem, 4vw, 4rem) 4rem;
    }

    /* Remove Streamlit chrome */
    #MainMenu,
    footer,
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"] {
        visibility: hidden;
        height: 0;
    }

    /* Editorial masthead */
    .masthead {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        padding: 0.35rem 0 1rem;
        border-bottom: 1px solid var(--ink);
        margin-bottom: 1.5rem;
        animation: reveal 420ms ease-out both;
    }

    .masthead-mark {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.15em;
        text-transform: uppercase;
    }

    .masthead-square {
        display: inline-block;
        width: 12px;
        height: 12px;
        background: var(--rust);
        transform: rotate(45deg);
    }

    .masthead-note {
        color: var(--muted);
        font-size: 0.72rem;
        letter-spacing: 0.08em;
        text-align: right;
        text-transform: uppercase;
    }

    .stApp h1, .stApp h2, .stApp h3 {
        color: var(--ink);
        font-family: 'Fraunces', Georgia, serif;
        font-weight: 500;
        letter-spacing: -0.035em;
    }

    .stApp h1 {
        font-size: clamp(2.3rem, 5vw, 4.3rem);
        line-height: 1.04;
        margin: 0.25rem 0 0.7rem;
    }

    .stApp h2 {
        font-size: clamp(1.6rem, 3vw, 2.3rem);
    }

    .stApp h3 {
        font-size: 1.35rem;
    }

    .stApp [data-testid="stCaptionContainer"] p {
        color: var(--muted);
        font-size: 0.84rem;
        line-height: 1.65;
    }

    .eyebrow {
        color: var(--rust);
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.17em;
        line-height: 1.6;
        text-transform: uppercase;
    }

    .display-copy {
        max-width: 34rem;
        color: var(--muted);
        font-size: 1rem;
        line-height: 1.85;
    }

    .editorial-rule {
        width: 100%;
        height: 1px;
        margin: 1.25rem 0;
        background: var(--rule);
    }

    .number-note {
        color: var(--olive);
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }

    /* Small static editorial panels */
    .paper-panel {
        padding: 1.25rem;
        border: 1px solid var(--rule);
        border-top: 3px solid var(--forest);
        background: rgba(255, 254, 250, 0.62);
    }

    .paper-panel h3 {
        margin: 0.25rem 0 0.6rem;
    }

    .paper-panel p {
        color: var(--muted);
        font-size: 0.85rem;
        line-height: 1.7;
    }

    .paper-panel .panel-index {
        color: var(--rust);
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.13em;
        text-transform: uppercase;
    }

    .section-label {
        padding-bottom: 0.6rem;
        border-bottom: 1px solid var(--rule);
        margin-bottom: 1rem;
        color: var(--muted);
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.13em;
        text-transform: uppercase;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: var(--forest);
        border-right: 1px solid #24342B;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem;
    }

    [data-testid="stSidebar"] * {
        color: var(--paper);
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #E3E5D9;
        line-height: 1.65;
        overflow-wrap: anywhere;
    }

    [data-testid="stSidebar"] hr {
        border-color: rgba(245, 241, 232, 0.25);
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: var(--paper);
        font-family: 'Fraunces', Georgia, serif;
    }

    [data-testid="stSidebar"] [data-testid="stButton"] button {
        background: transparent;
        color: var(--paper);
        border-color: rgba(245, 241, 232, 0.42);
    }

    [data-testid="stSidebar"] [data-testid="stButton"] button:hover {
        background: rgba(245, 241, 232, 0.12);
        border-color: var(--paper);
    }

    /* Buttons */
    [data-testid="stButton"] button,
    [data-testid="stFormSubmitButton"] button {
        min-height: 2.8rem;
        border: 1px solid var(--forest);
        border-radius: 3px;
        background: var(--forest);
        color: var(--white);
        font-family: 'DM Sans', sans-serif;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.015em;
        transition: background 160ms ease, transform 160ms ease,
                    border-color 160ms ease;
    }

    [data-testid="stButton"] button:hover,
    [data-testid="stFormSubmitButton"] button:hover {
        background: var(--rust);
        border-color: var(--rust);
        color: white;
        transform: translateY(-1px);
    }

    [data-testid="stButton"] button:focus-visible,
    [data-testid="stFormSubmitButton"] button:focus-visible,
    [data-testid="stTextInput"] input:focus-visible,
    [data-testid="stChatInput"] textarea:focus-visible {
        outline: 3px solid var(--rust) !important;
        outline-offset: 3px !important;
    }

    /* Inputs */
    [data-testid="stTextInput"] label,
    [data-testid="stTextArea"] label {
        color: var(--ink);
        font-size: 0.78rem;
        font-weight: 700;
    }

    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea {
        border: 1px solid var(--rule);
        border-radius: 3px;
        background: var(--white);
        color: var(--ink);
        font-family: 'DM Sans', sans-serif;
    }

    [data-testid="stTextInput"] input:focus,
    [data-testid="stTextArea"] textarea:focus {
        border-color: var(--forest);
        box-shadow: 0 0 0 1px var(--forest);
    }

    [data-testid="stTextInput"] input::placeholder,
    [data-testid="stChatInput"] textarea::placeholder {
        color: #77786F;
        opacity: 1;
    }

    /* Tabs */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: 1.2rem;
        border-bottom: 1px solid var(--rule);
        background: transparent;
    }

    [data-testid="stTabs"] button[role="tab"] {
        padding: 0.7rem 0.15rem;
        border-radius: 0;
        background: transparent;
        color: var(--muted);
        font-size: 0.83rem;
        font-weight: 600;
    }

    [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        border-bottom: 3px solid var(--rust);
        color: var(--ink);
    }

    [data-testid="stTabs"] button[role="tab"]:focus-visible {
        outline: 2px solid var(--rust);
        outline-offset: 3px;
    }

    /* Forms and expanders */
    [data-testid="stForm"] {
        padding: 1.25rem;
        border: 1px solid var(--rule);
        border-radius: 3px;
        background: rgba(255, 254, 250, 0.72);
    }

    [data-testid="stExpander"] {
        border: 1px solid var(--rule);
        border-radius: 3px;
        background: rgba(255, 254, 250, 0.62);
    }

    [data-testid="stExpander"] summary {
        color: var(--forest);
        font-size: 0.82rem;
        font-weight: 700;
    }

    /* Chat messages */
    [data-testid="stChatMessage"] {
        border: 1px solid var(--rule);
        border-radius: 3px;
        background: rgba(255, 254, 250, 0.7);
        padding: 1rem 1.1rem;
        margin-bottom: 0.8rem;
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: #EAE3D6;
    }

    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] li {
        line-height: 1.75;
    }

    [data-testid="stChatInput"] {
        border: 1px solid var(--forest);
        border-radius: 3px;
        background: var(--white);
    }

    
/* Chat input: force readable text and placeholder colors */
[data-testid="stChatInput"] {
    background-color: #FFFEFA !important;
}

[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] textarea:focus {
    color: #202820 !important;
    -webkit-text-fill-color: #202820 !important;
    caret-color: #C84F32 !important;
    background-color: #FFFEFA !important;
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #66695F !important;
    -webkit-text-fill-color: #66695F !important;
    opacity: 1 !important;
}

    }

    /* Sources */
    .source-heading {
        padding: 0.6rem 0;
        border-bottom: 1px solid var(--rule);
        color: var(--forest);
        font-size: 0.85rem;
        font-weight: 700;
        line-height: 1.5;
        overflow-wrap: anywhere;
    }

    .source-number {
        display: inline-block;
        margin-right: 0.45rem;
        color: var(--rust);
        font-variant-numeric: tabular-nums;
    }

    .source-category {
        color: var(--muted);
        font-size: 0.72rem;
        letter-spacing: 0.04em;
    }

    /* Alerts: keep existing st.error / st.success calls */
    [data-testid="stAlert"] {
        border: 1px solid var(--rule);
        border-left: 4px solid var(--olive);
        border-radius: 2px;
        background: var(--white);
        color: var(--ink);
    }

    [data-testid="stAlert"][kind="error"] {
        border-left-color: var(--danger);
        background: #F8EAE5;
    }

    [data-testid="stAlert"][kind="success"] {
        border-left-color: var(--success);
        background: #E7EFE6;
    }

    [data-testid="stAlert"] p {
        color: var(--ink);
    }

    /* Spinner / progress */
    [data-testid="stSpinner"] p {
        color: var(--forest);
        font-size: 0.84rem;
        font-weight: 600;
    }

    [data-testid="stProgress"] > div > div {
        background: var(--rust);
    }

    /* Entrance motion */
    @keyframes reveal {
        from {
            opacity: 0;
            transform: translateY(7px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .masthead, .paper-panel {
        animation: reveal 420ms ease-out both;
    }

    /* Mobile */
    @media (max-width: 700px) {
        .main .block-container {
            padding: 1.1rem 1rem 3rem;
        }

        .masthead {
            align-items: flex-start;
        }

        .masthead-note {
            max-width: 9rem;
            font-size: 0.62rem;
        }

        .stApp h1 {
            font-size: 2.5rem;
        }

        [data-testid="stForm"] {
            padding: 0.85rem;
        }

        [data-testid="stChatMessage"] {
            padding: 0.8rem;
        }
    }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
            scroll-behavior: auto !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# 3. Load configuration from the project root
# --------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_PUBLISHABLE_KEY = os.getenv(
    "SUPABASE_PUBLISHABLE_KEY"
)
API_URL = os.getenv(
    "API_URL", "http://127.0.0.1:8000"
).rstrip("/")


# --------------------------------------------------
# 4. Shared visual elements
# --------------------------------------------------

st.markdown(
    """
    <div class="masthead">
        <div class="masthead-mark">
            <span class="masthead-square"></span>
            <span>Student Support / Fieldnotes</span>
        </div>
        <div class="masthead-note">
            Academics · Careers · Study
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.title("Student Support AI")
st.caption(
    "A practical place to work through academic questions, "
    "career preparation, and study strategies."
)


def render_source(source):
    """Render source metadata safely, supporting both response formats."""

    citation = source.get(
        "citation",
        source.get("source_id", "?"),
    )
    document_name = html.escape(
        str(source.get("document_name", "Reference document"))
    )
    category = html.escape(
        str(source.get("category", "Uncategorized"))
    )

    st.markdown(
        f"""
        <div class="source-heading">
            <span class="source-number">[{html.escape(str(citation))}]</span>
            {document_name}
        </div>
        <div class="source-category">
            Category: {category}
        </div>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------
# 5. Check frontend configuration
# --------------------------------------------------

if not SUPABASE_URL or not SUPABASE_PUBLISHABLE_KEY:
    st.error(
        "Set SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY "
        "in the project-root .env file."
    )
    st.stop()


# Create a client using only the publishable key.
supabase = create_client(
    SUPABASE_URL,
    SUPABASE_PUBLISHABLE_KEY,
)


# --------------------------------------------------
# 6. Initialize session state
# --------------------------------------------------

if "access_token" not in st.session_state:
    st.session_state.access_token = None

if "messages" not in st.session_state:
    st.session_state.messages = []


# --------------------------------------------------
# 7. Authentication page
# --------------------------------------------------

def show_auth_page():
    """Display the signup and login forms."""

    col_intro, col_auth = st.columns(
        [1.2, 1],
        gap="large",
    )

    with col_intro:
        st.markdown(
            """
            <div class="eyebrow">Your student desk</div>
            <h2 style="font-size:clamp(2rem, 4vw, 3.1rem);
                       line-height:1.12; margin-top:0.6rem;">
                Find your next
                <span style="color:#C84F32;">clear step.</span>
            </h2>
            <p class="display-copy">
                Ask questions about study strategies, academic
                information, and career preparation. Answers are
                grounded in the support documents available to
                this assistant.
            </p>
            <div class="editorial-rule"></div>
            <div class="paper-panel">
                <div class="panel-index">01 / Academics</div>
                <h3>Make sense of the details.</h3>
                <p>
                    Work through academic questions using the
                    information available in the indexed documents.
                </p>
                <div class="panel-index">02 / Career preparation</div>
                <h3>Plan the next move.</h3>
                <p>
                    Use the assistant to explore career-related
                    guidance and study planning.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_auth:
        st.markdown(
            '<div class="section-label">Member access / 01</div>',
            unsafe_allow_html=True,
        )

        login_tab, signup_tab = st.tabs(
            ["Log in", "Create account"]
        )

        with login_tab:
            st.markdown(
                '<div class="eyebrow">Welcome back</div>',
                unsafe_allow_html=True,
            )

            with st.form("login_form"):
                email = st.text_input(
                    "Email",
                    key="login_email",
                    placeholder="you@example.com",
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    key="login_password",
                    placeholder="Enter your password",
                )
                submitted = st.form_submit_button(
                    "Log in",
                    use_container_width=True,
                )

            if submitted:
                if not email.strip() or not password:
                    st.error("Enter your email and password.")
                else:
                    try:
                        response = supabase.auth.sign_in_with_password(
                            {
                                "email": email.strip(),
                                "password": password,
                            }
                        )

                        if response.session:
                            st.session_state.access_token = (
                                response.session.access_token
                            )
                            st.session_state.user_email = email.strip()
                            st.session_state.messages = []
                            st.rerun()
                        else:
                            st.error(
                                "No session was returned. "
                                "Check your email confirmation settings."
                            )

                    except Exception as error:
                        st.error(
                            "Login failed. Check your credentials "
                            "and email confirmation status."
                        )
                        st.caption(str(error)[:300])

        with signup_tab:
            st.markdown(
                '<div class="eyebrow">Start here</div>',
                unsafe_allow_html=True,
            )

            with st.form("signup_form"):
                new_email = st.text_input(
                    "Email address",
                    key="signup_email",
                    placeholder="you@example.com",
                )
                new_password = st.text_input(
                    "Create password",
                    type="password",
                    key="signup_password",
                    help="Use a strong password.",
                    placeholder="At least 8 characters",
                )
                confirm_password = st.text_input(
                    "Confirm password",
                    type="password",
                    placeholder="Enter the same password again",
                )
                signup_submitted = st.form_submit_button(
                    "Create account",
                    use_container_width=True,
                )

            if signup_submitted:
                if not new_email.strip():
                    st.error("Enter your email address.")
                elif len(new_password) < 8:
                    st.error(
                        "Use a password with at least 8 characters."
                    )
                elif new_password != confirm_password:
                    st.error("The passwords do not match.")
                else:
                    try:
                        response = supabase.auth.sign_up(
                            {
                                "email": new_email.strip(),
                                "password": new_password,
                            }
                        )

                        if response.session:
                            st.session_state.access_token = (
                                response.session.access_token
                            )
                            st.session_state.user_email = (
                                new_email.strip()
                            )
                            st.session_state.messages = []
                            st.success("Account created successfully.")
                            st.rerun()
                        else:
                            st.success(
                                "Signup submitted. Check your email "
                                "for a confirmation link, then log in."
                            )

                    except Exception as error:
                        st.error("Account creation failed.")
                        st.caption(str(error)[:300])


# --------------------------------------------------
# 8. Authenticated chatbot page
# --------------------------------------------------

def show_chat_page():
    """Display the authenticated chatbot."""

    email = st.session_state.get(
        "user_email", "Student"
    )

    with st.sidebar:
        st.markdown(
            """
            <div class="eyebrow" style="color:#E8A18E;">
                Student desk / Signed in
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.subheader("Your workspace")
        st.write(f"Signed in as: {email}")
        st.divider()

        if st.button("Clear chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        if st.button("Log out", use_container_width=True):
            st.session_state.access_token = None
            st.session_state.pop("user_email", None)
            st.session_state.messages = []
            st.rerun()

        st.markdown(
            """
            <div style="margin-top:2rem; padding-top:1rem;
                        border-top:1px solid rgba(245,241,232,.25);">
                <div style="color:#E8A18E; font-size:.68rem;
                            font-weight:700; letter-spacing:.13em;">
                    HOW IT WORKS
                </div>
                <p style="font-size:.8rem; line-height:1.7;">
                    Your question is matched with relevant document
                    passages before the assistant prepares an answer.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    main_col, rail_col = st.columns(
        [2.25, 1],
        gap="large",
    )

    with main_col:
        st.markdown(
            """
            <div class="eyebrow">Conversation / Student support</div>
            <h2 style="margin-top:.35rem;">What are you working through?</h2>
            <p class="display-copy" style="font-size:.9rem;">
                Ask one clear question. Relevant source documents
                appear beneath answers when available.
            </p>
            <div class="editorial-rule"></div>
            """,
            unsafe_allow_html=True,
        )

        if not st.session_state.messages:
            st.markdown(
                """
                <div class="paper-panel">
                    <div class="panel-index">A note before you begin</div>
                    <h3>Your question sets the direction.</h3>
                    <p>
                        Ask about a topic, a process, or a study challenge.
                        The assistant searches its indexed student-support
                        documents and uses relevant passages to shape
                        its response. If the documents do not cover
                        something, the answer may say so.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Render previous messages.
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

                if message["role"] == "assistant":
                    sources = message.get("sources", [])

                    if sources:
                        with st.expander("View sources"):
                            for source in sources:
                                render_source(source)

    with rail_col:
        st.markdown(
            """
            <div class="section-label">Field guide / 01</div>
            <div class="paper-panel">
                <div class="panel-index">Ask with context</div>
                <h3>Be specific.</h3>
                <p>
                    Include the subject, task, or situation you need
                    help with. A focused question makes it easier to
                    find relevant passages.
                </p>
            </div>
            <div style="height:1rem;"></div>
            <div class="paper-panel"
                 style="border-top-color:#C84F32;">
                <div class="panel-index">Sources matter</div>
                <h3>Check the evidence.</h3>
                <p>
                    Open “View sources” under an answer to inspect
                    the documents used as context. Verify important
                    institutional decisions with the appropriate
                    official source.
                </p>
            </div>
            <div style="height:1.25rem;"></div>
            <div class="number-note">
                Academics / Careers / Study strategies
            </div>
            """,
            unsafe_allow_html=True,
        )

    question = st.chat_input(
        "Ask about academics, careers, or study strategies..."
    )

    if question:
        st.session_state.messages.append(
            {"role": "user", "content": question}
        )

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner(
                "Searching documents and preparing your answer..."
            ):
                try:
                    token = st.session_state.access_token

                    response = httpx.post(
                        f"{API_URL}/chat",
                        json={
                            "question": question,
                            "match_count": 5,
                        },
                        headers={
                            "Authorization": f"Bearer {token}"
                        },
                        timeout=120.0,
                    )

                    response.raise_for_status()
                    data = response.json()

                    answer = data.get(
                        "answer",
                        "No answer was returned.",
                    )
                    sources = data.get("sources", [])

                    st.markdown(answer)

                    if sources:
                        with st.expander("View sources"):
                            for source in sources:
                                render_source(source)

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer,
                            "sources": sources,
                        }
                    )

                except httpx.HTTPStatusError as error:
                    if error.response.status_code == 401:
                        st.error(
                            "Your login session may have expired. "
                            "Please log in again."
                        )
                    else:
                        st.error(
                            f"Backend error: "
                            f"HTTP {error.response.status_code}"
                        )
                        st.caption(error.response.text[:500])

                except httpx.RequestError:
                    st.error(
                        "Cannot connect to FastAPI. "
                        "Check that the backend is running."
                    )


# --------------------------------------------------
# 9. Choose which page to display
# --------------------------------------------------

if st.session_state.access_token:
    show_chat_page()
else:
    show_auth_page()
