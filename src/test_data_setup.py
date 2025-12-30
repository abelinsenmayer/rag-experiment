"""
Test data setup module for loading Q&A datasets for RAG experiment testing.
"""

from datasets import load_dataset
from typing import Dict, Any, List


def load_wikipedia_qa_dataset() -> Dict[str, Any]:
    """
    Load the mini-wikipedia question-answer dataset for testing.
    
    Returns:
        Dict containing the loaded Q&A dataset
    """
    print("Loading Wikipedia Q&A dataset...")
    
    try:
        # Load the question-answer dataset
        dataset = load_dataset("rag-datasets/rag-mini-wikipedia", "question-answer")
        
        print(f"Q&A dataset loaded successfully")
        print(f"Available splits: {list(dataset.keys())}")
        
        return dataset
        
    except Exception as e:
        print(f"Error loading Q&A dataset: {e}")
        return None


def get_qa_test_data(dataset: Dict[str, Any], split: str = "test", num_samples: int = 5) -> List[Dict[str, str]]:
    """
    Extract test questions and answers from the dataset.
    
    Args:
        dataset: The loaded Q&A dataset
        split: Dataset split to use (default: "test")
        num_samples: Number of Q&A pairs to extract (default: 5)
    
    Returns:
        List of dictionaries containing question and answer pairs
    """
    if not dataset or split not in dataset:
        print(f"Dataset or split '{split}' not available")
        return []
    
    try:
        # Get the specified split
        qa_data = dataset[split]
        
        # Extract the first num_samples Q&A pairs
        test_samples = []
        
        for i in range(min(num_samples, len(qa_data))):
            sample = {
                "question": qa_data[i]["question"],
                "answer": qa_data[i]["answer"]
            }
            test_samples.append(sample)
        
        return test_samples
        
    except Exception as e:
        print(f"Error extracting Q&A test data: {e}")
        return []


if __name__ == "__main__":
    # Test the data loading functionality
    dataset = load_wikipedia_qa_dataset()
    
    if dataset:
        print(f"\nDataset structure: {dataset}")
        
        # Try to get some test samples
        test_data = get_qa_test_data(dataset, num_samples=3)
        
        if test_data:
            print(f"\nSuccessfully extracted {len(test_data)} test samples")
            for i, qa in enumerate(test_data, 1):
                print(f"\nSample {i}:")
                print(f"Q: {qa['question']}")
                print(f"A: {qa['answer']}")
        else:
            print("No test data extracted")
