from src.matcher import IngredientMatcher

def standardize_ingredients(user_ingredients, ai_ingredients):
    matcher = IngredientMatcher(threshold=0.7)
    
    print("Matching User Ingredients...")
    matched_user = matcher.match_ingredients_list(user_ingredients)
    
    print("Matching AI-Generated Ingredients...")
    matched_ai = matcher.match_ingredients_list(ai_ingredients)
    
    return matched_user, matched_ai

if __name__ == "__main__":
    user_ingredients = [
        "all purpose flour",
        "gran sugar",
        "olive oil",
        "black pepper",
        "chicken breasts",
        "eggs",
        "milk",
        "butter"
    ]
    
    ai_ingredients = [
        "all-purpose flour",
        "granulated sugar",
        "extra virgin olive oil",
        "black pepper",
        "chicken breast",
        "egg",
        "whole milk",
        "unsalted butter"
    ]
    
    matched_user, matched_ai = standardize_ingredients(user_ingredients, ai_ingredients)
    
    print("\nMatched User Ingredients:")
    for k, v in matched_user.items():
        print(f"{k} -> {v['matched_name']} (Similarity: {v['similarity']:.2f})")
    
    print("\nMatched AI-Generated Ingredients:")
    for k, v in matched_ai.items():
        print(f"{k} -> {v['matched_name']} (Similarity: {v['similarity']:.2f})") 