# Neo4j ThinkScript Documentation

This project is a comprehensive system for managing and querying ThinkScript documentation using Neo4j as the backend database. The system consists of a FastAPI backend and a Next.js frontend that provides an interactive chat interface for querying ThinkScript documentation.

## System Architecture

### Backend (FastAPI)

The backend is built using FastAPI and provides the following key components:

1. **Neo4j Database Integration**
   - Uses Neo4j's Python driver for database operations
   - Implements connection pooling for efficient database access
   - Handles database connection errors and retries
   - Uses environment variables for database configuration

2. **Knowledge Base Management**
   - `ThinkScriptKnowledgeBase` class manages all database operations
   - Implements CRUD operations for documentation nodes
   - Handles text chunking and storage
   - Manages relationships between documentation nodes

3. **OpenAI Integration**
   - Uses OpenAI's API for natural language processing
   - Implements streaming responses for real-time chat
   - Handles API rate limiting and error cases
   - Configurable model selection (GPT-3.5 and GPT-4)

4. **API Endpoints**
   - `/api/chat`: Handles chat messages and streaming responses
   - `/api/health`: Provides system health status
   - Implements CORS for frontend access
   - Handles error responses and validation

### Frontend (Next.js)

The frontend is built using Next.js and provides:

1. **Chat Interface**
   - Real-time message streaming
   - Message history management
   - Code block formatting
   - Markdown rendering
   - Local storage for chat persistence

2. **UI Components**
   - Message parser for formatting responses
   - Code editor for syntax highlighting
   - Scrollable chat area
   - Model selection dropdown
   - Clear history functionality

3. **State Management**
   - React state for messages and UI
   - Local storage for persistence
   - Streaming state handling
   - Error state management

## Database Schema

### Neo4j Nodes

1. **Documentation Node**
   ```cypher
   (doc:Documentation {
     name: string,
     content: string,
     chunks: string[],
     url: string
   })
   ```

2. **Chunk Node**
   ```cypher
   (chunk:Chunk {
     content: string,
     index: number
   })
   ```

### Relationships

1. **Documentation to Chunks**
   ```cypher
   (doc:Documentation)-[:HAS_CHUNK]->(chunk:Chunk)
   ```

2. **Chunk to Chunk**
   ```cypher
   (chunk1:Chunk)-[:NEXT]->(chunk2:Chunk)
   ```

## Data Processing Pipeline

### 1. Documentation Crawling

The system crawls ThinkScript documentation using:

1. **URL Collection**
   - Scrapes ThinkScript documentation pages
   - Extracts relevant URLs and content
   - Handles pagination and navigation

2. **Content Extraction**
   - Parses HTML content
   - Extracts text and code blocks
   - Preserves formatting and structure

### 2. Text Chunking

Content is processed into chunks for efficient storage and retrieval:

1. **Chunking Strategy**
   - Splits content into manageable chunks
   - Preserves context and relationships
   - Maintains code block integrity

2. **Chunk Storage**
   - Stores chunks in Neo4j
   - Maintains order and relationships
   - Enables efficient retrieval

### 3. Query Processing

The system processes queries through multiple stages:

1. **Query Understanding**
   - Analyzes user input
   - Identifies key concepts
   - Determines search parameters

2. **Knowledge Retrieval**
   - Searches Neo4j for relevant chunks
   - Uses graph traversal for context
   - Ranks results by relevance

3. **Response Generation**
   - Combines relevant chunks
   - Uses OpenAI for natural language generation
   - Streams response to frontend

## Message Processing

### 1. Message Parsing

The frontend processes messages through multiple stages:

1. **Text Processing**
   - Removes markdown formatting
   - Handles code blocks
   - Processes headings and lists

2. **Formatting**
   - Converts markdown to HTML
   - Handles bullet points and numbered lists
   - Preserves code block formatting

### 2. Message Display

Messages are displayed with proper formatting:

1. **Text Formatting**
   - Handles headings (single #)
   - Processes bullet points (###)
   - Formats numbered lists
   - Removes asterisks and markdown

2. **Code Display**
   - Syntax highlighting
   - Proper indentation
   - Copy functionality

## Environment Setup

### Required Environment Variables

1. **Backend**
   ```
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your_password
   OPENAI_API_KEY=your_openai_key
   ```

2. **Frontend**
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

### Installation

1. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

3. **Database Setup**
   ```bash
   # Start Neo4j database
   docker-compose up -d
   ```

## Running the Application

1. **Start Backend**
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

2. **Start Frontend**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Neo4j Browser: http://localhost:7474

## Error Handling

The system implements comprehensive error handling:

1. **Backend Errors**
   - Database connection errors
   - API rate limiting
   - Invalid queries
   - Network issues

2. **Frontend Errors**
   - Message streaming errors
   - State management errors
   - UI rendering issues
   - Network connectivity

## Performance Considerations

1. **Database Optimization**
   - Connection pooling
   - Indexed queries
   - Efficient graph traversal
   - Caching strategies

2. **Frontend Optimization**
   - Message streaming
   - Efficient state updates
   - Lazy loading
   - Memory management

## Security Considerations

1. **API Security**
   - CORS configuration
   - Rate limiting
   - Input validation
   - Error handling

2. **Data Security**
   - Secure database access
   - API key management
   - Environment variables
   - Input sanitization

## Future Improvements

1. **Planned Features**
   - Enhanced search capabilities
   - User authentication
   - Chat history management
   - Advanced code analysis

2. **Technical Improvements**
   - Performance optimization
   - Enhanced error handling
   - Better documentation
   - Testing coverage

## Contributing

1. **Development Guidelines**
   - Code style
   - Testing requirements
   - Documentation standards
   - Pull request process

2. **Setup for Development**
   - Local environment
   - Testing environment
   - Documentation tools
   - Code quality tools
