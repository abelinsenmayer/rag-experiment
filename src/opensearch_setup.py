"""
OpenSearch index setup module for RAG experiment with ML support.
"""

import json
import os
import time
from datasets import load_dataset
from opensearchpy import OpenSearch


def setup_opensearch_indexes(host: str = "localhost", port: int = 9200):
    """
    Set up OpenSearch indexes for the RAG experiment with ML capabilities.
    
    This function will:
    1. Configure ML cluster settings
    2. Register and deploy the sentence-transformers model
    3. Create an ingest pipeline with text embedding
    4. Create the NLP index with k-NN support
    
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
        
        # Step 1: Set up ML cluster settings
        setup_ml_cluster_settings(client)
        
        # Step 2: Register and deploy the embedding model
        model_id = register_and_deploy_model_separately(client)
        
        # Store model ID in environment variable
        os.environ['OPENSEARCH_MODEL_ID'] = model_id
        print(f"Model ID stored in environment variable: {model_id}")
        
        # Step 3: Create the ingest pipeline
        create_ingest_pipeline(client, model_id)
        
        # Step 4: Create the NLP index
        create_nlp_index(client)
        
        # Step 5: Load and ingest the dataset
        ingest_wikipedia_dataset(client)
        
        print("\nOpenSearch ML setup completed successfully!")
        
    except Exception as e:
        print(f"Error setting up OpenSearch: {e}")
        raise


def setup_ml_cluster_settings(client):
    """
    Configure ML cluster settings for OpenSearch.
    
    Args:
        client: OpenSearch client instance
    """
    print("\nConfiguring ML cluster settings...")
    
    settings = {
        "persistent": {
            "plugins.ml_commons.only_run_on_ml_node": "false",
            "plugins.ml_commons.native_memory_threshold": "99"
        }
    }
    
    response = client.cluster.put_settings(body=settings)
    
    if response.get('acknowledged', False):
        print("ML cluster settings configured successfully")
    else:
        print("Failed to configure ML cluster settings")
        print(f"Response: {response}")


def register_and_deploy_model_separately(client):
    """
    Register and deploy the sentence-transformers embedding model in separate steps.
    
    Args:
        client: OpenSearch client instance
        
    Returns:
        str: The deployed model ID
    """
    # Step 1: Register the model
    model_id = register_model(client)
    
    # Step 2: Deploy the model
    deploy_model(client, model_id)
    
    # Step 3: Verify model is ready for inference
    verify_model_ready(client, model_id)
    
    return model_id


def register_model(client):
    """
    Register the sentence-transformers embedding model.
    
    Args:
        client: OpenSearch client instance
        
    Returns:
        str: The registered model ID
    """
    print("\nRegistering embedding model...")
    
    model_config = {
        "name": "huggingface/sentence-transformers/all-MiniLM-L6-v2",
        "version": "1.0.1",
        "model_format": "TORCH_SCRIPT"
    }
    
    # Register the model (without deploying)
    response = client.transport.perform_request(
        'POST',
        '/_plugins/_ml/models/_register',
        body=model_config
    )
    
    task_id = response.get('task_id')
    print(f"Model registration task started with ID: {task_id}")
    
    # Wait for registration to complete
    model_id = wait_for_task_completion(client, task_id, "registration")
    
    return model_id


def deploy_model(client, model_id):
    """
    Deploy a registered model.
    
    Args:
        client: OpenSearch client instance
        model_id: The ID of the registered model
    """
    print(f"\nDeploying model {model_id}...")
    
    # Deploy the model
    response = client.transport.perform_request(
        'POST',
        f'/_plugins/_ml/models/{model_id}/_deploy'
    )
    
    task_id = response.get('task_id')
    print(f"Model deployment task started with ID: {task_id}")
    
    # Wait for deployment to complete
    wait_for_task_completion(client, task_id, "deployment", model_id)


def wait_for_task_completion(client, task_id, operation, model_id=None, timeout=300):
    """
    Wait for a model task to complete.
    
    Args:
        client: OpenSearch client instance
        task_id: The task ID to monitor
        operation: Description of the operation (e.g., "registration", "deployment")
        model_id: The model ID (for deployment tasks)
        timeout: Maximum time to wait in seconds
        
    Returns:
        str: The model ID (for registration tasks)
    """
    print(f"Waiting for model {operation}...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        # Check task status
        response = client.transport.perform_request(
            'GET',
            f'/_plugins/_ml/tasks/{task_id}'
        )
        
        state = response.get('state')
        
        if state == 'COMPLETED':
            if operation == "registration":
                model_id = response.get('model_id')
                print(f"Model registered successfully with ID: {model_id}")
                return model_id
            elif operation == "deployment":
                print(f"Model deployed successfully!")
                return model_id
        elif state == 'FAILED':
            error = response.get('error', 'Unknown error')
            raise Exception(f"Model {operation} failed: {error}")
        
        print(f"Model {operation} in progress... (state: {state})")
        time.sleep(5)
    
    raise TimeoutError(f"Model {operation} timed out after {timeout} seconds")


def verify_model_ready(client, model_id, timeout=300):
    """
    Verify that the model is fully deployed and ready for inference.
    
    Args:
        client: OpenSearch client instance
        model_id: The ID of the deployed model
        timeout: Maximum time to wait in seconds
    """
    print("\nVerifying model is ready for inference...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            # Check model status
            response = client.transport.perform_request(
                'GET',
                f'/_plugins/_ml/models/{model_id}'
            )
            
            model_state = response.get('model_state')
            
            if model_state == 'DEPLOYED':
                print("Model is ready for inference!")
                return
            elif model_state in ['PARTIALLY_DEPLOYED', 'DEPLOYING']:
                print(f"Model deployment in progress... (model_state: {model_state})")
            else:
                print(f"Model state: {model_state}")
            
            time.sleep(10)  # Wait 10 seconds before checking again
            
        except Exception as e:
            print(f"Error checking model status: {e}")
            time.sleep(10)
    
    raise TimeoutError(f"Model not ready after {timeout} seconds")


def create_ingest_pipeline(client, model_id):
    """
    Create an ingest pipeline with text embedding processor.
    
    Args:
        client: OpenSearch client instance
        model_id: The ID of the deployed model
    """
    print("\nCreating NLP ingest pipeline...")
    
    pipeline_config = {
        "description": "An NLP ingest pipeline",
        "processors": [
            {
                "text_embedding": {
                    "model_id": model_id,
                    "field_map": {
                        "passage": "passage_embedding"
                    }
                }
            }
        ]
    }
    
    response = client.ingest.put_pipeline(
        id='nlp-ingest-pipeline',
        body=pipeline_config
    )
    
    if response.get('acknowledged', False):
        print("NLP ingest pipeline created successfully")
    else:
        print("Failed to create NLP ingest pipeline")
        print(f"Response: {response}")


def create_nlp_index(client):
    """
    Create the NLP index with k-NN support and ingest pipeline.
    
    Args:
        client: OpenSearch client instance
    """
    print("\nCreating NLP index...")
    
    index_name = "my-nlp-index"
    
    # Check if index already exists
    if client.indices.exists(index=index_name):
        print(f"Index '{index_name}' already exists. Deleting and recreating...")
        client.indices.delete(index=index_name)
    
    index_config = {
        "settings": {
            "index.knn": True,
            "default_pipeline": "nlp-ingest-pipeline"
        },
        "mappings": {
            "properties": {
                "passage_embedding": {
                    "type": "knn_vector",
                    "dimension": 384,
                    "method": {
                        "name": "hnsw",
                        "space_type": "l2",
                        "engine": "nmslib"
                    }
                },
                "passage": {
                    "type": "text"
                }
            }
        }
    }
    
    # Create the index
    response = client.indices.create(index=index_name, body=index_config)
    
    if response.get('acknowledged', False):
        print(f"Successfully created index '{index_name}'")
    else:
        print(f"Failed to create index '{index_name}'")
        print(f"Response: {response}")


def ingest_wikipedia_dataset(client):
    """
    Load and ingest the Wikipedia dataset into OpenSearch.
    
    Args:
        client: OpenSearch client instance
    """
    print("\nLoading Wikipedia dataset...")
    
    try:
        # Load the dataset
        dataset = load_dataset("rag-datasets/rag-mini-wikipedia", "text-corpus")
        
        # Get the train split
        train_data = dataset["passages"]
        
        print(f"Dataset loaded with {len(train_data)} documents")
        print("Starting ingestion...")
        
        # Process documents in batches
        batch_size = 100
        total_ingested = 0
        
        for i in range(0, len(train_data), batch_size):
            # Get batch
            batch = train_data[i:i + batch_size]
            
            # Prepare bulk data
            bulk_data = []
            
            # The batch structure is {"passage": [...], "id": [...]}
            passages = batch["passage"]
            ids = batch["id"]
            
            for idx, passage in enumerate(passages):
                doc_id = ids[idx] if idx < len(ids) else f"{i + idx}"
                
                # Add index operation
                bulk_data.append({
                    "index": {"_index": "my-nlp-index", "_id": str(doc_id)}
                })
                # Add document
                bulk_data.append({
                    "passage": passage
                })
            
            # Convert to bulk format
            bulk_body = ""
            for item in bulk_data:
                bulk_body += f"{json.dumps(item)}\n"
            
            # Execute bulk request
            response = client.bulk(body=bulk_body)
            
            # Check for errors
            if response.get('errors'):
                print(f"Errors in batch {i//batch_size + 1}:")
                for item in response['items']:
                    if 'index' in item and item['index'].get('error'):
                        print(f"  Error: {item['index']['error']}")
            else:
                total_ingested += len(passages)
                if (i // batch_size + 1) % 10 == 0:  # Print every 10 batches
                    print(f"Ingested {total_ingested} documents...")
        
        print(f"\nSuccessfully ingested {total_ingested} documents into OpenSearch")
        
    except Exception as e:
        print(f"Error ingesting dataset: {e}")
        raise


if __name__ == "__main__":
    # Test connection when run directly
    setup_opensearch_indexes()
