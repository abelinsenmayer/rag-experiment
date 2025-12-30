"""
HuggingFace dataset setup for RAG experiment.
"""

from datasets import load_dataset
from huggingface_hub import login


def setup_rag_dataset():
    """
    Load and prepare the rag-datasets/rag-mini-wikipedia dataset.
    
    This function will:
    1. Authenticate with HuggingFace (if needed)
    2. Load the rag-mini-wikipedia dataset
    3. Display dataset information
    """
    
    # Optional: Login to HuggingFace if accessing private datasets
    # Uncomment the line below and run with your HuggingFace token
    # login(token="your-huggingface-token")
    
    print("Loading rag-datasets/rag-mini-wikipedia dataset...")
    
    try:
        # Load the dataset
        dataset = load_dataset("rag-datasets/rag-mini-wikipedia", "text-corpus")
        
        # Display dataset information
        print("\nDataset loaded successfully!")
        print(f"Dataset splits: {list(dataset.keys())}")
        
        for split_name, split_data in dataset.items():
            print(f"\n{split_name} split:")
            print(f"  Number of examples: {len(split_data)}")
            print(f"  Features: {split_data.features}")
            
            # Show a sample example
            if len(split_data) > 0:
                print(f"  Example 1:")
                example = split_data[0]
                for key, value in example.items():
                    # Truncate long text for display
                    if isinstance(value, str) and len(value) > 200:
                        value = value[:200] + "..."
                    print(f"    {key}: {value}")
        
        # Save dataset info for later use
        print("\nDataset is ready for use!")
        
        return dataset
        
    except Exception as e:
        print(f"Error loading dataset: {e}")
        raise


def main():
    """
    Main entrypoint for dataset setup.
    """
    dataset = setup_rag_dataset()


if __name__ == "__main__":
    main()
