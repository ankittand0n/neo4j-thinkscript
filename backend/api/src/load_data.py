import json
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

class DataLoader:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI", "neo4j://localhost:7687"),
            auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "password"))
        )

    def close(self):
        self.driver.close()

    def clear_data(self):
        with self.driver.session() as session:
            # Drop all existing indexes
            session.run("SHOW INDEXES").data()
            session.run("DROP INDEX node_title IF EXISTS")
            session.run("DROP INDEX node_content IF EXISTS")
            # Clear all data
            session.run("MATCH (n) DETACH DELETE n")

    def create_indexes(self):
        with self.driver.session() as session:
            # Only create index on title for searching
            session.run("CREATE INDEX node_title IF NOT EXISTS FOR (n:Node) ON (n.title)")

    def load_data(self, file_path: str):
        with open(file_path, 'r') as f:
            data = json.load(f)

        print(f"Found {len(data)} items in JSON file")
        
        with self.driver.session() as session:
            for item in data:
                title = item.get('title', '')
                content = item.get('content', '')

                # Create node with content as a non-indexed property
                session.run("""
                    CREATE (n:Node {
                        title: $title,
                        content: $content
                    })
                """, {
                    "title": title,
                    "content": content
                })

        # Print statistics after loading
        with self.driver.session() as session:
            result = session.run("MATCH (n:Node) RETURN count(n) as count").single()
            print(f"Loaded {result['count']} nodes into Neo4j")
            
            # Print some sample titles
            result = session.run("MATCH (n:Node) RETURN n.title as title LIMIT 5").data()
            print("\nSample titles loaded:")
            for record in result:
                print(f"- {record['title']}")

    def determine_type(self, url: str) -> str:
        if "function" in url.lower():
            return "Function"
        elif "constant" in url.lower():
            return "Constant"
        elif "operator" in url.lower():
            return "Operator"
        elif "pattern" in url.lower():
            return "Pattern"
        else:
            return "Documentation"

def main():
    loader = DataLoader()
    try:
        print("Clearing existing data and indexes...")
        loader.clear_data()
        
        print("Creating indexes...")
        loader.create_indexes()
        
        print("Loading data...")
        data_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                "src", "crawler", "thinkscript_crawler", "output", "thinkscript_data.json")
        loader.load_data(data_file)
        
        print("\nData loading completed successfully!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        loader.close()

if __name__ == "__main__":
    main() 