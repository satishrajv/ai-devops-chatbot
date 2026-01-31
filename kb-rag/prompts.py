"""
Centralized Prompts for RAG Chatbot
All LLM system prompts and templates in one place
"""

# ============================================
# SYSTEM PROMPTS
# ============================================

SYSTEM_PROMPT_DEVOPS_ASSISTANT = """You are a helpful DevOps assistant specializing in Jenkins and CI/CD troubleshooting.

Your expertise includes:
- Jenkins build failures and errors
- Docker container issues
- CI/CD pipeline optimization
- Memory management (OOM errors)
- Infrastructure troubleshooting
- Best practices for DevOps

Guidelines:
- Provide clear, actionable answers based on the documentation provided
- Use step-by-step instructions when explaining fixes
- Include specific commands or code examples when relevant
- If the answer is not in the documentation, say so honestly
- Focus on practical solutions that can be implemented immediately
"""

# ============================================
# ANSWER GENERATION PROMPTS
# ============================================

ANSWER_GENERATION_TEMPLATE = """Use the following documentation to answer the user's question.

Documentation:
{context}

User Question: {question}

Instructions:
- Provide a clear, step-by-step answer if applicable
- Use bullet points or numbered lists for clarity
- Include specific commands or code examples if relevant
- Cite which document(s) you used
- If the answer is not in the documentation, say so
- Keep your answer focused and relevant to the question
- Use markdown formatting for better readability

Answer:"""

# ============================================
# FALLBACK PROMPTS
# ============================================

FALLBACK_NO_CONTEXT_MESSAGE = """I couldn't find specific information about that in the knowledge base.

This could mean:

1. **The topic hasn't been documented yet** - Consider adding this to the knowledge base

**Suggestions:**
- Ask about Jenkins errors, Docker issues, or CI/CD troubleshooting


Would you like to ask something else about Jenkins, Docker, or CI/CD?"""

# ============================================
# QUERY PROCESSING PROMPTS
# ============================================

# Currently query processing doesn't use LLM prompts
# But we can add query expansion/refinement in the future

QUERY_EXPANSION_TEMPLATE = """Given the user's question, generate 2-3 alternative phrasings that might help find relevant information.

Original Question: {question}

Alternative Phrasings (one per line):"""

# ============================================
# EVALUATION PROMPTS
# ============================================

ANSWER_QUALITY_EVALUATION_TEMPLATE = """Evaluate the quality of this answer based on the question and context.

Question: {question}

Context Used:
{context}

Generated Answer:
{answer}

Rate the answer on:
1. Relevance (0-10): Does it answer the question?
2. Completeness (0-10): Does it provide enough detail?
3. Accuracy (0-10): Is the information correct based on context?

Provide scores in JSON format:
{{"relevance": X, "completeness": Y, "accuracy": Z}}"""

# ============================================
# CUSTOM TEMPLATES FOR SPECIFIC USE CASES
# ============================================

# Template for troubleshooting questions
TROUBLESHOOTING_TEMPLATE = """You are helping diagnose a technical issue.

Problem Description: {question}

Relevant Documentation:
{context}

Provide a structured troubleshooting guide:

**Diagnosis:**
- What is likely causing this issue?

**Solution:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Prevention:**
- How to prevent this in the future

**References:**
- Cite relevant documentation"""

# Template for "how to" questions
HOW_TO_TEMPLATE = """You are providing step-by-step instructions.

Task: {question}

Relevant Documentation:
{context}

Provide clear, actionable instructions:

**Prerequisites:**
- What you need before starting

**Steps:**
1. [Detailed step 1]
2. [Detailed step 2]
3. [Detailed step 3]

**Verification:**
- How to verify it worked

**Common Issues:**
- Potential problems and solutions"""

# Template for "what is" questions
EXPLANATION_TEMPLATE = """You are explaining a technical concept.

Topic: {question}

Relevant Documentation:
{context}

Provide a clear explanation:

**Overview:**
- Brief introduction to the topic

**Key Concepts:**
- Main points to understand

**Example:**
- Practical example if applicable

**Related Topics:**
- Other relevant areas to explore"""

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_prompt_template(question_type: str = "default") -> str:
    """
    Get the appropriate prompt template based on question type

    Args:
        question_type: Type of question ("troubleshooting", "how_to", "explanation", "default")

    Returns:
        Prompt template string
    """
    templates = {
        "troubleshooting": TROUBLESHOOTING_TEMPLATE,
        "how_to": HOW_TO_TEMPLATE,
        "explanation": EXPLANATION_TEMPLATE,
        "default": ANSWER_GENERATION_TEMPLATE
    }

    return templates.get(question_type, ANSWER_GENERATION_TEMPLATE)


def detect_question_type(question: str) -> str:
    """
    Detect the type of question to use appropriate template

    Args:
        question: User's question

    Returns:
        Question type ("troubleshooting", "how_to", "explanation", "default")
    """
    question_lower = question.lower()

    # Troubleshooting indicators
    if any(word in question_lower for word in ["error", "failure", "failed", "issue", "problem", "fix", "troubleshoot"]):
        return "troubleshooting"

    # How-to indicators
    if any(word in question_lower for word in ["how to", "how do i", "how can i", "steps to", "guide"]):
        return "how_to"

    # Explanation indicators
    if any(word in question_lower for word in ["what is", "what are", "explain", "define", "meaning of"]):
        return "explanation"

    return "default"


def format_prompt(template: str, **kwargs) -> str:
    """
    Format a prompt template with provided variables

    Args:
        template: Prompt template string with {placeholders}
        **kwargs: Variables to fill in the template

    Returns:
        Formatted prompt string
    """
    return template.format(**kwargs)


# ============================================
# EXAMPLE USAGE
# ============================================

if __name__ == "__main__":
    # Example: Format answer generation prompt
    context = "OutOfMemoryError occurs when Docker containers exceed memory limits..."
    question = "What causes OutOfMemoryError?"

    prompt = format_prompt(
        ANSWER_GENERATION_TEMPLATE,
        context=context,
        question=question
    )

    print("Generated Prompt:")
    print("="*60)
    print(prompt)
    print("="*60)

    # Example: Detect question type
    questions = [
        "What causes OutOfMemoryError?",
        "How do I fix Jenkins build failures?",
        "What is Docker?",
        "Jenkins build failed with error 500"
    ]

    print("\nQuestion Type Detection:")
    print("="*60)
    for q in questions:
        q_type = detect_question_type(q)
        print(f"{q}")
        print(f"  → Type: {q_type}\n")
