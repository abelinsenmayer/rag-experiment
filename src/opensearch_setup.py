"""
OpenSearch index setup module for RAG experiment.
"""

import json
from opensearchpy import OpenSearch


def setup_opensearch_indexes(host: str = "localhost", port: int = 9200):
    """
    Set up OpenSearch indexes for the RAG experiment.
    
    This function will create the necessary indexes with appropriate mappings.
    The actual implementation will be added later.
    
    Args:
        host: OpenSearch host address
        port: OpenSearch port number
    """
    # Create OpenSearch client
    client = OpenSearch(
        hosts=[{'host': host, 'port': port}],
        http_auth=None,  # No authentication as security is disabled
        use_ssl=False,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False,
    )
    
    # Test connection
    try:
        # Ping the cluster to verify connection
        if not client.ping():
            raise ConnectionError("Could not connect to OpenSearch cluster")
        
        # Get cluster info to verify it's working
        cluster_info = client.info()
        print(f"Connected to OpenSearch cluster: {cluster_info['cluster_name']}")
        print(f"OpenSearch version: {cluster_info['version']['number']}")
        
        # Create the hotels index with k-NN support
        index_name = "hotels-index"
        
        # Check if index already exists
        if client.indices.exists(index=index_name):
            print(f"Index '{index_name}' already exists. Deleting and recreating...")
            client.indices.delete(index=index_name)
        
        # Create index with k-NN settings and mappings
        index_body = {
            "settings": {
                "index.knn": True
            },
            "mappings": {
                "properties": {
                    "location": {
                        "type": "knn_vector",
                        "dimension": 2,
                        "space_type": "l2"
                    }
                }
            }
        }
        
        # Create the index
        response = client.indices.create(index=index_name, body=index_body)
        
        if response.get('acknowledged', False):
            print(f"Successfully created index '{index_name}'")
        else:
            print(f"Failed to create index '{index_name}'")
            print(f"Response: {response}")
        
        # Inject sample hotel data
        inject_sample_data(client)
        
    except Exception as e:
        print(f"Error connecting to OpenSearch: {e}")
        raise


def inject_sample_data(client):
    """
    Inject sample hotel data into the hotels index using bulk API.
    
    Args:
        client: OpenSearch client instance
    """
    print("\nInjecting sample hotel data...")
    
    # Prepare bulk data
    bulk_data = [
        # Hotel 1
        {"index": {"_index": "hotels-index", "_id": "1"}},
        {"location": [5.2, 4.4]},
        
        # Hotel 2
        {"index": {"_index": "hotels-index", "_id": "2"}},
        {"location": [5.2, 3.9]},
        
        # Hotel 3
        {"index": {"_index": "hotels-index", "_id": "3"}},
        {"location": [4.9, 3.4]},
        
        # Hotel 4
        {"index": {"_index": "hotels-index", "_id": "4"}},
        {"location": [4.2, 4.6]},
        
        # Hotel 5
        {"index": {"_index": "hotels-index", "_id": "5"}},
        {"location": [3.3, 4.5]},
    ]
    
    # Convert to bulk format string
    bulk_body = ""
    for item in bulk_data:
        bulk_body += f"{json.dumps(item)}\n"
    
    # Execute bulk request
    response = client.bulk(body=bulk_body)
    
    # Check for errors
    if response.get('errors', False):
        print("Some errors occurred during bulk indexing:")
        for item in response['items']:
            if 'index' in item and item['index'].get('error'):
                print(f"  Error: {item['index']['error']}")
    else:
        print(f"Successfully indexed {len(bulk_data) // 2} hotel documents")


if __name__ == "__main__":
    # Test connection when run directly
    setup_opensearch_indexes()
