from neo4j import GraphDatabase
from knowledge_base import ThinkScriptKnowledgeBase
import os
from dotenv import load_dotenv
import json

# Get the absolute path to the .env file and project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))  # Go up 3 levels from src to project root
env_file = os.path.join(project_root, '.env')

print(f"Loading environment from: {env_file}")
load_dotenv(env_file)

def create_nodes_from_crawl(crawl_file):
    """Create nodes from crawl data"""
    # Convert relative path to absolute path
    if not os.path.isabs(crawl_file):
        crawl_file = os.path.join(project_root, crawl_file)
    
    print(f"Creating nodes from crawl file: {crawl_file}")
    
    if not os.path.exists(crawl_file):
        raise FileNotFoundError(f"Crawl file not found: {crawl_file}")
    
    with open(crawl_file, 'r') as f:
        crawl_data = json.load(f)
    
    kb = ThinkScriptKnowledgeBase()
    
    with kb.driver.session() as session:
        # Clear existing nodes
        session.run("MATCH (n:Node) DETACH DELETE n")
        
        # Create new nodes from crawl data
        for item in crawl_data:
            session.run("""
                CREATE (n:Node {
                    title: $title,
                    content: $content,
                    url: $url
                })
            """, {
                'title': item.get('title', ''),
                'content': item.get('content', ''),
                'url': item.get('url', '')
            })
        
        print(f"Created {len(crawl_data)} nodes from crawl data")

def process_content(crawl_file=None):
    """Process content into chunks"""
    kb = ThinkScriptKnowledgeBase()
    
    with kb.driver.session() as session:
        # Get all existing nodes
        result = session.run("""
            MATCH (n:Node)
            RETURN n.title as title, n.content as content
        """)
        
        nodes = list(result)
        if not nodes:
            print("No nodes found to process. Please run with a crawl file first.")
            return
        
        for record in nodes:
            title = record['title']
            content = record['content']
            
            # Split content into chunks
            chunks = kb.split_content(content)
            
            # Create content chunks and relationships
            for i, chunk in enumerate(chunks):
                session.run("""
                    MATCH (parent:Node {title: $title})
                    CREATE (chunk:ContentChunk {
                        content: $chunk,
                        chunk_index: $index
                    })
                    CREATE (parent)-[:HAS_CHUNK]->(chunk)
                """, {
                    'title': title,
                    'chunk': chunk,
                    'index': i
                })
            
            print(f"Processed {title} into {len(chunks)} chunks")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        crawl_file = sys.argv[1]
        create_nodes_from_crawl(crawl_file)
    process_content() 