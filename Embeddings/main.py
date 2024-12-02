from src.matcher import IngredientMatcher
import config

def standardize_ingredients(user_ingredients, ai_ingredients):
    matcher = IngredientMatcher(threshold=config.THRESHOLD)
    
    print("Matching User Ingredients...")
    matched_user = matcher.match_ingredients_list(user_ingredients)
    
    print("Matching AI-Generated Ingredients...")
    matched_ai = matcher.match_ingredients_list(ai_ingredients)
    
    return matched_user, matched_ai

if __name__ == "__main__":
    matched_user, matched_ai = standardize_ingredients(config.USER_INGREDIENTS, config.AI_INGREDIENTS)
    
    print("\nMatched User Ingredients:")
    for k, v in matched_user.items():
        print(f"{k} -> {v['matched_name']} (Similarity: {v['similarity']:.2f})")
    
    print("\nMatched AI-Generated Ingredients:")
    for k, v in matched_ai.items():
        print(f"{k} -> {v['matched_name']} (Similarity: {v['similarity']:.2f})") 