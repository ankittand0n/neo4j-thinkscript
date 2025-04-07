import os
from openai import OpenAI
from anthropic import Anthropic
from neo4j import GraphDatabase
from dotenv import load_dotenv
import json
import re
from typing import List, Dict, Any, Optional
import time
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from the specified .env file
env_file = os.getenv("ENV_FILE", ".env")
print(f"Loading environment from: {env_file}")
load_dotenv(env_file)

# Debug: Print environment variables
print(f"NEO4J_URI: {os.getenv('NEO4J_URI')}")
print(f"NEO4J_USER: {os.getenv('NEO4J_USER')}")
print(f"OPENAI_API_KEY: {'set' if os.getenv('OPENAI_API_KEY') else 'not set'}")
print(f"ANTHROPIC_API_KEY: {'set' if os.getenv('ANTHROPIC_API_KEY') else 'not set'}")

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
        
        # Initialize OpenAI client
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            self.openai_client = OpenAI(api_key=openai_api_key)
        else:
            self.openai_client = None
            
        # Initialize Anthropic client
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_api_key:
            self.anthropic_client = Anthropic(api_key=anthropic_api_key)
        else:
            self.anthropic_client = None
            
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
            # First try exact title match
            result = session.run("""
                MATCH (n:Node)
                WHERE n.title = $query
                RETURN n.title as name, n.content as content
                LIMIT 1
            """, {"query": query})
            
            exact_match = list(result)
            if exact_match:
                print("Found exact title match")
                return [{
                    'name': record['name'],
                    'content': record['content']
                } for record in exact_match]
            
            # If no exact match, try fulltext search on both Node and ContentChunk
            result = session.run("""
                CALL db.index.fulltext.queryNodes("content_fulltext_index", $query)
                YIELD node, score
                WITH node, score
                MATCH (node)
                WHERE node:Node OR node:ContentChunk
                WITH node, score
                ORDER BY score DESC
                LIMIT 5
                RETURN 
                    CASE 
                        WHEN node:Node THEN node.title
                        ELSE [(node)<-[:HAS_CHUNK]-(parent:Node) | parent.title][0]
                    END as name,
                    CASE 
                        WHEN node:Node THEN node.content
                        ELSE node.content
                    END as content,
                    score
            """, {"query": query})
            
            nodes = []
            for record in result:
                nodes.append({
                    'name': record['name'],
                    'content': record['content']
                })
            
            print(f"Found {len(nodes)} matches")
            return nodes

    def generate_response(
        self,
        messages: List[Dict[str, str]],
        stream: bool = True,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        timeout: Optional[int] = None,
        retries: Optional[int] = None,
        model: str = "gpt-3.5-turbo"
    ) -> Any:
        """
        Generate a response using either OpenAI or Anthropic API with streaming support.
        """
        # Use provided values or defaults
        timeout = timeout or 30  # seconds
        retries = retries or 3
        
        # Determine which API to use based on model
        if model.startswith('claude'):
            if not self.anthropic_client:
                raise ValueError("Anthropic API key not configured")
            return self._generate_claude_response(messages, stream, temperature, max_tokens, model)
        else:
            if not self.openai_client:
                raise ValueError("OpenAI API key not configured")
            return self._generate_openai_response(messages, stream, temperature, max_tokens, model)

    def _generate_openai_response(
        self,
        messages: List[Dict[str, str]],
        stream: bool,
        temperature: float,
        max_tokens: Optional[int],
        model: str
    ) -> Any:
        """Generate response using OpenAI API"""
        params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream
        }
        
        if max_tokens:
            params["max_tokens"] = max_tokens
            
        self.openai_client.timeout = 30
        
        for attempt in range(3):
            try:
                if stream:
                    return self.openai_client.chat.completions.create(**params)
                else:
                    response = self.openai_client.chat.completions.create(**params)
                    return response.choices[0].message.content
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < 2:
                    time.sleep(1)
                else:
                    raise

    def _generate_claude_response(
        self,
        messages: List[Dict[str, str]],
        stream: bool,
        temperature: float,
        max_tokens: Optional[int],
        model: str
    ) -> Any:
        """Generate response using Anthropic API"""
        # Convert messages to Anthropic format
        system_message = next((msg for msg in messages if msg["role"] == "system"), None)
        user_messages = [msg for msg in messages if msg["role"] == "user"]
        assistant_messages = [msg for msg in messages if msg["role"] == "assistant"]
        
        # Combine messages into conversation
        conversation = []
        for user_msg, assistant_msg in zip(user_messages, assistant_messages):
            conversation.append({"role": "user", "content": user_msg["content"]})
            if assistant_msg:
                conversation.append({"role": "assistant", "content": assistant_msg["content"]})
        
        params = {
            "model": model,
            "messages": conversation,
            "temperature": temperature,
            "stream": stream
        }
        
        if max_tokens:
            params["max_tokens"] = max_tokens
            
        if system_message:
            params["system"] = system_message["content"]
            
        for attempt in range(3):
            try:
                if stream:
                    return self.anthropic_client.messages.stream(**params)
                else:
                    response = self.anthropic_client.messages.create(**params)
                    return response.content[0].text
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < 2:
                    time.sleep(1)
                else:
                    raise 