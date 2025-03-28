from neo4j import GraphDatabase
from knowledge_base import ThinkScriptKnowledgeBase
import os
from dotenv import load_dotenv

load_dotenv()

def process_content():
    kb = ThinkScriptKnowledgeBase()
    
    with kb.driver.session() as session:
        # Get all existing nodes
        result = session.run("""
            MATCH (n:Node)
            RETURN n.title as title, n.content as content
        """)
        
        for record in result:
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
    process_content() 