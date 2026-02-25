import logging
import os
import sys
from io import BytesIO
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import streamlit as st
import trafilatura
from pypdf import PdfReader
import google.generativeai as genai

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("babs_assistant.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("BabsAssistant")

ASSISTANT_NAME = "Babs Leye"
MAX_CONTENT_LENGTH = 120000
SUMMARY_PROMPT = """You are Babs Leye, a friendly and knowledgeable AI assistant. 
You have a warm, approachable personality - helpful but never condescending. 
You're passionate about making information accessible and love helping people understand complex topics.

Summarize the following content in a clear, engaging way. 
Keep the summary concise (2-4 paragraphs) but capture the key points and main ideas.
Write in a conversational tone, as if you're explaining it to a friend over coffee.
If the content seems incomplete or truncated, mention that in your summary.

Content to summarize:
"""


def get_gemini_client() -> bool:
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets.get("GOOGLE_API_KEY") or st.secrets.get("GEMINI_API_KEY")
        except Exception:
            pass
    if not api_key:
        logger.warning("GOOGLE_API_KEY or GEMINI_API_KEY not set")
        return False
    genai.configure(api_key=api_key)
    return True


def extract_article_from_url(url: str) -> tuple[str, Optional[str]]:
    try:
        logger.info(f"Fetching article from URL: {url[:80]}...")
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return "", "Could not fetch the URL. Check if the link is valid and accessible."
        text = trafilatura.extract(downloaded)
        if not text or len(text.strip()) < 50:
            return "", "Could not extract meaningful content from this URL. It may not be an article page."
        text = text.strip()
        if len(text) > MAX_CONTENT_LENGTH:
            text = text[:MAX_CONTENT_LENGTH] + "\n\n[Content truncated due to length...]"
            logger.info(f"Truncated content to {MAX_CONTENT_LENGTH} chars")
        logger.info(f"Successfully extracted {len(text)} characters from URL")
        return text, None
    except Exception as e:
        logger.exception(f"Error extracting article from URL: {e}")
        return "", f"Failed to fetch or parse the article: {str(e)}"


def extract_text_from_pdf(uploaded_file) -> tuple[str, Optional[str]]:
    try:
        logger.info("Processing uploaded PDF file")
        pdf_reader = PdfReader(BytesIO(uploaded_file.read()))
        text_parts = []
        for page_num, page in enumerate(pdf_reader.pages, 1):
            try:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            except Exception as page_err:
                logger.warning(f"Could not extract page {page_num}: {page_err}")
                continue
        if not text_parts:
            return "", "Could not extract any text from this PDF. It may be scanned or image-based."
        full_text = "\n\n".join(text_parts)
        if len(full_text) > MAX_CONTENT_LENGTH:
            full_text = full_text[:MAX_CONTENT_LENGTH] + "\n\n[Content truncated due to length...]"
            logger.info(f"Truncated PDF content to {MAX_CONTENT_LENGTH} chars")
        logger.info(f"Successfully extracted {len(full_text)} characters from PDF ({len(pdf_reader.pages)} pages)")
        return full_text, None
    except Exception as e:
        logger.exception(f"Error processing PDF: {e}")
        return "", f"Failed to process PDF: {str(e)}"


GEMINI_MODELS = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-pro"]


def _generate(prompt: str, model_name: str, max_tokens: int = 500) -> tuple[str, Optional[str]]:
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.7, "max_output_tokens": max_tokens},
        )
        if not response.text:
            return "", "Could not generate a response."
        return response.text.strip(), None
    except Exception as e:
        return "", str(e)


def chat_with_assistant(user_message: str) -> tuple[str, Optional[str]]:
    prompt = f"""You are {ASSISTANT_NAME}, a friendly AI assistant. You have a warm, approachable personality.
When asked about yourself, say your name is Babs Leye and you're an AI assistant created by Babs Leye.
Keep responses concise and friendly. Answer in the same language as the user's question.

User: {user_message}

Answer:"""
    for model_name in GEMINI_MODELS:
        result, err = _generate(prompt, model_name, 500)
        if not err:
            return result, None
        if "404" in err or "not found" in err.lower():
            logger.warning(f"Model {model_name} not available, trying next")
            continue
        logger.exception(f"Chat error: {err}")
        return "", f"Error: {err}"
    return "", "No compatible Gemini model available. Try updating your API key."


def summarize_content(content: str) -> tuple[str, Optional[str]]:
    logger.info("Generating summary via Gemini")
    prompt = SUMMARY_PROMPT + content
    for model_name in GEMINI_MODELS:
        summary, err = _generate(prompt, model_name, 1000)
        if not err:
            logger.info("Summary generated successfully")
            return summary, None
        if "404" in err or "not found" in err.lower():
            logger.warning(f"Model {model_name} not available, trying next")
            continue
        error_msg = err
        if "rate limit" in error_msg.lower() or "429" in error_msg or "quota" in error_msg.lower():
            return "", "Rate limit exceeded. Please try again in a few moments."
        if "invalid" in error_msg.lower() or "api key" in error_msg.lower() or "api_key" in error_msg.lower():
            return "", "Invalid API configuration. Please check your GOOGLE_API_KEY or GEMINI_API_KEY."
        logger.exception(f"Summarization error: {err}")
        return "", f"Failed to generate summary: {error_msg}"
    return "", "No compatible Gemini model available."


def render_sidebar():
    with st.sidebar:
        st.markdown("### 🤖")
        st.title(f"👋 Hi, I'm {ASSISTANT_NAME}!")
        st.markdown("""
        I'm your friendly AI assistant. I love helping you understand articles and documents!
        
        **What I can do:**
        - 📰 Summarize articles from any link
        - 📄 Summarize PDF documents
        
        Just paste a URL or upload a PDF, and I'll give you a clear, engaging summary.
        """)
        st.divider()
        st.caption("Built with ❤️ by Babs Leye")


def main():
    st.set_page_config(
        page_title=f"{ASSISTANT_NAME} - AI Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    render_sidebar()
    st.title(f"🤖 {ASSISTANT_NAME} AI Assistant")
    st.markdown("*Your friendly article summarizer — making information accessible, one summary at a time!*")
    if not get_gemini_client():
        st.error(
            "⚠️ **Google Gemini API Key Required**\n\n"
            "To use this assistant, please set the `GOOGLE_API_KEY` or `GEMINI_API_KEY`. "
            "Get a free key at [Google AI Studio](https://aistudio.google.com/app/apikey).\n\n"
            "On Streamlit Cloud: App settings → Secrets → add GOOGLE_API_KEY"
        )
        st.stop()
    st.divider()
    if "messages" not in st.session_state:
        st.session_state.messages = []
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    if prompt := st.chat_input("Pose une question (ex: C'est quoi ton nom ?)"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("..."):
                reply, err = chat_with_assistant(prompt)
                if err:
                    st.error(err)
                else:
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.divider()
    st.subheader("📰 Résumer un article ou un PDF")
    input_method = st.radio(
        "How would you like to provide content?",
        ["🔗 Paste a link (URL)", "📄 Upload a PDF"],
        horizontal=True,
    )
    content = ""
    source_info = ""
    if "Paste a link" in input_method:
        url = st.text_input("Enter article URL", placeholder="https://example.com/article")
        if st.button("Summarize Article", type="primary"):
            if not url or not url.strip():
                st.warning("Please enter a valid URL.")
            else:
                with st.spinner("Fetching and analyzing the article..."):
                    content, error = extract_article_from_url(url.strip())
                    if error:
                        st.error(f"❌ {error}")
                        logger.error(f"URL extraction failed: {error}")
                    else:
                        source_info = f"Article from: {url}"
    else:
        uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
        if uploaded_file and st.button("Summarize PDF", type="primary"):
            with st.spinner("Reading and analyzing your PDF..."):
                content, error = extract_text_from_pdf(uploaded_file)
                if error:
                    st.error(f"❌ {error}")
                    logger.error(f"PDF extraction failed: {error}")
                else:
                    source_info = f"PDF: {uploaded_file.name}"
    if content and source_info:
        with st.spinner("Crafting your summary..."):
            summary, error = summarize_content(content)
            if error:
                st.error(f"❌ {error}")
                logger.error(f"Summarization failed: {error}")
            else:
                st.success("Here's your summary!")
                st.markdown("---")
                st.markdown(summary)
                st.caption(f"*Summarized by {ASSISTANT_NAME} • Source: {source_info}*")
                logger.info("Summary displayed successfully")


if __name__ == "__main__":
    main()
