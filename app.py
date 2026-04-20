import streamlit as st
from backend import run
from datetime import date
import json

# ===================== PAGE CONFIG =====================

st.set_page_config(
    page_title="AI Agent Blogger",
    page_icon="✏️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===================== PROFESSIONAL STYLING =====================

st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background-color: #f5f7fa;
    }
    
    .main {
        background-color: #ffffff;
    }
    
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 40px 0;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        border-radius: 0;
    }
    
    .header-container h1 {
        font-size: 2.5em;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin-bottom: 10px;
    }
    
    .header-container p {
        font-size: 1.1em;
        font-weight: 300;
        letter-spacing: 0.5px;
        opacity: 0.95;
    }
    
    .config-section {
        background-color: #ffffff;
        border: 1px solid #e8eef5;
        border-radius: 8px;
        padding: 25px;
        margin-bottom: 20px;
    }
    
    .config-section label {
        font-weight: 600;
        color: #2d3748;
        font-size: 0.95em;
        display: block;
        margin-bottom: 8px;
    }
    
    .section-title {
        font-size: 1.4em;
        font-weight: 700;
        color: #2d3748;
        margin-bottom: 25px;
        padding-bottom: 15px;
        border-bottom: 2px solid #e8eef5;
    }
    
    .result-container {
        background-color: #f9fafb;
        border: 1px solid #e8eef5;
        border-radius: 8px;
        padding: 30px;
        margin: 20px 0;
    }
    
    .plan-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px;
        background-color: #f0f4f8;
        border-radius: 6px;
        margin-bottom: 15px;
    }
    
    .plan-value {
        font-weight: 600;
        color: #667eea;
        font-size: 1.05em;
    }
    
    .section-card {
        border: 1px solid #e8eef5;
        border-radius: 6px;
        padding: 18px;
        margin: 12px 0;
        background-color: #ffffff;
        transition: all 0.2s ease;
    }
    
    .section-card:hover {
        border-color: #667eea;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
    }
    
    .section-goal {
        font-size: 0.95em;
        color: #4a5568;
        margin: 10px 0;
        line-height: 1.6;
    }
    
    .bullet-list {
        margin: 12px 0;
        padding-left: 20px;
    }
    
    .bullet-item {
        margin: 8px 0;
        color: #4a5568;
        line-height: 1.5;
    }
    
    .flag-container {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin: 10px 0;
    }
    
    .flag {
        background-color: #e6f2ff;
        color: #2952cc;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.85em;
        font-weight: 500;
    }
    
    .evidence-card {
        border-left: 4px solid #667eea;
        padding: 18px;
        margin: 15px 0;
        background-color: #f9fafb;
        border-radius: 4px;
    }
    
    .evidence-title {
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 8px;
        font-size: 1em;
    }
    
    .evidence-meta {
        font-size: 0.9em;
        color: #718096;
        margin: 5px 0;
    }
    
    .evidence-snippet {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 12px;
        border-radius: 4px;
        font-size: 0.9em;
        color: #4a5568;
        margin-top: 10px;
        line-height: 1.5;
    }
    
    .metadata-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        margin: 20px 0;
    }
    
    .metadata-item {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 6px;
        border: 1px solid #e8eef5;
    }
    
    .metadata-label {
        font-weight: 600;
        color: #667eea;
        font-size: 0.9em;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    
    .metadata-value {
        color: #2d3748;
        font-size: 1.1em;
        font-weight: 500;
    }
    
    .button-row {
        display: flex;
        gap: 10px;
        margin-top: 20px;
    }
    
    .footer {
        text-align: center;
        padding: 30px 0;
        color: #718096;
        font-size: 0.9em;
        border-top: 1px solid #e8eef5;
        margin-top: 40px;
    }
    
    .info-box {
        background-color: #eff6ff;
        border-left: 4px solid #3b82f6;
        padding: 15px;
        border-radius: 4px;
        color: #1e40af;
        font-size: 0.95em;
        line-height: 1.6;
        margin: 15px 0;
    }
    
    .success-box {
        background-color: #f0fdf4;
        border-left: 4px solid #10b981;
        padding: 15px;
        border-radius: 4px;
        color: #065f46;
        font-size: 0.95em;
        font-weight: 500;
        margin: 15px 0;
    }
    
    .error-box {
        background-color: #fef2f2;
        border-left: 4px solid #ef4444;
        padding: 15px;
        border-radius: 4px;
        color: #7f1d1d;
        font-size: 0.95em;
        font-weight: 500;
        margin: 15px 0;
    }
    
    .divider {
        border-bottom: 1px solid #e8eef5;
        margin: 25px 0;
    }
    
    .tab-content {
        padding: 25px 0;
    }
</style>
""", unsafe_allow_html=True)

# ===================== INITIALIZE SESSION STATE =====================

if "blog_result" not in st.session_state:
    st.session_state.blog_result = None

if "is_generating" not in st.session_state:
    st.session_state.is_generating = False

if "topic_value" not in st.session_state:
    st.session_state.topic_value = "write a blog on "

if "date_value" not in st.session_state:
    st.session_state.date_value = date.today()


# ===================== HEADER =====================

st.markdown("""
<div class="header-container">
    <h1>AI Blogger</h1>
    <p>Technical Blog Content Generation</p>
</div>
""", unsafe_allow_html=True)

# ===================== SIDEBAR - CONFIGURATION =====================

with st.sidebar:
    st.markdown('<div style="padding: 0px 0;"><h2 style="font-size: 1.3em; color: #00000; margin-bottom: 20px;">Configuration</h2></div>', unsafe_allow_html=True)
    
    
    as_of_date = st.date_input(
        "Reference Date",
        value=st.session_state.date_value,
        help="The date for which this blog is being written"
    )
    st.session_state.date_value = as_of_date
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    st.markdown('<h3 style="font-size: 1.1em; color: #00000; margin-bottom: 15px;">How It Works</h3>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <strong>Process Overview</strong><br>
        1. Submit your blog topic<br>
        2. AI determines research requirements<br>
        3. Automatic outline generation<br>
        4. Content generation for each section<br>
        5. Visual elements added<br>
        6. Final blog post delivery
    </div>
    """, unsafe_allow_html=True)

# ===================== MAIN CONTENT =====================

topic, col_button = st.columns([3, 1])

topic = st.text_input(
    "Blog Topic",
    value=st.session_state.topic_value,
    placeholder="Enter your blog topic here...",
    help="What would you like to write about?",
    key="topic_input"
)
st.session_state.topic_value = topic

generate_clicked = st.button("Generate Blog", use_container_width=True, type="primary")


# ===================== GENERATION LOGIC =====================

if generate_clicked:
    if not topic.strip():
        st.markdown('<div class="error-box">Please enter a blog topic to proceed.</div>', unsafe_allow_html=True)
    else:
        st.session_state.is_generating = True

if st.session_state.is_generating and topic.strip():
    with st.spinner("Processing your request..."):
        try:
            progress_placeholder = st.empty()
            progress_placeholder.markdown('<div class="info-box">Generating content. This may take several minutes...</div>', unsafe_allow_html=True)
            
            as_of_str = as_of_date.isoformat()
            
            result = run(topic=topic, as_of=as_of_str)
            
            st.session_state.blog_result = result
            st.session_state.is_generating = False
            
            progress_placeholder.markdown('<div class="success-box">Blog post generated successfully.</div>', unsafe_allow_html=True)
            
        except Exception as e:
            st.session_state.is_generating = False
            st.markdown(f'<div class="error-box">Error: {str(e)}</div>', unsafe_allow_html=True)
            with st.expander("Error Details"):
                st.code(str(e), language="text")

# ===================== DISPLAY RESULTS =====================

if st.session_state.blog_result:
    result = st.session_state.blog_result
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="success-box">Blog post is ready for download and review.</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["Blog Content", "Plan Overview", "Research Sources", "Generation Details"])
    
    # ===================== TAB 1: BLOG CONTENT =====================
    with tab1:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-title">Final Blog Post</h3>', unsafe_allow_html=True)
        
        if result.get("final"):
            st.markdown(result["final"])
            
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            st.markdown('<h4 style="color: #2d3748; margin-bottom: 15px;">Download Options</h4>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="Download as Markdown",
                    data=result["final"],
                    file_name=f"{result.get('plan', {}).get('blog_title', 'blog')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            with col2:
                st.download_button(
                    label="Download as Text",
                    data=result["final"],
                    file_name=f"{result.get('plan', {}).get('blog_title', 'blog')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ===================== TAB 2: PLAN OVERVIEW =====================
    with tab2:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-title">Content Outline</h3>', unsafe_allow_html=True)
        
        plan = result.get("plan")
        if plan:
            # Plan metadata
            st.markdown('<h4 style="color: #2d3748; margin-bottom: 20px; font-weight: 600;">Blog Configuration</h4>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div class="metadata-grid">
                    <div class="metadata-item">
                        <div class="metadata-label">Title</div>
                        <div class="metadata-value">{plan.get('blog_title', 'N/A')}</div>
                    </div>
                    <div class="metadata-item">
                        <div class="metadata-label">Audience</div>
                        <div class="metadata-value">{plan.get('audience', 'N/A')}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metadata-grid">
                    <div class="metadata-item">
                        <div class="metadata-label">Tone</div>
                        <div class="metadata-value">{plan.get('tone', 'N/A')}</div>
                    </div>
                    <div class="metadata-item">
                        <div class="metadata-label">Type</div>
                        <div class="metadata-value">{plan.get('blog_kind', 'N/A')}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            if plan.get("constraints"):
                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                st.markdown('<h4 style="color: #2d3748; margin-bottom: 12px; font-weight: 600;">Constraints</h4>', unsafe_allow_html=True)
                for constraint in plan.get("constraints", []):
                    st.markdown(f'<div class="bullet-item">• {constraint}</div>', unsafe_allow_html=True)
            
            # Sections
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            st.markdown(f'<h4 style="color: #2d3748; margin-bottom: 15px; font-weight: 600;">Sections ({len(plan.get("tasks", []))})</h4>', unsafe_allow_html=True)
            
            for idx, task in enumerate(plan.get("tasks", []), 1):
                with st.expander(f"Section {idx}: {task.get('title', 'Untitled')}"):
                    st.markdown(f"""
                    <div class="section-card">
                        <div style="margin-bottom: 12px;">
                            <strong>Goal:</strong>
                            <div class="section-goal">{task.get('goal', 'N/A')}</div>
                        </div>
                        <div style="margin-bottom: 12px;">
                            <strong>Target Word Count:</strong> {task.get('target_words', 'N/A')}
                        </div>
                        <div style="margin-bottom: 12px;">
                            <strong>Bullets:</strong>
                            <div class="bullet-list">
                    """, unsafe_allow_html=True)
                    
                    for bullet in task.get("bullets", []):
                        st.markdown(f'<div class="bullet-item">• {bullet}</div>', unsafe_allow_html=True)
                    
                    # Flags
                    flags = []
                    if task.get("requires_research"):
                        flags.append("Research Required")
                    if task.get("requires_citations"):
                        flags.append("Citations Required")
                    if task.get("requires_code"):
                        flags.append("Code Included")
                    
                    if flags:
                        st.markdown('</div></div><div class="flag-container">', unsafe_allow_html=True)
                        for flag in flags:
                            st.markdown(f'<span class="flag">{flag}</span>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('</div></div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ===================== TAB 3: RESEARCH SOURCES =====================
    with tab3:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-title">Research Evidence</h3>', unsafe_allow_html=True)
        
        evidence = result.get("evidence", [])
        
        if evidence:
            st.markdown(f'<p style="color: #4a5568; margin-bottom: 20px;"><strong>Total Sources:</strong> {len(evidence)}</p>', unsafe_allow_html=True)
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            
            for idx, item in enumerate(evidence, 1):
                source_title = item.get('title', 'Untitled')
                source_url = item.get('url', '#')
                source_name = item.get('source', 'Unknown Source')
                published = item.get('published_at', 'Unknown Date')
                snippet = item.get('snippet', '')
                
                st.markdown(f"""
                <div class="evidence-card">
                    <div class="evidence-title">{idx}. {source_title}</div>
                    <div class="evidence-meta">Source: {source_name}</div>
                    <div class="evidence-meta">Published: {published}</div>
                    <a href="{source_url}" target="_blank" style="color: #667eea; text-decoration: none; font-weight: 500;">Visit Source</a>
                    {f'<div class="evidence-snippet">{snippet}</div>' if snippet else ''}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="info-box">No external research was required for this topic. Content generated from existing knowledge.</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ===================== TAB 4: GENERATION DETAILS =====================
    with tab4:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-title">Generation Information</h3>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="metadata-grid">
                <div class="metadata-item">
                    <div class="metadata-label">Topic</div>
                    <div class="metadata-value" style="word-wrap: break-word;">{result.get('topic', 'N/A')}</div>
                </div>
                <div class="metadata-item">
                    <div class="metadata-label">Processing Mode</div>
                    <div class="metadata-value">{result.get('mode', 'N/A')}</div>
                </div>
                <div class="metadata-item">
                    <div class="metadata-label">Research Required</div>
                    <div class="metadata-value">{'Yes' if result.get('needs_research') else 'No'}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metadata-grid">
                <div class="metadata-item">
                    <div class="metadata-label">Reference Date</div>
                    <div class="metadata-value">{result.get('as_of', 'N/A')}</div>
                </div>
                <div class="metadata-item">
                    <div class="metadata-label">Recency Window</div>
                    <div class="metadata-value">{result.get('recency_days', 'N/A')} days</div>
                </div>
                <div class="metadata-item">
                    <div class="metadata-label">Total Sections</div>
                    <div class="metadata-value">{len(result.get('plan', {}).get('tasks', []))}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if result.get("image_specs"):
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            st.markdown(f'<h4 style="color: #2d3748; margin-bottom: 15px; font-weight: 600;">Generated Images ({len(result.get("image_specs", []))})</h4>', unsafe_allow_html=True)
            
            for idx, img in enumerate(result.get('image_specs', []), 1):
                with st.expander(f"Image {idx}: {img.get('filename', 'image')}"):
                    st.markdown(f"""
                    <div class="metadata-grid">
                        <div class="metadata-item">
                            <div class="metadata-label">Filename</div>
                            <div class="metadata-value">{img.get('filename', 'N/A')}</div>
                        </div>
                        <div class="metadata-item">
                            <div class="metadata-label">Dimensions</div>
                            <div class="metadata-value">{img.get('size', 'N/A')}</div>
                        </div>
                        <div class="metadata-item">
                            <div class="metadata-label">Quality</div>
                            <div class="metadata-value">{img.get('quality', 'N/A')}</div>
                        </div>
                    </div>
                    <div style="margin-top: 15px;">
                        <strong style="color: #2d3748;">Alt Text:</strong>
                        <p style="color: #4a5568; margin-top: 5px;">{img.get('alt', 'N/A')}</p>
                    </div>
                    <div style="margin-top: 15px;">
                        <strong style="color: #2d3748;">Caption:</strong>
                        <p style="color: #4a5568; margin-top: 5px;">{img.get('caption', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ===================== ACTION BUTTONS =====================
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    col_reset, col_spacer = st.columns([1, 4])
    with col_reset:
        if st.button("Generate Another Blog", use_container_width=True):
            st.session_state.blog_result = None
            st.session_state.is_generating = False
            st.rerun()


