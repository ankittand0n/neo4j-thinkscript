#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if Neo4j is ready
check_neo4j() {
    for i in {1..30}; do
        if curl -s -f http://localhost:7474 > /dev/null; then
            echo -e "${GREEN}Neo4j is ready!${NC}"
            return 0
        fi
        echo "Waiting for Neo4j... ($i/30)"
        sleep 2
    done
    echo -e "${RED}Neo4j failed to start within 60 seconds${NC}"
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

# Function to start services with Docker
start_docker() {
    echo -e "${GREEN}Starting services with Docker...${NC}"
    docker-compose up -d
    check_neo4j
}

# Function to stop services with Docker
stop_docker() {
    echo -e "${YELLOW}Stopping Docker services...${NC}"
    docker-compose down
}

# Function to start services without Docker
start_local() {
    echo -e "${GREEN}Starting services locally...${NC}"
    
    # Start Neo4j
    if ! command -v neo4j &> /dev/null; then
        echo -e "${RED}Neo4j is not installed. Please install Neo4j first.${NC}"
        exit 1
    fi
    neo4j start
    check_neo4j

    # Start Backend API
    echo -e "${GREEN}Starting Backend API...${NC}"
    cd backend/api
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install -r requirements.txt
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
    cd ../..

    # Start Frontend
    echo -e "${GREEN}Starting Frontend...${NC}"
    cd frontend
    if [ ! -d "node_modules" ]; then
        npm install
    fi
    npm run dev &
    cd ..
}

# Function to stop services without Docker
stop_local() {
    echo -e "${YELLOW}Stopping local services...${NC}"
    neo4j stop
    pkill -f "uvicorn main:app"
    pkill -f "npm run dev"
}

# Function to show logs
show_logs() {
    if [ "$1" = "docker" ]; then
        docker-compose logs -f
    else
        neo4j logs
    fi
}

# Function to reset data
reset_data() {
    echo -e "${RED}Warning: This will delete all data in Neo4j${NC}"
    read -p "Are you sure? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ "$1" = "docker" ]; then
            stop_docker
            docker volume rm $(docker volume ls -q | grep neo4j)
            start_docker
        else
            neo4j stop
            rm -rf /var/lib/neo4j/data/*
            neo4j start
            check_neo4j
        fi
        echo -e "${GREEN}All Neo4j data has been reset${NC}"
    fi
}

# Function to run crawler
run_crawler() {
    echo -e "${GREEN}Starting ThinkScript crawler...${NC}"
    setup_data_dirs
    if [ "$1" = "docker" ]; then
        docker-compose exec crawler scrapy crawl thinkscript
    else
        cd backend/crawler
        if [ ! -d "venv" ]; then
            python3 -m venv venv
        fi
        source venv/bin/activate
        pip install -r requirements.txt
        scrapy crawl thinkscript
        deactivate
        cd ../..
    fi
}

# Function to list crawl files
list_crawls() {
    echo -e "${GREEN}Available crawl files:${NC}"
    ls -l data/crawls/thinkscript_data_*.json 2>/dev/null || echo "No crawl files found"
}

# Function to process specific crawl file
process_crawl() {
    if [ -z "$2" ]; then
        echo -e "${RED}Please specify a crawl file to process${NC}"
        list_crawls
        return
    fi

    crawl_file="data/crawls/$2"
    if [ ! -f "$crawl_file" ]; then
        echo -e "${RED}Crawl file not found: $crawl_file${NC}"
        list_crawls
        return
    fi

    echo -e "${GREEN}Processing crawl file: $crawl_file${NC}"
    if [ "$1" = "docker" ]; then
        docker-compose exec api python process_data.py "$crawl_file"
    else
        cd backend/api
        source venv/bin/activate
        python process_data.py "$crawl_file"
        deactivate
        cd ../..
    fi
}

# Function to setup schema
setup_schema() {
    echo -e "${GREEN}Setting up Neo4j schema...${NC}"
    if [ "$1" = "docker" ]; then
        docker-compose exec api python schema_setup.py
    else
        cd backend/api
        source venv/bin/activate
        python schema_setup.py
        deactivate
        cd ../..
    fi
}

# Function to process data
process_data() {
    echo -e "${GREEN}Processing data and creating Neo4j nodes...${NC}"
    if [ "$1" = "docker" ]; then
        docker-compose exec api python process_data.py
    else
        cd backend/api
        source venv/bin/activate
        python process_data.py
        deactivate
        cd ../..
    fi
}

# Function to run full setup
run_full_setup() {
    if [ "$1" = "docker" ]; then
        start_docker
        setup_schema "docker"
        run_crawler "docker"
        process_data "docker"
    else
        start_local
        setup_schema "local"
        run_crawler "local"
        process_data "local"
    fi
}

# Show help menu
show_help() {
    echo "Usage: ./run.sh [mode] [command]"
    echo "Modes:"
    echo "  docker    - Run with Docker (default)"
    echo "  local     - Run without Docker"
    echo "Commands:"
    echo "  start     - Start all services"
    echo "  stop      - Stop all services"
    echo "  restart   - Restart all services"
    echo "  logs      - Show service logs"
    echo "  reset     - Reset all Neo4j data"
    echo "  crawl     - Run the ThinkScript crawler"
    echo "  crawls    - List available crawl files"
    echo "  process   - Process data and create Neo4j nodes"
    echo "  process-crawl [file] - Process specific crawl file"
    echo "  schema    - Set up Neo4j schema"
    echo "  setup     - Run full setup (start services, schema, crawler, process)"
    echo "  help      - Show this help message"
}

# Check for .env file
check_env

# Determine mode and command
MODE="docker"
COMMAND="help"

if [ "$1" = "local" ]; then
    MODE="local"
    COMMAND="$2"
elif [ "$1" = "docker" ]; then
    COMMAND="$2"
else
    COMMAND="$1"
fi

# Main script
case "$COMMAND" in
    "start")
        if [ "$MODE" = "docker" ]; then
            start_docker
        else
            start_local
        fi
        ;;
    "stop")
        if [ "$MODE" = "docker" ]; then
            stop_docker
        else
            stop_local
        fi
        ;;
    "restart")
        if [ "$MODE" = "docker" ]; then
            stop_docker
            start_docker
        else
            stop_local
            start_local
        fi
        ;;
    "logs")
        show_logs "$MODE"
        ;;
    "reset")
        reset_data "$MODE"
        ;;
    "crawl")
        run_crawler "$MODE"
        ;;
    "crawls")
        list_crawls
        ;;
    "process-crawl")
        process_crawl "$MODE" "$2"
        ;;
    "schema")
        setup_schema "$MODE"
        ;;
    "process")
        process_data "$MODE"
        ;;
    "setup")
        run_full_setup "$MODE"
        ;;
    "help")
        show_help
        ;;
    *)
        echo -e "${YELLOW}No command specified, showing help...${NC}"
        show_help
        ;;
esac