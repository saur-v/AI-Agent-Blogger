# AI Agent Blogger

An automated technical blog content generation system that uses AI to research topics, create outlines, and generate complete blog posts with images.

## Overview

AI Agent Blogger is a tool that takes a blog topic and automatically generates a complete, well-structured technical blog post. The system:

- Analyzes the topic to determine if research is needed
- Searches the web for relevant information when necessary
- Creates a detailed content outline with sections and goals
- Generates original content for each section in parallel
- Adds relevant images and diagrams
- Delivers a polished, ready-to-publish blog post

## Features

- Intelligent routing that decides whether research is needed
- Three processing modes: closed_book (no research), hybrid (some research), and open_book (web research)
- Parallel content generation for faster processing
- Automatic image generation for visual clarity
- Web research using Tavily Search API
- Support for multiple blog types: explainer, tutorial, news roundup, comparison, and system design
- Interactive web interface with Streamlit
- Download blog posts in Markdown or text format
- Detailed generation information and source tracking

## Tech Stack

- Python 3.9+
- Streamlit (frontend web interface)
- LangGraph (workflow orchestration)
- LangChain (LLM integration)
- Together AI (LLM API - Llama 3.3 70B)
- Tavily Search (web research)
- Pydantic (data validation)

## Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- API keys for:
  - Together AI (for LLM access)
  - Tavily Search (for web search)

### Setup Steps

1. Clone the repository:
```bash
git clone https://github.com/saur-v/AI-Agent-Blogger.git
cd AI-Agent-Blogger
```

2. Create a virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a .env file in the project root:
```
TOGETHER_API_KEY=your_together_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
OPENAI_API_BASE=https://api.together.ai/v1
```

## Usage

### Running the Application

Start the Streamlit app:
```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

### How to Generate a Blog

1. Enter your blog topic in the text input field
2. Optionally select a reference date (defaults to today)
3. Click "Generate Blog"
4. Wait for processing (typically 2-5 minutes depending on topic complexity)
5. View results in different tabs:
   - Blog Content: The final generated blog post
   - Plan Overview: The outline and section details
   - Research Sources: Web research results used
   - Generation Details: Processing information and generated images

### Download Options

After generation, you can download:
- Markdown format (.md) - preserves all formatting
- Plain text format (.txt) - basic text version

## Project Structure

```
AI-Agent-Blogger/
├── app.py                 # Streamlit frontend interface
├── backend.py             # LangGraph workflow and processing logic
├── .env                   # Environment variables (not in repo)
├── .gitignore             # Git ignore rules
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── images/                # Generated images directory
└── *.ipynb                # Jupyter notebooks for development
```

## File Descriptions

### app.py
The Streamlit web interface. Handles:
- User input for blog topics and dates
- Display of generated content
- Tab-based result viewing
- Download functionality
- Professional UI styling

### backend.py
Core processing engine using LangGraph. Contains:
- Data models (Plan, Task, EvidenceItem, etc.)
- Router node: determines if research is needed
- Research node: performs web searches and extracts evidence
- Orchestrator node: creates detailed content outline
- Worker nodes: generates content for each section in parallel
- Reducer subgraph: merges sections, generates images, produces final output

## How It Works

### Processing Flow

1. Router Phase
   - Analyzes topic to decide research requirements
   - Selects processing mode (closed_book/hybrid/open_book)
   - Generates search queries if needed

2. Research Phase (if needed)
   - Searches the web for relevant sources
   - Extracts and deduplicates evidence
   - Filters for authoritative sources

3. Planning Phase
   - Creates 5-9 sections with specific goals
   - Defines 3-5 bullets per section
   - Sets target word counts
   - Marks sections requiring code, research, or citations

4. Generation Phase
   - Generates content for each section in parallel
   - Respects section goals and bullet points
   - Includes code snippets when needed
   - Cites research sources appropriately

5. Refinement Phase
   - Merges all sections into coherent blog post
   - Identifies optimal image locations
   - Generates images using AI
   - Creates final formatted output

## Configuration

### Environment Variables

- `TOGETHER_API_KEY`: API key for Together AI (required for LLM)
- `TAVILY_API_KEY`: API key for Tavily Search (required for research)
- `OPENAI_API_BASE`: Base URL for Together AI API (default: https://api.together.ai/v1)

### Customizable Parameters

In `backend.py`, you can adjust:
- LLM model selection (line 122)
- Temperature and max tokens for LLM
- Max search results per query (line 217)
- Image generation parameters (line 507)
- Number of sections (line 244)

## Requirements

See `requirements.txt` for full list. Main dependencies:

```
streamlit>=1.28.0
langgraph>=0.0.39
langchain>=0.1.0
langchain-openai>=0.0.8
langchain-community>=0.0.10
together>=0.2.0
tavily-python>=0.3.0
pydantic>=2.0.0
requests>=2.31.0
python-dotenv>=1.0.0
```

## Limitations

- Blog generation can take 2-5 minutes depending on complexity
- Requires active internet for research and image generation
- Image generation quality depends on API availability
- Generated blogs are approximately 1500-2500 words
- Research limited to top 5 sources per query

## Error Handling

The system includes graceful error handling:
- Failed image generation shows a fallback error block with generation details
- Missing research sources default to knowledge-based generation
- Invalid API keys produce clear error messages
- Parse errors are caught and logged

## Future Improvements

- Caching for repeated topics
- Multiple language support
- Custom section templates
- Integration with publishing platforms
- Enhanced image placement algorithms
- Support for video content recommendations

## License

This project is provided as-is for educational and professional use.

## Support

For issues or questions:
1. Check the error details displayed in the Generation Details tab
2. Verify API keys are correctly set in .env
3. Ensure internet connection for research and image generation
4. Check that all dependencies are installed correctly


## Repository

GitHub: https://github.com/saur-v/AI-Agent-Blogger
