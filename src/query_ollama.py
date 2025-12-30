import ollama
from typing import Optional, Dict, Any
from query_wikipedia import create_opensearch_client, search_wikipedia_articles


def query_gemma3_model(prompt: str, model: str = "gemma3", host: str = "http://localhost:11434") -> Optional[str]:
    """
    Query the Gemma3 model using Ollama and return the response.
    
    Args:
        prompt (str): The input prompt to send to the model
        model (str): The model name to use (default: "gemma3")
        host (str): The Ollama server host (default: "http://localhost:11434")
    
    Returns:
        Optional[str]: The model's response or None if an error occurred
    """
    try:
        # Initialize the Ollama client
        client = ollama.Client(host=host)
        
        # Send the prompt to the model
        response = client.chat(
            model=model,
            messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        )
        
        # Extract and return the response content
        if response and 'message' in response and 'content' in response['message']:
            return response['message']['content']
        else:
            print("Unexpected response format from Ollama")
            return None
            
    except Exception as e:
        print(f"Error querying Ollama: {e}")
        return None


def query_gemma3_model_with_rag(prompt: str, model: str = "gemma3", host: str = "http://localhost:11434", opensearch_host: str = "localhost", opensearch_port: int = 9200) -> Optional[str]:
    """
    Query the Gemma3 model using Ollama with RAG (Retrieval-Augmented Generation).
    Retrieves relevant Wikipedia articles and includes them as context.
    
    Args:
        prompt (str): The input prompt to send to the model
        model (str): The model name to use (default: "gemma3")
        host (str): The Ollama server host (default: "http://localhost:11434")
        opensearch_host (str): OpenSearch host for article retrieval
        opensearch_port (int): OpenSearch port for article retrieval
    
    Returns:
        Optional[str]: The model's response or None if an error occurred
    """
    try:
        # Create OpenSearch client for article retrieval
        opensearch_client = create_opensearch_client(host=opensearch_host, port=opensearch_port)
        
        # Test OpenSearch connection
        if not opensearch_client.ping():
            print("Warning: Could not connect to OpenSearch. Falling back to non-RAG query.")
            return query_gemma3_model(prompt, model, host)
        
        # Retrieve relevant Wikipedia articles
        search_results = search_wikipedia_articles(opensearch_client, query_text=prompt, k=10, size=10)
        
        # Extract article passages for context
        context_passages = []
        if 'hits' in search_results and 'hits' in search_results['hits']:
            for hit in search_results['hits']['hits']:
                if '_source' in hit and 'passage' in hit['_source']:
                    passage = hit['_source']['passage']
                    # Limit passage length to avoid overly long context
                    if len(passage) > 300:
                        passage = passage[:300] + "..."
                    context_passages.append(passage)
        
        # Build RAG prompt with context
        if context_passages:
            context_text = "\n\n".join([f"Context {i+1}: {passage}" for i, passage in enumerate(context_passages)])
            rag_prompt = f"""
            QUESTION:
            {prompt}

            CONTEXT:
            {context_text}

            Using the CONTEXT provided, answer the QUESTION. Keep your answer grounded in the facts of the CONTEXT. If the CONTEXT doesn't contain the answer to the QUESTION, say you don't know.
            Answer in a single word or a short sentence. Do not ask follow-up questions or make suggestions.
            """
        else:
            # Fallback to non-RAG if no context found
            rag_prompt = f"""
            {prompt}

            Answer in a single word or a short sentence. Do not ask follow-up questions or make suggestions.
        """
        
        # Initialize the Ollama client
        client = ollama.Client(host=host)
        
        # Send the RAG prompt to the model
        response = client.chat(
            model=model,
            messages=[
                {
                    'role': 'user',
                    'content': rag_prompt
                }
            ]
        )
        
        # Extract and return the response content
        if response and 'message' in response and 'content' in response['message']:
            return response['message']['content']
        else:
            print("Unexpected response format from Ollama")
            return None
            
    except Exception as e:
        print(f"Error in RAG query: {e}")
        # Fallback to non-RAG query on error
        return query_gemma3_model(prompt, model, host)


def test_ollama_connection():
    """
    Temporary testing function that sends a static query to the Gemma3 model.
    """
    print("Testing Ollama connection with Gemma3 model...")
    print("-" * 50)
    
    # Static test query
    test_prompt = "Hello! Can you tell me a brief interesting fact about artificial intelligence?"
    
    print(f"Sending prompt: {test_prompt}")
    print("\nWaiting for response...")
    
    # Query the model
    response = query_gemma3_model(test_prompt)
    
    if response:
        print("\n✅ Success! Model response:")
        print("-" * 30)
        print(response)
        print("-" * 30)
    else:
        print("\n❌ Failed to get response from the model")
        print("Make sure Ollama is running and the gemma3 model is available")


def test_rag_connection():
    """
    Test function for RAG-enabled Gemma3 model.
    """
    print("Testing RAG-enabled Ollama connection with Gemma3 model...")
    print("-" * 60)
    
    # Static test query
    test_prompt = "What did Abraham Lincoln accomplish as president?"
    
    print(f"Sending RAG prompt: {test_prompt}")
    print("\nRetrieving context and waiting for response...")
    
    # Query the model with RAG
    response = query_gemma3_model_with_rag(test_prompt)
    
    if response:
        print("\n✅ Success! RAG Model response:")
        print("-" * 30)
        print(response)
        print("-" * 30)
    else:
        print("\n❌ Failed to get response from the RAG model")
        print("Make sure Ollama and OpenSearch are running")


if __name__ == "__main__":
    # Test both regular and RAG connections
    test_ollama_connection()
    print("\n" + "="*60 + "\n")
    test_rag_connection()
