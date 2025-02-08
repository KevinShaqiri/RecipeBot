# Import necessary libraries.
import json
import sys
from difflib import get_close_matches
import re
import random
from datetime import  datetime
# Initialize a global list to store the user's current ingredients.

current_ingredients = []
user_dietary_restrictions = []  
# Function to load recipes from a JSON file.
def load_json(filename: str):
    # Open the specified file.
    with open(filename,'r') as file:
        # Load the JSON data from the file.
        recipes = json.load(file) 
    # Return the loaded recipes.
    return recipes
 
#Function to load bot knowledge base.
def load_bot_knowledge(filename:str)->dict:

    with open(filename) as file:
        data:dict=json.load(file) # Load and parse the JSON data into a dictionary
    return data    

def load_ingredients(filename:str):
  # Open the specified file in read mode.
    with open(filename, 'r') as file:
        # Load the JSON data, which is expected to be a list of recipes.
        recipes = json.load(file)
    
    # Initialize an empty set to store unique ingredients.
    unique_ingredients = set()
    
    # Iterate through each recipe in the list.
    for recipe in recipes:
        # Add each ingredient of the current recipe to the set.
        # Since a set is used, only unique ingredients are kept.
        unique_ingredients.update(recipe['ingredients'])
    
    # Convert the set back to a list to return it.
    return list(unique_ingredients)    

     


def find_best_match(user_question:str,questions:list[str])->str | None:
    match=get_close_matches(user_question,questions,n=1,cutoff=0.6)
    return match[0] if match else None #Since get_close_matches returns a list,then match[0] gives the first value of a list,in this case a string

def get_answer_for_question(question: str, knowledge_base: dict) -> str | None:
    for q in knowledge_base["questions"]:
        if q["question"] == question:
            return q["answer"]  # Return the answer if the question is found


# Function to find recipes that can be made with the user's ingredients.
def find_recipes(user_ingredients, recipes):
    matching_recipes = []
    for recipe in recipes:
        # Check if recipe meets dietary restrictions
        if not all(restriction in recipe.get('dietaryRestrictions', []) for restriction in user_dietary_restrictions):
            continue  # Skip recipes that don't meet the dietary restrictions
        if all(ingredient in user_ingredients for ingredient in recipe['ingredients']):
            matching_recipes.append(recipe)
    if not matching_recipes:
        print("No recipes available with those ingredients and dietary preferences.")
    return matching_recipes


def add_ingredient():
    
    # Prompt the user to add an ingredient, remove one, or quit.
    new_ingredient = input("Bot: Please add an ingredient or dietary restriction.\nBot: To quit, write 'quit'.\nBot: If you want some additional commands,write help :\n").lower()
    # Check if the user wants to quit the program.
    if new_ingredient == 'quit':
        print("Exited recipe mode!\n")
        return False
    # Check if the user wants to remove an ingredient.
    elif 'diet' in new_ingredient.lower() or 'restriction' in new_ingredient.lower() or 'restrictions' in new_ingredient.lower():
        return ask_dietary_restrictions()
    elif 'remove restriction' in new_ingredient:
        delete_dietary_restrictions()    
        return True
    elif 'show restrictions' in new_ingredient:
        show_dietary_restrictions()
        return True
    elif 'remove' in new_ingredient:
        # Extract the ingredient to be removed from the input string.
        ingredient_to_remove = new_ingredient.split('remove ')[-1]
        # Check if the ingredient to be removed is in the current ingredients list.
        if ingredient_to_remove in current_ingredients:
            remove_ingredient(ingredient_to_remove)
            return True
        else:
            print('Bot: Could not remove ingredient. It may not exist in the list.')
            return True
    elif 'help' in new_ingredient:
        print("Recipebot commands: ")
        print("\'remove Your_Ingredient\' : Removes an ingredient from your current list of ingredients")
        print("\'show ingredients\': Shows your current ingredients")
        print("\' quit\' : Exits from the current mode")
        print("\'Your_ingredient\' : Adds an ingredient")
        print("\'diet' : Add a dietary restriction")
        print("\'remove restriction' : Remove a dietary restriction")
        print("\'show resrictions' Shows your current dietary restrictions\n")
        return True
    elif new_ingredient == 'show ingredients':
        if not current_ingredients:
            print('Bot: There are currently no ingredients')
            return True
        print("Bot: Current ingredients:")
        for ingredient in current_ingredients:
            print(ingredient.capitalize())
        return True
    elif new_ingredient not in load_ingredients('knowledge_base.json'):
        print("Bot: That ingredient is not available,please choose another one.")
        return True

    else:
        # If adding a new ingredient (not removing or showing), append it to the current ingredients list.
        current_ingredients.append(new_ingredient)
        return True
    
# Function to remove an ingredient from the user's list.
def remove_ingredient(ingredient):
    # Remove the specified ingredient from the current ingredients list.
    current_ingredients.remove(ingredient)


def ask_dietary_restrictions():
    global user_dietary_restrictions
    valid_restrictions = ["vegan", "vegetarian", "gluten-free"]  # Valid dietary restrictions
    if user_dietary_restrictions:
        print("Current dietary restrictions:", ", ".join(user_dietary_restrictions))
        change = input("Would you like to change your dietary restrictions? (yes/no) ").lower().strip()
        if change == 'no':
            return True
    
    while True:  # Loop until valid input is provided
        print("Please enter your dietary restrictions separated by commas.")
        print("Available options: vegan, vegetarian, gluten-free. Type 'none' for no restrictions.")
        restrictions = input("Your dietary restrictions: ").lower().strip()
        
        if restrictions == 'none':
            user_dietary_restrictions = []
            print("All dietary restrictions have been cleared.\n")
            return True
        elif restrictions=="quit":
         print("Exiting the dietary restrictions setup.\n")
         return True
        else:
            # Split the input and filter out any invalid or duplicate entries
            input_restrictions = [r.strip() for r in restrictions.split(',') if r.strip() in valid_restrictions]
            if not input_restrictions:
                print("None of the entered restrictions are valid. Please try again.")
                continue  # Ask for the input again if none are valid

            # Check if the user tried to input any restrictions not on the list
            invalid_entries = [r.strip() for r in restrictions.split(',') if r.strip() not in valid_restrictions]
            if invalid_entries:
                print("Some restrictions are not recognized: " + ", ".join(invalid_entries))
                print("Please only use the available options.")
                continue  # Ask for the input again if there are invalid entries

            user_dietary_restrictions = input_restrictions
            print("Your dietary restrictions have been updated to: " + ", ".join(user_dietary_restrictions))
            print()
            return True  # Exit the loop if all entries are valid




def show_dietary_restrictions():
    if not user_dietary_restrictions:
        print("No dietary restrictions set.")
    else:
        print("Current dietary restrictions:", ", ".join(user_dietary_restrictions))
def delete_dietary_restrictions():
    global user_dietary_restrictions
    if not user_dietary_restrictions:
        print("No dietary restrictions to remove.")
    else:
        print("Current dietary restrictions:", ", ".join(user_dietary_restrictions))
        while True:
            restriction_to_remove=input("Which restriction would you like to remove?")
            if restriction_to_remove not in user_dietary_restrictions:
                print("Unable to remove,it might not be in your list,please try again.")
            else:    
             user_dietary_restrictions.remove(restriction_to_remove)
             print(f"Succesfully removed '{restriction_to_remove}' from your restrictions")
             break
        
# Function to display the recipes that match the user's ingredients.
def showrecipes(recipes):
    # Find recipes that match the current ingredients.
    matching_recipes = find_recipes(current_ingredients, recipes)
    # If there are matching recipes, print them out.
    if matching_recipes:
        for recipe in matching_recipes:
            # Print the recipe name.
            print(f"Recipe Name: {recipe['name']}")
            # Print the list of ingredients.
            print(f"Ingredients: {', '.join(recipe['ingredients'])}")
            #Print the calories
            print(f"Calories: {recipe['calories']}")
            #Print the Cooking time
            print(f"Cooking time: {recipe['cookingTime']} min")
            #Print the instructions 
            print(f"Instructions: {recipe['instructions']}")
            print()  # Print a newline for better separation between recipes.



   

def recipeMode():

 # Load recipes from a JSON file.
    recipes = load_json('knowledge_base.json')
    # Enter a loop to continually ask the user to add ingredients and show matching recipes.
    while True:
        should_show_recipes = add_ingredient()
        if should_show_recipes:
            showrecipes(recipes)
        else:
          break

    



def bot():
   botKnowledgeBase=load_bot_knowledge('bot.json')
   recipes=load_json('knowledge_base.json')
   print("Bot: Hello,how can i help you?")
   while True:
    user_input=input("You: ")
    user_input_lower=user_input.lower()
    if user_input_lower=='quit':
       sys.exit()
    #Finding the best match
    best_match:str |None=find_best_match(user_input,(q["question"] for q in botKnowledgeBase["questions"]))
    if 'hi' in user_input_lower or 'hello' in user_input_lower or 'whats up' in user_input_lower  or 'what\'s up' in user_input_lower:
        a=random.randint(1,4)
        if a==1:
            print("Hi!")
            continue
        elif a==2:
            print("Hello!")   
            continue
        elif a==3:
            print("What\'s up!")
            continue
        else:
            print("Ciao!")
            continue
    elif 'help' in user_input_lower :
        print("Chatbot commands: ")
        print("\' quit\' : exits from the current mode")
        print("\'recipes' : enters recipe mode")
    elif best_match:
        answer:str=get_answer_for_question(best_match,botKnowledgeBase)
        print(f"Bot: {answer}")
    elif 'date' in user_input_lower or 'what is the date' in user_input_lower or 'what\'s the date' in user_input_lower:
        print(f"The date is : {datetime.now().date()}") 
    elif 'time' in user_input_lower or 'what is the time' in user_input_lower or 'what\'s the time' in user_input_lower:
        # Using strftime to format the time
        print(f"The time is : {datetime.now().strftime('%H:%M:%S')}") 
    elif re.search(r'\b' + re.escape('recipe') + r'\b', user_input_lower) or re.search(r'\b' + re.escape('recipes') + r'\b', user_input_lower) : #Checks if the words are in the user input
        yes_or_no=input("Bot: Would you like to look at recipes?If yes,write yes and you can start adding ingredients.Otherwise,write anything else.")
        if 'yes' in (yes_or_no.lower()).strip():
            recipeMode()
        else:
            print("What can i help you with?")
            continue    
         
    else:
        print("I am not sure i can answer that,please try again!")    
    
    
    

bot()