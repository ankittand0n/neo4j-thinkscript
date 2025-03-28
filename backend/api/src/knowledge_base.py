import os
from openai import OpenAI
from neo4j import GraphDatabase
from dotenv import load_dotenv
import json
import re

# Load environment variables from the specified .env file
env_file = os.getenv("ENV_FILE", ".env")
print(f"Loading environment from: {env_file}")
load_dotenv(env_file)

# Debug: Print environment variables
print(f"NEO4J_URI: {os.getenv('NEO4J_URI')}")
print(f"NEO4J_USER: {os.getenv('NEO4J_USER')}")
print(f"OPENAI_API_KEY: {'set' if os.getenv('OPENAI_API_KEY') else 'not set'}")

class ThinkScriptKnowledgeBase:
    def __init__(self):
        neo4j_uri = os.getenv("NEO4J_URI", "neo4j://localhost:7687")
        neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
        
        print(f"Connecting to Neo4j at: {neo4j_uri}")
        self.driver = GraphDatabase.driver(
            neo4j_uri,
            auth=(neo4j_user, neo4j_password)
        )
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set. Please check your .env file.")
        
        # Initialize OpenAI client with minimal configuration
        self.client = OpenAI(api_key=api_key)
        self.setup_indexes()

    def close(self):
        self.driver.close()

    def setup_indexes(self):
        """Set up Neo4j indexes for better search performance"""
        with self.driver.session() as session:
            # Create indexes for content chunks
            session.run("""
                CREATE INDEX content_chunk_index IF NOT EXISTS
                FOR (n:ContentChunk) ON (n.content)
            """)
            # Create fulltext index for better text search
            session.run("""
                CREATE FULLTEXT INDEX content_fulltext_index IF NOT EXISTS
                FOR (n:ContentChunk) ON EACH [n.content]
            """)

    def split_content(self, content: str, chunk_size: int = 100) -> list:
        """Split content into chunks of approximately chunk_size words"""
        # Split content into sentences
        sentences = re.split(r'(?<=[.!?])\s+', content)
        chunks = []
        current_chunk = []
        current_size = 0

        for sentence in sentences:
            sentence_words = len(sentence.split())
            if current_size + sentence_words > chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_size = 0
            current_chunk.append(sentence)
            current_size += sentence_words

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks

    def find_relevant_nodes(self, query: str) -> list:
        print(f"\nSearching for: {query}")
        
        with self.driver.session() as session:
            # Extract key technical terms from the query
            technical_terms = {
                'moving average': ['sma', 'moving average', 'ma'],
                'crossover': ['cross', 'crossover', 'crosses'],
                'strategy': ['strategy', 'strategies', 'trading'],
                'indicator': ['indicator', 'study', 'plot'],
                'signal': ['signal', 'buy', 'sell', 'order']
            }
            
            # Build search conditions based on technical terms
            search_terms = []
            query_lower = query.lower()
            for category, terms in technical_terms.items():
                if any(term in query_lower for term in terms):
                    search_terms.extend(terms)
            
            if not search_terms:
                search_terms = query_lower.split()
            
            # Create Cypher conditions for content search using fulltext index
            search_conditions = []
            for term in search_terms:
                search_conditions.append(f"n.content CONTAINS toLower('{term}')")
            
            where_clause = " OR ".join(search_conditions)
            
            # Search with combined conditions using fulltext index
            print("Searching with technical terms...")
            result = session.run(f"""
                MATCH (n:ContentChunk)
                WHERE {where_clause}
                WITH n
                MATCH (n)<-[:HAS_CHUNK]-(parent:Node)
                RETURN DISTINCT parent.title as name, collect(n.content) as chunks
                LIMIT 5
            """)
            
            nodes = []
            for record in result:
                # Combine chunks into full content
                full_content = " ".join(record['chunks'])
                nodes.append({
                    'name': record['name'],
                    'content': full_content
                })
            
            print(f"Found {len(nodes)} matches")
            return nodes

    def generate_response(self, query: str, relevant_nodes: list) -> str:
        try:
            if not relevant_nodes:
                return "I apologize, but I couldn't find any relevant information about ThinkScript in my knowledge base. Could you please try rephrasing your question or ask about a different aspect of ThinkScript?"

            # Create context from relevant nodes
            context = "\n\n".join([
                f"Title: {node['name']}\nContent: {node['content']}"
                for node in relevant_nodes
            ])

            # Generate response using OpenAI with timeout
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a helpful assistant that answers questions about ThinkScript programming language.
                                    Your responses should be:
                                    1. Clear and concise
                                    2. Include code examples when relevant
                                    3. Explain the key concepts
                                    4. Provide step-by-step instructions when needed
                                    5. Include any important warnings or considerations
                                    
                                    If you find multiple relevant pieces of information, combine them to provide a comprehensive answer.
                                    If you're not sure about something, say so rather than making assumptions.
                                    Always format code examples with proper indentation and comments."""
                    },
                    {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
                ],
                temperature=0.7,
                max_tokens=1000,
                timeout=30  # 30 second timeout
            )

            # Ensure we have a valid response
            if not response or not response.choices:
                return "I apologize, but I encountered an error while generating a response. Please try again."

            # Get the response content
            response_content = response.choices[0].message.content
            
            # Ensure the response is a string
            if not isinstance(response_content, str):
                return "I apologize, but I encountered an error while generating a response. Please try again."

            return response_content

        except Exception as e:
            print(f"Error generating response: {str(e)}")
            # Try to provide a more helpful error message
            if "timeout" in str(e).lower():
                return "I apologize, but the response is taking longer than expected. Please try your question again, or try breaking it down into smaller parts."
            return "I apologize, but I encountered an error while generating a response. Please try again." 