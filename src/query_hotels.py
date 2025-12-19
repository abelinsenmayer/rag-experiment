"""
Query entrypoint for searching hotels in OpenSearch using k-NN.
"""

import json
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


def search_nearby_hotels(client, vector: list, k: int = 3, size: int = 3):
    """
    Search for hotels near the given vector coordinates using k-NN.
    
    Args:
        client: OpenSearch client instance
        vector: 2D coordinate vector to search near
        k: Number of nearest neighbors to find
        size: Number of results to return
        
    Returns:
        Search results from OpenSearch
    """
    # Build the k-NN search query
    search_query = {
        "size": size,
        "query": {
            "knn": {
                "location": {
                    "vector": vector,
                    "k": k
                }
            }
        }
    }
    
    # Execute the search
    response = client.search(
        index="hotels-index",
        body=search_query
    )
    
    return response


def main():
    """
    Main entrypoint for querying hotels.
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
    
    # Search for hotels near coordinates [5, 4]
    print("\nSearching for hotels near coordinates [5, 4]...")
    results = search_nearby_hotels(client, vector=[5, 4], k=3, size=3)
    
    # Print results
    print(f"\nFound {len(results['hits']['hits'])} hotels:")
    print("-" * 50)
    
    for hit in results['hits']['hits']:
        hotel_id = hit['_id']
        score = hit['_score']
        location = hit['_source']['location']
        print(f"Hotel ID: {hotel_id}")
        print(f"Location: {location}")
        print(f"Score: {score:.4f}")
        print("-" * 50)
    
    # Print full response for debugging
    print("\nFull search response:")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
