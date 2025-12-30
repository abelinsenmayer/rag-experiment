"""
Q&A Test Runner for RAG experiment.
This script loads the question-answer dataset and displays test questions/answers.
"""

from test_data_setup import load_wikipedia_qa_dataset, get_qa_test_data
from query_ollama import query_gemma3_model, query_gemma3_model_with_rag


def display_qa_samples(qa_samples, title="Test Questions and Answers"):
    """
    Display Q&A samples in a formatted way.
    
    Args:
        qa_samples: List of question-answer dictionaries
        title: Title to display above the samples
    """
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    
    if not qa_samples:
        print("No Q&A samples to display.")
        return
    
    for i, qa in enumerate(qa_samples, 1):
        print(f"\n📝 Question {i}:")
        print(f"   {qa['question']}")
        print(f"\n✅ Answer {i}:")
        print(f"   {qa['answer']}")
        print(f"\n{'-'*50}")


def compare_answers_with_gemma(gemma_answer, correct_answer):
    """
    Use Gemma to compare two answers for semantic equivalence.
    
    Args:
        gemma_answer: Answer provided by Gemma
        correct_answer: Correct answer from dataset
    
    Returns:
        str: 'CORRECT' if semantically equivalent, 'INCORRECT' if not, or 'ERROR' if failed
    """
    comparison_prompt = f"""Compare these two answers for semantic equivalence:

Answer 1: {gemma_answer}
Answer 2: {correct_answer}

Are these answers semantically equivalent? Answer only "CORRECT" if they are equivalent or "INCORRECT" if they are not. Do not elaborate."""
    
    comparison_result = query_gemma3_model(comparison_prompt)
    
    if comparison_result:
        # Clean up the response and extract CORRECT/INCORRECT
        result = comparison_result.strip().upper()
        if "CORRECT" in result and "INCORRECT" not in result:
            return "CORRECT"
        elif "INCORRECT" in result:
            return "INCORRECT"
        else:
            return "ERROR"
    else:
        return "ERROR"


def evaluate_with_ollama(qa_samples, use_rag=False, title="Ollama Gemma3 Evaluation"):
    """
    Evaluate Ollama Gemma3 responses against correct answers.
    
    Args:
        qa_samples: List of question-answer dictionaries
        use_rag: Whether to use RAG-enabled queries
        title: Title to display above the evaluation
    
    Returns:
        dict: Evaluation results with answer pairs and correctness scores
    """
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}")
    
    if not qa_samples:
        print("No Q&A samples to evaluate.")
        return {"answer_pairs": [], "total_questions": 0, "correct_count": 0, "percentage": 0}
    
    answer_pairs = []
    
    for i, qa in enumerate(qa_samples, 1):
        # Show progress every 10 questions
        if i % 10 == 1 or i == len(qa_samples):
            mode_text = "RAG-enabled" if use_rag else "regular"
            print(f"\n🤖 Processing {mode_text} questions {i}-{min(i+9, len(qa_samples))} of {len(qa_samples)}...")
        
        # Choose query function based on RAG setting
        if use_rag:
            ollama_response = query_gemma3_model_with_rag(qa['question'])
        else:
            # Format the prompt with specific instructions for concise answers
            formatted_prompt = f"{qa['question']}\n\nAnswer in a single word or a short sentence. Do not ask follow-up questions or make suggestions."
            ollama_response = query_gemma3_model(formatted_prompt)
        
        if not ollama_response:
            ollama_response = "[NO RESPONSE]"
        
        # Store the answer pair
        answer_pairs.append({
            "question": qa['question'],
            "gemma_answer": ollama_response,
            "correct_answer": qa['answer']
        })
    
    return {"answer_pairs": answer_pairs, "total_questions": len(qa_samples), "correct_count": 0, "percentage": 0}


def run_qa_test(num_questions=None):
    """
    Main function to run the Q&A test with Ollama Gemma3 evaluation.
    Loads the dataset and evaluates Ollama responses against correct answers.
    
    Args:
        num_questions: Number of questions to test (default: all available)
    """
    print("🚀 Starting Q&A Test Runner...")
    print("Loading Wikipedia Q&A dataset for testing...")
    
    # Load the Q&A dataset
    dataset = load_wikipedia_qa_dataset()
    
    if not dataset:
        print("❌ Failed to load dataset. Exiting.")
        return
    
    # Try different splits to find available data
    available_splits = list(dataset.keys())
    print(f"Available dataset splits: {available_splits}")
    
    # Try to get test data from different splits
    test_data = None
    for split in ["test", "validation", "train"]:
        if split in available_splits:
            print(f"\nTrying to load data from '{split}' split...")
            # Use num_questions parameter or default to 5 for initial load
            initial_samples = num_questions if num_questions else 5  # Load more initially to have options
            test_data = get_qa_test_data(dataset, split=split, num_samples=initial_samples)
            if test_data:
                print(f"✅ Successfully loaded {len(test_data)} samples from '{split}' split")
                break
            else:
                print(f"❌ No data found in '{split}' split")
    
    if not test_data:
        print("❌ Could not load any test data from any split.")
        return
    
    # Limit to requested number of questions
    if num_questions and len(test_data) > num_questions:
        test_data = test_data[:num_questions]
        print(f"\n📊 Limited to first {num_questions} questions for evaluation")
    
    # Evaluate with regular Ollama Gemma3
    print(f"\n🚀 Starting Regular Gemma3 Evaluation...")
    regular_results = evaluate_with_ollama(test_data, use_rag=False, title=f"Regular Gemma3 Evaluation - {len(test_data)} Questions")
    
    # Evaluate with RAG-enabled Ollama Gemma3
    print(f"\n🚀 Starting RAG-enabled Gemma3 Evaluation...")
    rag_results = evaluate_with_ollama(test_data, use_rag=True, title=f"RAG-enabled Gemma3 Evaluation - {len(test_data)} Questions")
    
    # Function to calculate accuracy for a set of results
    def calculate_accuracy(evaluation_results, mode_name):
        if not evaluation_results["answer_pairs"]:
            return 0, 0, 0
            
        print(f"\n{'='*70}")
        print(f"{mode_name} Semantic Equivalence Evaluation")
        print(f"{'='*70}")
        
        correct_count = 0
        total_questions = len(evaluation_results["answer_pairs"])
        
        for i, pair in enumerate(evaluation_results["answer_pairs"], 1):
            # Show progress every 10 comparisons
            if i % 10 == 1 or i == len(evaluation_results["answer_pairs"]):
                print(f"\n🔍 Evaluating {mode_name.lower()} semantic equivalence {i}-{min(i+9, len(evaluation_results['answer_pairs']))} of {len(evaluation_results['answer_pairs'])}...")
            
            if pair["gemma_answer"] == "[NO RESPONSE]":
                continue
                
            comparison_result = compare_answers_with_gemma(pair["gemma_answer"], pair["correct_answer"])
            
            if comparison_result == "CORRECT":
                correct_count += 1
        
        # Calculate percentage
        percentage = (correct_count / total_questions) * 100 if total_questions > 0 else 0
        return total_questions, correct_count, percentage
    
    # Calculate accuracy for both modes
    regular_total, regular_correct, regular_percentage = calculate_accuracy(regular_results, "Regular Gemma3")
    rag_total, rag_correct, rag_percentage = calculate_accuracy(rag_results, "RAG-enabled Gemma3")
    
    # Comparative Results
    print(f"\n{'='*80}")
    print(f"🏆 COMPARATIVE EVALUATION RESULTS")
    print(f"{'='*80}")
    print(f"")
    print(f"🤖 Regular Gemma3 Results:")
    print(f"   Total Questions: {regular_total}")
    print(f"   Correct Answers: {regular_correct}")
    print(f"   Incorrect Answers: {regular_total - regular_correct}")
    print(f"   Accuracy: {regular_percentage:.1f}%")
    print(f"")
    print(f"🤖📚 RAG-enabled Gemma3 Results:")
    print(f"   Total Questions: {rag_total}")
    print(f"   Correct Answers: {rag_correct}")
    print(f"   Incorrect Answers: {rag_total - rag_correct}")
    print(f"   Accuracy: {rag_percentage:.1f}%")
    print(f"")
    print(f"📊 Performance Comparison:")
    if rag_percentage > regular_percentage:
        improvement = rag_percentage - regular_percentage
        print(f"   ✅ RAG improved accuracy by {improvement:.1f} percentage points")
        print(f"   📈 RAG shows {improvement/regular_percentage*100:.1f}% relative improvement")
    elif regular_percentage > rag_percentage:
        decline = regular_percentage - rag_percentage
        print(f"   ❌ RAG decreased accuracy by {decline:.1f} percentage points")
        print(f"   📉 RAG shows {decline/regular_percentage*100:.1f}% relative decline")
    else:
        print(f"   ⚖️ RAG and regular Gemma3 performed equally")
    print(f"{'='*80}")
    
    # Summary
    print(f"\n🎯 Evaluation Summary:")
    print(f"   • Dataset loaded successfully")
    print(f"   • Evaluated {len(test_data)} Q&A pairs with both regular and RAG-enabled Gemma3")
    print(f"   • Performed semantic equivalence analysis for both modes")
    print(f"   • RAG evaluation complete - see comparative results above!")


if __name__ == "__main__":
    # Run with 10 questions as starting point for comparison
    run_qa_test(num_questions=200)
