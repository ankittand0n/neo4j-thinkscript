#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if Neo4j is ready
check_neo4j() {
    # for i in {1..30}; do
    #     if curl -s -f http://localhost:7474/db/neo4j/tx/commit -X POST -H "Content-Type: application/json" -d '{"statements": [{"statement": "RETURN 1"}]}' > /dev/null; then
    #         echo -e "${GREEN}Neo4j is ready!${NC}"
    #         return 0
    #     fi
    #     echo "Waiting for Neo4j... ($i/30)"
        sleep 2
    # done
    # echo -e "${RED}Neo4j failed to start within 60 seconds${NC}"
    return 1
}

# Function to check if .env file exists and create if needed
check_env() {
    if [ ! -f .env ]; then
        echo -e "${RED}Error: .env file not found!${NC}"
        echo "Creating default .env file..."
        cat > .env << EOL
# Neo4j Configuration
NEO4J_URI=neo4j://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
NEO4J_PAGECACHE_SIZE=512M
NEO4J_HEAP_INITIAL_SIZE=512M
NEO4J_HEAP_MAX_SIZE=1G

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Frontend Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
EOL
        echo -e "${YELLOW}Please update the .env file with your OpenAI API key${NC}"
        exit 1
    fi
}

# Function to create data directories
setup_data_dirs() {
    echo -e "${GREEN}Setting up data directories...${NC}"
    mkdir -p data/crawls data/processed
}

# Function to start Neo4j
start_neo4j() {
    echo -e "${GREEN}Starting Neo4j...${NC}"
    docker-compose up neo4j -d
    check_neo4j
}

# Function to stop Neo4j
stop_neo4j() {
    echo -e "${YELLOW}Stopping Neo4j...${NC}"
    docker-compose down
}

# Function to show logs
show_logs() {
    docker-compose logs -f
}

# Function to reset data
reset_data() {
    echo -e "${RED}Warning: This will delete all data in Neo4j${NC}"
    read -p "Are you sure? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        stop_neo4j
        docker volume rm $(docker volume ls -q | grep neo4j)
        start_neo4j
        echo -e "${GREEN}All Neo4j data has been reset${NC}"
    fi
}

# Function to run crawler
run_crawler() {
    echo -e "${GREEN}Starting ThinkScript crawler...${NC}"
    setup_data_dirs
    cd backend/crawler
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip3 install -r requirements.txt
    scrapy crawl thinkscript
    deactivate
    cd ../..
}

# Function to list crawl files
list_crawls() {
    echo -e "${GREEN}Available crawl files:${NC}"
    ls -l data/crawls/thinkscript_data_*.json 2>/dev/null || echo "No crawl files found"
}

# Function to get project root directory
get_project_root() {
    echo "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
}

# Function to process specific crawl file
process_crawl() {
    if [ -z "$1" ]; then
        echo -e "${RED}Please specify a crawl file to process${NC}"
        list_crawls
        return
    fi

    crawl_file="data/crawls/$1"
    if [ ! -f "$crawl_file" ]; then
        echo -e "${RED}Crawl file not found: $crawl_file${NC}"
        list_crawls
        return
    fi

    echo -e "${GREEN}Processing crawl file: $crawl_file${NC}"
    cd backend/api
    source venv/bin/activate
    PYTHONPATH=$PYTHONPATH:$(pwd)/src ENV_FILE="$(get_project_root)/.env" python3 src/process_content.py "$crawl_file"
    deactivate
    cd ../..
}

# Function to setup schema
setup_schema() {
    echo -e "${GREEN}Setting up Neo4j schema...${NC}"
    cd backend/api
    source venv/bin/activate
    PYTHONPATH=$PYTHONPATH:$(pwd)/src ENV_FILE="$(get_project_root)/.env" python3 src/knowledge_base.py
    deactivate
    cd ../..
}

# Function to process data
process_data() {
    echo -e "${GREEN}Processing data and creating Neo4j nodes...${NC}"
    cd backend/api
    source venv/bin/activate
    PYTHONPATH=$PYTHONPATH:$(pwd)/src ENV_FILE="$(get_project_root)/.env" python3 src/process_content.py
    deactivate
    cd ../..
}

# Function to kill processes using specific ports
kill_port_processes() {
    echo -e "${YELLOW}Checking for processes using ports 3000 and 8000...${NC}"
    
    # Kill process using port 3000 (frontend)
    if lsof -i :3000 > /dev/null; then
        echo -e "${YELLOW}Killing process using port 3000...${NC}"
        lsof -ti :3000 | xargs kill -9 2>/dev/null
    fi
    
    # Kill process using port 8000 (backend)
    if lsof -i :8000 > /dev/null; then
        echo -e "${YELLOW}Killing process using port 8000...${NC}"
        lsof -ti :8000 | xargs kill -9 2>/dev/null
    fi
}

# Function to start backend API only
start_backend() {
    echo -e "${GREEN}Starting Backend API...${NC}"
    
    # Kill any existing process using port 8000
    if lsof -i :8000 > /dev/null; then
        echo -e "${YELLOW}Port 8000 is in use. Killing existing process...${NC}"
        lsof -ti :8000 | xargs kill -9 2>/dev/null
        sleep 2
    fi
    
    cd backend/api
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}Creating virtual environment...${NC}"
        python3 -m venv venv
    fi
    source venv/bin/activate
    
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip3 install --upgrade httpx openai
    pip3 install -r requirements.txt
    
    echo -e "${YELLOW}Starting FastAPI server...${NC}"
    PYTHONPATH=$PYTHONPATH:$(pwd)/src ENV_FILE="$(get_project_root)/.env" uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload &
    
    # Wait for the server to start
    # for i in {1..30}; do
    #     if curl -s http://localhost:8000/api/health > /dev/null; then
    #         echo -e "${GREEN}Backend API is running!${NC}"
    #         break
    #     fi
    #     echo "Waiting for backend to start... ($i/30)"
    #     sleep 1
    # done
    
    cd ../..
}

# Function to start frontend only
start_frontend() {
    echo -e "${GREEN}Starting Frontend...${NC}"
    
    # Kill any existing process using port 3000
    if lsof -i :3000 > /dev/null; then
        echo -e "${YELLOW}Port 3000 is in use. Killing existing process...${NC}"
        lsof -ti :3000 | xargs kill -9 2>/dev/null
        sleep 2
    fi
    
    cd frontend
    if [ ! -d "node_modules" ]; then
        npm install
    fi
    npm run dev &
    cd ..
}

# Function to start all services
start_services() {
    echo -e "${GREEN}Starting services...${NC}"
    
    # Start Neo4j
    start_neo4j
    
    # Setup schema and load data
    setup_schema
    process_crawl "thinkscript_data_20250328_132839.json"
    
    # Start Backend API
    start_backend
    
    # Start Frontend
    start_frontend
}

# Function to stop all services
stop_services() {
    echo -e "${YELLOW}Stopping services...${NC}"
    stop_neo4j
    kill_port_processes
}

# Show help menu
show_help() {
    echo "Usage: ./run.sh [command]"
    echo "Commands:"
    echo "  start     - Start all services"
    echo "  stop      - Stop all services"
    echo "  restart   - Restart all services"
    echo "  backend   - Start only the backend API"
    echo "  frontend  - Start only the frontend"
    echo "  logs      - Show service logs"
    echo "  reset     - Reset all Neo4j data"
    echo "  crawl     - Run the ThinkScript crawler"
    echo "  crawls    - List available crawl files"
    echo "  process   - Process data and create Neo4j nodes"
    echo "  process-crawl [file] - Process specific crawl file"
    echo "  schema    - Set up Neo4j schema"
    echo "  help      - Show this help message"
}

# Check for .env file
check_env

# Main script
case "$1" in
    "start")
        start_services
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        stop_services
        start_services
        ;;
    "backend")
        start_backend
        ;;
    "frontend")
        start_frontend
        ;;
    "logs")
        show_logs
        ;;
    "reset")
        reset_data
        ;;
    "crawl")
        run_crawler
        ;;
    "crawls")
        list_crawls
        ;;
    "process-crawl")
        process_crawl "$2"
        ;;
    "schema")
        setup_schema
        ;;
    "process")
        process_data
        ;;
    "help")
        show_help
        ;;
    *)
        echo -e "${YELLOW}No command specified, showing help...${NC}"
        show_help
        ;;
esac