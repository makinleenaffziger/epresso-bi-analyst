import hashlib

import pandas as pd
import streamlit as st

from agent import answer_question

# Import Gemini lazily so the rules-based assistant still works without its SDK.


def show_assistant(data, year=None, channel=None, category=None):
    """Display the rules-based assistant and its calculation logs."""

    st.subheader("E-Presso analytical assistant")
    st.caption(
        "Ask about revenue by store type, year, or month. "
        "Answers use your currently uploaded data and dashboard filters."
    )

    with st.expander("Supported questions", expanded=True):
        st.write("- Compare revenue by store type")
        st.write("- Which store type has the most revenue?")
        st.write("- Show revenue by year")
        st.write("- Show monthly revenue shares")
        st.write("- Does revenue tell us profit?")
        st.write(
            "Select the year, store type, and category using the "
            "dashboard filters before asking."
        )

    if "assistant_count" not in st.session_state:
        st.session_state.assistant_count = 0

    if "assistant_history" not in st.session_state:
        st.session_state.assistant_history = []

    # Clear old answers when data or filters change.
    # The question counter remains unchanged.
    fingerprint = hashlib.sha256(
        pd.util.hash_pandas_object(data, index=True).values.tobytes()
    ).hexdigest()

    context = (
        fingerprint,
        tuple(data.columns),
        year,
        channel,
        category
    )

    if st.session_state.get("assistant_context") != context:
        st.session_state.assistant_history = []
        st.session_state.assistant_context = context

    use_gemini = st.checkbox("Use Gemini", value=False)

    count = st.session_state.assistant_count
    st.caption(f"Questions used this session: {count} of 15")

    if count >= 15:
        st.info(
            "You have reached this session's 15-question limit. "
            "You can continue exploring the dashboard."
        )

    question = st.chat_input(
        "Enter a supported business question",
        disabled=count >= 15,
        key="epresso_question"
    )

    if question:
        st.session_state.assistant_count += 1

        try:
            responder = answer_question
            extra = {}
            if use_gemini:
                from gemini_agent import answer_with_gemini
                responder = answer_with_gemini
                extra = {"api_key": st.secrets["GEMINI_API_KEY"]}
            response = responder(
                data,
                question,
                year=year,
                channel=channel,
                category=category,
                store=None,
                **extra
            )
        except Exception:
            response = {
                "scope": (
                    f"Scope: year={year}; store type={channel}; "
                    f"category={category}; all stores."
                ),
                "findings": "The assistant could not complete this request.",
                "interpretation": "No analytical conclusion is available.",
                "next_steps": "Check your data and try a supported question.",
                "tool_log": None
            }

        st.session_state.assistant_history.append({
            "question": question,
            "response": response
        })

    for entry in st.session_state.assistant_history:
        with st.chat_message("user"):
            st.write(entry["question"])

        response = entry["response"]

        with st.chat_message("assistant"):
            st.caption(response.get("mode", "Rules-based"))
            st.write(response["scope"])

            st.markdown("**Findings**")
            st.markdown(response["findings"])

            st.markdown("**Interpretation**")
            st.write(response["interpretation"])

            st.markdown("**Next steps**")
            st.write(response["next_steps"])

            if response["tool_log"] is not None:
                with st.expander("Tool-call log", expanded=True):
                    st.json(response["tool_log"])
            else:
                st.caption("No analytical tool was run for this request.")