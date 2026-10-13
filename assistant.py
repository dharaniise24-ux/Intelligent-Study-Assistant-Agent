import os
from dotenv import load_dotenv
from google import genai

# Load environment variable from .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)
MODEL_NAME = "gemini-3.5-flash-lite"


# ==========================================
# 1. PROMPT ENGINEERING TECHNIQUES
# ==========================================

def zero_shot_prompt(topic: str) -> str:
    """Zero-shot: Direct task instruction without examples."""
    prompt = f"Explain the concept of '{topic}' in simple terms for a beginner computer science student."
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    return response.text


def few_shot_prompt(unformatted_query: str) -> str:
    """Few-shot: Providing in-context input-output examples."""
    prompt = f"""Transform student queries into structured revision flashcards with Concept, Definition, and Quick Example.

Example 1:
Query: What is recursion?
Flashcard:
- Concept: Recursion
- Definition: A method where a function calls itself to solve a smaller instance of the problem.
- Quick Example: Calculating factorial (n! = n * (n-1)!).

Example 2:
Query: What is encapsulation?
Flashcard:
- Concept: Encapsulation
- Definition: Bundling data and methods into a single unit and restricting direct access to object internals.
- Quick Example: Private class attributes accessed via getter and setter methods.

Query: {unformatted_query}
Flashcard:"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    return response.text


def role_prompt(question: str) -> str:
    """Role Prompting: System instructions assigning an academic mentor persona."""
    config = {
        "system_instruction": (
            "You are an encouraging, expert university Professor and Academic Mentor. "
            "Break down complex academic queries into clear explanations, use intuitive analogies, "
            "highlight common pitfalls students make, and end with a quick check-for-understanding question."
        )
    }
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=question,
        config=config
    )
    return response.text


# ==========================================
# 2. INTELLIGENT FAQ ASSISTANT
# ==========================================

FAQ_KNOWLEDGE_BASE = """
[Course: CS101 - Introduction to Programming & Algorithms]
1. Grading Scheme: 30% Midterms, 40% Final Exam, 20% Lab Assignments, 10% Attendance/Quizzes.
2. Assignment Submission: All code must be submitted via the university LMS before Sunday 11:59 PM. Late penalty is 10% per day.
3. Office Hours: Dr. Sharma's office hours are Tuesdays and Thursdays from 2:00 PM to 4:00 PM in Room 402.
4. Lab Policy: Students must complete all lab activity sheets individually unless group work is explicitly noted.
5. Recommended Textbook: "Introduction to Algorithms" by Cormen et al. (CLRS).
"""

def intelligent_faq_assistant(student_query: str) -> str:
    """Intelligent FAQ agent grounded on course rules."""
    config = {
        "system_instruction": (
            "You are the Intelligent Academic FAQ Assistant for CS101. "
            "Answer the student's question accurately using ONLY the provided course knowledge base below. "
            "If the answer is not contained in the knowledge base, state clearly that the information "
            "is not in the course guide and instruct them to contact the teaching assistant.\n\n"
            f"KNOWLEDGE BASE:\n{FAQ_KNOWLEDGE_BASE}"
        )
    }
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=student_query,
        config=config
    )
    return response.text


# ==========================================
# 3. INTERACTIVE CLI RUNNER
# ==========================================

def main():
    while True:
        print("\n" + "=" * 55)
        print("STUDY ASSISTANT & FAQ AGENT MENU")
        print("=" * 55)
        print("1. Zero-shot Prompting (Quick Concept Explainer)")
        print("2. Few-shot Prompting (Generate Study Flashcard)")
        print("3. Role Prompting (Ask Academic Mentor/Professor)")
        print("4. Intelligent FAQ Assistant (Course Rules & Policies)")
        print("5. Exit")
        
        choice = input("\nSelect an option (1-5): ").strip()
        
        if choice == "1":
            topic = input("Enter a topic to explain (e.g., 'Binary Search Tree'): ")
            print("\n--- Assistant Output ---")
            print(zero_shot_prompt(topic))
            
        elif choice == "2":
            query = input("Enter a concept for a flashcard (e.g., 'What is Polymorphism?'): ")
            print("\n--- Assistant Output ---")
            print(few_shot_prompt(query))
            
        elif choice == "3":
            question = input("Ask the Mentor a question: ")
            print("\n--- Assistant Output ---")
            print(role_prompt(question))
            
        elif choice == "4":
            faq_q = input("Ask a course FAQ question (e.g., 'What happens if I submit late?'): ")
            print("\n--- Assistant Output ---")
            print(intelligent_faq_assistant(faq_q))
            
        elif choice == "5":
            print("Exiting assistant. Goodbye!")
            break
        else:
            print("Invalid selection. Please choose 1 to 5.")

if __name__ == "__main__":
    main()