# LangChain Documentation RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot that scrapes LangChain documentation using crawl4AI and stores embeddings in Pinecone for intelligent question answering.

## Features

- 🤖 **RAG-based Chatbot**: Uses LangChain and OpenAI for intelligent responses
- 🕷️ **Web Scraping**: Uses crawl4AI to scrape LangChain documentation
- 🗄️ **Vector Storage**: Pinecone for scalable vector storage and similarity search
- 🌐 **Web Interface**: Streamlit app for easy interaction
- 📱 **CLI Interface**: Terminal-based chat interface
- 🔍 **Source Attribution**: Shows source documents for each answer

## Prerequisites

- Python 3.8+
- OpenAI API key
- Pinecone API key and environment
- crawl4AI API key (if required)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd LangChainDocChatbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env_example.txt .env
   ```
   
   Edit `.env` file with your API keys:
   ```env
   # OpenAI API Key
   OPENAI_API_KEY=your_openai_api_key_here
   
   # Pinecone Configuration
   PINECONE_API_KEY=your_pinecone_api_key_here
   PINECONE_ENVIRONMENT=your_pinecone_environment_here
   PINECONE_INDEX_NAME=langchain-docs
   
   # Crawl4AI API Key (if required)
   CRAWL4AI_API_KEY=your_crawl4ai_api_key_here
   
   # LangChain Documentation URL
   LANGCHAIN_DOCS_URL=https://python.langchain.com/docs/
   ```

## Setup Instructions

### 1. Setup Pinecone
```bash
python setup_pinecone.py
```
This will verify your Pinecone configuration and optionally create the index.

### 2. Scrape LangChain Documentation
```bash
python scraper.py
```
This will:
- Scrape LangChain documentation using crawl4AI
- Extract structured data (title, content, code examples, etc.)
- Save results to `langchain_docs.json`

### 3. Create Vector Store
```bash
python vector_store.py
```
This will:
- Load scraped documents
- Split them into chunks
- Generate embeddings using OpenAI
- Store vectors in Pinecone

### 4. Test the Chatbot
```bash
python rag_chatbot.py
```
This starts an interactive CLI chat interface.

### 5. Launch Web Interface
```bash
streamlit run streamlit_app.py
```
This opens a modern web interface in your browser.

## Usage

### CLI Interface
```bash
python rag_chatbot.py
```
- Type your questions about LangChain
- Type `quit` to exit
- Type `info` to see vector store information

### Web Interface
```bash
streamlit run streamlit_app.py
```
- Modern, responsive web interface
- Quick action buttons for common questions
- Source attribution for answers
- Real-time chat experience

## Project Structure

```
LangChainDocChatbot/
├── scraper.py              # Web scraping with crawl4AI
├── vector_store.py         # Pinecone vector store management
├── rag_chatbot.py          # RAG chatbot implementation
├── streamlit_app.py        # Web interface
├── setup_pinecone.py       # Pinecone setup utility
├── requirements.txt        # Python dependencies
├── env_example.txt         # Environment variables template
└── README.md              # This file
```

## Configuration

### Pinecone Setup
1. Sign up at [Pinecone](https://www.pinecone.io/)
2. Get your API key and environment
3. Add them to your `.env` file
4. Run `python setup_pinecone.py`

### OpenAI Setup
1. Get an API key from [OpenAI](https://platform.openai.com/)
2. Add it to your `.env` file

### crawl4AI Setup
1. Get an API key from [crawl4AI](https://crawl4ai.com/) (if required)
2. Add it to your `.env` file

## Customization

### Modify Scraping
Edit `scraper.py` to:
- Change the target URL
- Modify extraction strategy
- Adjust chunking parameters

### Modify Vector Store
Edit `vector_store.py` to:
- Change embedding model
- Adjust chunk size and overlap
- Modify metadata structure

### Modify Chatbot
Edit `rag_chatbot.py` to:
- Change LLM model
- Modify prompt template
- Adjust retrieval parameters

## Troubleshooting

### Common Issues

1. **Pinecone API Error**
   - Verify your API key and environment
   - Check if the index exists
   - Ensure you have sufficient quota

2. **OpenAI API Error**
   - Verify your API key
   - Check your billing status
   - Ensure you have sufficient credits

3. **Scraping Issues**
   - Check if crawl4AI API key is required
   - Verify the target URL is accessible
   - Check network connectivity

4. **Vector Store Issues**
   - Ensure Pinecone index exists
   - Check embedding model compatibility
   - Verify document format

### Getting Help

1. Check the console output for error messages
2. Verify all environment variables are set
3. Ensure all dependencies are installed
4. Check API quotas and billing status

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [LangChain](https://langchain.com/) for the documentation
- [crawl4AI](https://crawl4ai.com/) for web scraping capabilities
- [Pinecone](https://www.pinecone.io/) for vector storage
- [OpenAI](https://openai.com/) for language models
- [Streamlit](https://streamlit.io/) for the web interface 