import os
import random
import tkinter as tk
from tkinter import messagebox
from google.cloud import translate_v2 as translate
from google.cloud import aiplatform as vertexai
from vertexai.generative_models import GenerationConfig, GenerativeModel

##### google cloud translate setup #####

# only use vertex path
credentials_path = "/Users/lukedoudna/Downloads/howdyhack-437017-b83f0253d9c7.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

# initialize translate
def translate_text(text, target_language="es"):
    translate_client = translate.Client()
    result = translate_client.translate(text, target_language=target_language)
    return result['translatedText']

##### vertex ai / gemini setup #####

# initialize ai
PROJECT_ID = "howdyhack-437017"
LOCATION = "us-central1"
vertexai.init(project=PROJECT_ID, location=LOCATION)

MODEL_ID = "gemini-1.5-pro-002"
example_model = GenerativeModel(
    MODEL_ID,
    system_instruction=[
        "You are a language model that generates concise content based on the user's category input.",
        "Your mission is to provide 5 words related to the specified category."
    ],
)

generation_config = GenerationConfig(
    temperature=0.7,
    max_output_tokens=150,
)

def generate_category_words(category):
    difficulty_level = selected_difficulty.get().lower()

    # difficulty prompts
    if difficulty_level == "basic":
        prompt = f"Category: {category}\nDifficulty: Basic\nProvide 5 simple and common words related to this category."
    elif difficulty_level == "normal":
        prompt = f"Category: {category}\nDifficulty: Normal\nProvide 5 slightly complex words related to this category."
    elif difficulty_level == "advanced":
        prompt = f"Category: {category}\nDifficulty: Advanced\nProvide 5 complex and specialized words related to this category."
    
    response = example_model.generate_content(
        [prompt],
        generation_config=generation_config
    )
    words = response.text.strip().split(", ")
    print(f"Generated words for category '{category}' with difficulty '{difficulty_level}': {words}")  # Debugging output
    return words



# language list
language_options = [
    ("Spanish", "es"),
    ("Italian", "it"),
    ("Portuguese", "pt"),
    ("German", "de"),
    ("French", "fr")
]



def create_language_dropdown():
    tk.Label(root, text="Select a Language:").pack()
    selected_language.set(language_options[0][0]) #default

    language_menu = tk.OptionMenu(root, selected_language, *[lang[0] for lang in language_options])
    language_menu.pack()
    

difficulty_options = [
    ("Basic", "basic"),
    ("Normal", "normal"),
    ("Advanced", "advanced")
]


def create_difficulty_dropdown():
    tk.Label(root, text="Select Difficulty Level:").pack()
    selected_difficulty.set(difficulty_options[0][0])  #default

    difficulty_menu = tk.OptionMenu(root, selected_difficulty, *[level[0] for level in difficulty_options])
    difficulty_menu.pack()



def on_category_selected():
    category = category_entry.get()
    if not category:
        messagebox.showwarning("Warning", "Please enter a category.")
        return
    
    target_language_code = next(code for name, code in language_options if name == selected_language.get())
    
    words = generate_category_words(category)
    if len(words) < 5:
        messagebox.showerror("Error", "Not enough words generated. Please try a different category.")
        return
    
    
    global current_words, current_translations
    current_words = random.sample(words, 5)
    
    current_translations = [translate_text(word, target_language=target_language_code) for word in current_words]
    
    shuffled_translations = current_translations.copy()
    random.shuffle(shuffled_translations)

    display_matching_interface(current_words, shuffled_translations)

def display_matching_interface(words, translations):
    for widget in matching_frame.winfo_children():
        widget.destroy()

    word_bank_frame = tk.Frame(matching_frame)
    word_bank_frame.pack(pady=10)

    tk.Label(word_bank_frame, text="Possible Translations:").pack()

    for translation in translations:
        tk.Label(word_bank_frame, text=translation).pack()

    tk.Label(matching_frame, text="Match the words with their translations:").pack(pady=10)

    global entry_vars
    entry_vars = [tk.StringVar() for _ in range(len(words))]

    for i, word in enumerate(words):
        tk.Label(matching_frame, text=word).pack()
        entry = tk.Entry(matching_frame, textvariable=entry_vars[i])
        entry.pack()

    tk.Button(matching_frame, text="Submit", command=check_matches).pack(pady=10)

def check_matches():
    correct_count = 0
    for i in range(len(current_words)):
        user_translation = entry_vars[i].get()
        if user_translation.strip().casefold() == current_translations[i].casefold():
            correct_count += 1
    
    messagebox.showinfo("Results", f"You matched {correct_count} out of {len(current_words)} words correctly!")

def reset_game():
    category_entry.delete(0, tk.END)
    for entry_var in entry_vars:
        entry_var.set("")
    for widget in matching_frame.winfo_children():
        widget.destroy()
    selected_language.set(language_options[0][0])

def open_translator():
    translator_window = tk.Toplevel(root)
    translator_window.title("Text Translator")
    
    tk.Label(translator_window, text="Enter text to translate:").pack(pady=10)
    text_to_translate = tk.Entry(translator_window, width=50)
    text_to_translate.pack(pady=10)

    tk.Label(translator_window, text="Select a Language:").pack(pady=10)
    selected_translation_language = tk.StringVar()
    selected_translation_language.set(language_options[0][0])

    translation_menu = tk.OptionMenu(translator_window, selected_translation_language, *[lang[0] for lang in language_options])
    translation_menu.pack()

    def translate_and_display():
        text = text_to_translate.get()
        if not text:
            messagebox.showwarning("Warning", "Please enter text to translate.")
            return
        target_language_code = next(code for name, code in language_options if name == selected_translation_language.get())
        translated_text = translate_text(text, target_language=target_language_code)
        messagebox.showinfo("Translation Result", f"Translated Text: {translated_text}")

    tk.Button(translator_window, text="Translate", command=translate_and_display).pack(pady=20)

\
def generate_sentences_with_blanks():
    sentences_with_blanks = []
    correct_words = []
    
    words = generate_category_words(category_entry.get())  #get words ?
    if len(words) < 6:
        messagebox.showerror("Error", "The fill in the blank doesn't work. :(")
        return [], []

    verbs = random.sample(words, 2)
    nouns = random.sample(words, 2)
    adjectives = random.sample(words, 2)

    sentences_with_blanks.append(f"The {adjectives[0]} {nouns[0]} will {verbs[0]} quickly.")
    sentences_with_blanks.append(f"A {adjectives[1]} {nouns[1]} is going to {verbs[1]} soon.")

    correct_words.extend(verbs + nouns + adjectives)

    return sentences_with_blanks, correct_words

def open_fill_in_the_blank_game():
    print("Opening Fill in the Blank Game...")  # debugging
    fill_in_the_blank_window = tk.Toplevel(root)
    fill_in_the_blank_window.title("Fill in the Blank Game")

    
    sentences, correct_words = generate_sentences_with_blanks()

    if not sentences:
        print("No sentences generated.")  # debug
        return 

    tk.Label(fill_in_the_blank_window, text="Fill in the missing words!").pack(pady=10)

    entries = []
    for i, sentence in enumerate(sentences):
        tk.Label(fill_in_the_blank_window, text=f"{sentence}").pack(pady=5)
        entry = tk.Entry(fill_in_the_blank_window)
        entry.pack(pady=5)
        entries.append(entry)

    #shuffle
    shuffled_words = correct_words.copy()  
    print(f"Original Correct Words: {correct_words}")  
    random.shuffle(shuffled_words)  
    print(f"Shuffled Words: {shuffled_words}")  

    tk.Label(fill_in_the_blank_window, text="Word Bank:").pack(pady=10)
    tk.Label(fill_in_the_blank_window, text=", ".join(shuffled_words)).pack(pady=10)

    # submit + checking
    def check_fill_in_the_blank():
        correct_count = 0
        for i, entry in enumerate(entries):
            user_word = entry.get().strip()
            if user_word.casefold() == correct_words[i].casefold():
                correct_count += 1
        
        messagebox.showinfo("Game Result", f"You got {correct_count} out of {len(sentences)} correct!")

    tk.Button(fill_in_the_blank_window, text="Submit", command=check_fill_in_the_blank).pack(pady=20)


##### window stuff #####
root = tk.Tk()
root.title("TAMU Thematic Translator")
root.geometry("1200x900")

selected_language = tk.StringVar()

selected_difficulty = tk.StringVar()  

tk.Label(root, text="Enter a Category:").pack()
category_entry = tk.Entry(root)
category_entry.pack()

create_language_dropdown()
create_difficulty_dropdown() 

#buttons

tk.Button(root, text="Generate Words", command=on_category_selected).pack()

tk.Button(root, text="Reset", command=reset_game).pack()

tk.Button(root, text="Open Translator", command=open_translator).pack()

tk.Button(root, text="Play Fill in the Blank", command=open_fill_in_the_blank_game).pack()


matching_frame = tk.Frame(root)
matching_frame.pack()


root.mainloop()
