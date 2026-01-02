import sys
import os

# Add the current directory to sys.path so we can import app modules
sys.path.append(os.getcwd())

from app.core.semantic_cache import SemanticCache

def test_semantic_cache():
    print("Initializing SemanticCache...")
    cache = SemanticCache()
    
    # Test text
    q1 = "Show all users"
    q2 = "Display all users" 
    q3 = "Delete all databases"
    
    print(f"\nGenerating embeddings for:")
    print(f"1. '{q1}'")
    print(f"2. '{q2}'")
    print(f"3. '{q3}'")
    
    emb1 = cache.generate_embedding(q1)
    emb2 = cache.generate_embedding(q2)
    emb3 = cache.generate_embedding(q3)
    
    print("\nCalculating similarities:")
    
    sim1_2 = cache.compute_similarity(emb1, emb2)
    print(f"Similarity ('{q1}' vs '{q2}'): {sim1_2:.4f}")
    
    sim1_3 = cache.compute_similarity(emb1, emb3)
    print(f"Similarity ('{q1}' vs '{q3}'): {sim1_3:.4f}")
    
    threshold = cache.similarity_threshold
    print(f"\nThreshold is: {threshold}")
    
    if sim1_2 > threshold:
        print("PASS: Similar questions correctly identified!")
    else:
        print("FAIL: Similar questions NOT identified.")
        
    if sim1_3 < threshold:
        print("PASS: Dissimilar questions correctly rejected!")
    else:
        print("FAIL: Dissimilar questions NOT rejected.")

if __name__ == "__main__":
    test_semantic_cache()
