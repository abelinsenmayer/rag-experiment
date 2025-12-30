"""
Query entrypoint for searching Wikipedia articles in OpenSearch using neural search.
"""

import json
import os
from opensearchpy import OpenSearch


def create_opensearch_client(host: str = "localhost", port: int = 9200) -> OpenSearch:
    """
    Create and return an OpenSearch client.
    
    Args:
        host: OpenSearch host address
        port: OpenSearch port number
        
    Returns:
        OpenSearch client instance
    """
    client = OpenSearch(
        hosts=[{'host': host, 'port': port}],
        http_auth=None,  # No authentication as security is disabled
        use_ssl=False,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False,
    )
    return client


def search_wikipedia_articles(client, query_text: str, k: int = 5, size: int = 5):
    """
    Search for Wikipedia articles using neural search with text embeddings.
    
    Args:
        client: OpenSearch client instance
        query_text: Text query to search for
        k: Number of nearest neighbors to find
        size: Number of results to return
        
    Returns:
        Search results from OpenSearch
    """
    # Get model ID from environment variable
    model_id = os.environ.get('OPENSEARCH_MODEL_ID')
    if not model_id:
        raise ValueError("OPENSEARCH_MODEL_ID environment variable not set. Please run opensearch_setup.py first.")
    
    # Build the neural search query
    search_query = {
        "_source": {
            "excludes": [
                "passage_embedding"
            ]
        },
        "size": size,
        "query": {
            "neural": {
                "passage_embedding": {
                    "query_text": query_text,
                    "model_id": model_id,
                    "k": k
                }
            }
        }
    }
    
    # Execute the search
    response = client.search(
        index="my-nlp-index",
        body=search_query
    )
    
    return response


def main():
    """
    Main entrypoint for querying Wikipedia articles.
    """
    # Create OpenSearch client
    client = create_opensearch_client()
    
    # Test connection
    try:
        if not client.ping():
            raise ConnectionError("Could not connect to OpenSearch cluster")
        print("Connected to OpenSearch cluster")
    except Exception as e:
        print(f"Error connecting to OpenSearch: {e}")
        return
    
    # Search for articles about Abraham Lincoln
    query_text = "What did Abraham Lincoln accomplish as president during the Civil War?"
    print(f"\nSearching Wikipedia for: '{query_text}'...")
    
    try:
        results = search_wikipedia_articles(client, query_text=query_text, k=5, size=5)
        
        # Print results
        print(f"\nFound {len(results['hits']['hits'])} relevant articles:")
        print("-" * 80)
        
        for i, hit in enumerate(results['hits']['hits'], 1):
            article_id = hit['_id']
            score = hit['_score']
            passage = hit['_source']['passage']
            
            # Truncate passage for display
            display_passage = passage[:200] + "..." if len(passage) > 200 else passage
            
            print(f"{i}. Article ID: {article_id}")
            print(f"   Relevance Score: {score:.4f}")
            print(f"   Passage: {display_passage}")
            print("-" * 80)
        
        # Print full response for debugging
        print("\nFull search response:")
        print(json.dumps(results, indent=2))
        
    except Exception as e:
        print(f"Error performing search: {e}")
        return


if __name__ == "__main__":
    main()
