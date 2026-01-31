# Centralized Prompts Management

Complete guide to managing and customizing LLM prompts in the RAG chatbot.

## Overview

All LLM prompts are centralized in `prompts.py` for easy:
- ✅ **Version Control** - Track prompt changes in git
- ✅ **A/B Testing** - Compare different prompt versions
- ✅ **Customization** - Modify prompts without touching agent code
- ✅ **Consistency** - Same prompts across all agents
- ✅ **Documentation** - Clear examples and templates

## File Structure

```
kb-rag/
├── prompts.py                  # ← All prompts stored here
├── agents/
│   └── answer_generator.py    # ← Imports prompts from prompts.py
├── config.py                   # ← Model settings (temperature, etc.)
└── PROMPTS_README.md          # ← This file
```

## Available Prompts

### 1. System Prompt

**Variable**: `SYSTEM_PROMPT_DEVOPS_ASSISTANT`

**Purpose**: Defines the AI assistant's role and expertise

**Current Content**:
```python
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
```

**When to Modify**:
- Change the assistant's expertise area
- Add new guidelines for responses
- Adjust tone or formality

---

### 2. Answer Generation Template

**Variable**: `ANSWER_GENERATION_TEMPLATE`

**Purpose**: Main template for generating answers with retrieved context

**Placeholders**:
- `{context}` - Retrieved document chunks
- `{question}` - User's question

**Current Content**:
```python
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
```

**When to Modify**:
- Change answer format/structure
- Add specific instructions for citing sources
- Adjust level of detail in answers

---

### 3. Fallback Message

**Variable**: `FALLBACK_NO_CONTEXT_MESSAGE`

**Purpose**: Message when no relevant documents found

**Current Content**:
```python
FALLBACK_NO_CONTEXT_MESSAGE = """I couldn't find specific information about that in the knowledge base.

This could mean:

1. **The topic hasn't been documented yet** - Consider adding this to the knowledge base
2. **Try rephrasing your question** - Use different keywords or be more specific
3. **The information might be in a different section** - Try asking about related topics

**Suggestions:**
- Ask about Jenkins errors, Docker issues, or CI/CD troubleshooting
- Use specific error messages or symptoms in your question
- Try asking "What causes [specific error]?" or "How do I fix [specific problem]?"

Would you like to ask something else about Jenkins, Docker, or CI/CD?"""
```

**When to Modify**:
- Change suggestions for users
- Add links to documentation
- Adjust helpfulness level

---

### 4. Specialized Templates

#### Troubleshooting Template

**Variable**: `TROUBLESHOOTING_TEMPLATE`

**Purpose**: Structured format for debugging questions

**Auto-triggered when**: Question contains "error", "failure", "issue", "problem", "fix"

**Format**:
- Diagnosis section
- Solution steps (numbered)
- Prevention tips
- References

#### How-To Template

**Variable**: `HOW_TO_TEMPLATE`

**Purpose**: Step-by-step instructions

**Auto-triggered when**: Question contains "how to", "how do i", "steps to"

**Format**:
- Prerequisites
- Detailed steps
- Verification
- Common issues

#### Explanation Template

**Variable**: `EXPLANATION_TEMPLATE`

**Purpose**: Concept explanations

**Auto-triggered when**: Question contains "what is", "explain", "define"

**Format**:
- Overview
- Key concepts
- Example
- Related topics

---

## How It Works

### Automatic Template Selection

The system automatically detects question type:

```python
from prompts import detect_question_type, get_prompt_template

question = "How do I fix Jenkins build failures?"

# Auto-detect type
question_type = detect_question_type(question)  # Returns: "troubleshooting"

# Get appropriate template
template = get_prompt_template(question_type)   # Returns: TROUBLESHOOTING_TEMPLATE
```

### Question Type Detection

```python
# Troubleshooting questions
"What causes OutOfMemoryError?"          → troubleshooting
"Jenkins build failed"                   → troubleshooting
"Error 500 in pipeline"                  → troubleshooting

# How-to questions
"How do I configure Jenkins?"            → how_to
"Steps to deploy Docker container"       → how_to
"How can I optimize my pipeline?"        → how_to

# Explanation questions
"What is Jenkins?"                       → explanation
"Explain Docker networking"              → explanation
"What are CI/CD pipelines?"              → explanation

# Default
"Tell me about Jenkins"                  → default
```

---

## Customization Guide

### Example 1: Change System Prompt

**Scenario**: You want the assistant to be more technical

```python
# In prompts.py

SYSTEM_PROMPT_DEVOPS_ASSISTANT = """You are an advanced DevOps engineer specializing in Jenkins and CI/CD.

Your expertise:
- Deep Jenkins internals and Groovy scripting
- Advanced Docker networking and orchestration
- Kubernetes integration with CI/CD
- Performance optimization and scaling
- Security best practices

Communication style:
- Use technical terminology
- Provide detailed explanations with code examples
- Reference official documentation
- Assume user has intermediate DevOps knowledge
"""
```

**Result**: Answers become more technical and detailed

---

### Example 2: Add Code Block Formatting

**Scenario**: Enforce code blocks in all answers

```python
# In prompts.py

ANSWER_GENERATION_TEMPLATE = """Use the following documentation to answer the user's question.

Documentation:
{context}

User Question: {question}

Instructions:
- Provide a clear, step-by-step answer
- **IMPORTANT**: Wrap all commands in code blocks using ```bash
- **IMPORTANT**: Wrap all config/code in appropriate code blocks
- Use bullet points for lists
- Cite which document(s) you used

Example format:
To fix this issue:
1. Run the following command:
```bash
docker restart jenkins
```

2. Update your config:
```yaml
memory: 2GB
```

Answer:"""
```

**Result**: All answers now include properly formatted code blocks

---

### Example 3: Custom Fallback for Specific Topics

**Scenario**: Redirect Kubernetes questions to different KB

```python
# In prompts.py

def get_custom_fallback(question: str) -> str:
    """Generate custom fallback based on question topic"""

    if "kubernetes" in question.lower() or "k8s" in question.lower():
        return """I couldn't find Kubernetes information in this knowledge base.

This knowledge base focuses on Jenkins and Docker. For Kubernetes questions:
- Visit the Kubernetes KB at: http://kb.example.com/kubernetes
- Or ask in #kubernetes Slack channel

Would you like to ask about Jenkins or Docker instead?"""

    # Default fallback
    return FALLBACK_NO_CONTEXT_MESSAGE


# Update answer_generator.py to use this
```

---

### Example 4: Add Citation Requirements

**Scenario**: Force exact document citations

```python
# In prompts.py

ANSWER_GENERATION_TEMPLATE = """Use the following documentation to answer the user's question.

Documentation:
{context}

User Question: {question}

**CRITICAL INSTRUCTIONS:**
1. Provide step-by-step answer
2. **You MUST cite sources** using this exact format:
   > According to [Document Name], ...

3. Include document name in square brackets for every fact
4. Use bullet points for clarity
5. If answer not in docs, say "This information is not available in the provided documentation."

**Example of required citation format:**
> According to [jenkins-error-kb-001-outofmemory.md], OutOfMemoryError occurs when...

Answer:"""
```

**Result**: All answers include explicit document citations

---

## Testing Prompts

### Manual Testing

```bash
cd C:\code\AI-DevOps-chatbot\kb-rag
venv\Scripts\activate
python prompts.py
```

This runs example usage showing:
- Template formatting
- Question type detection
- Prompt generation

### Testing in Chatbot

```python
# Test specific template
from prompts import get_prompt_template, format_prompt

template = get_prompt_template("troubleshooting")
prompt = format_prompt(template,
    question="Jenkins build failed with OOM",
    context="Memory limit is 1GB..."
)

print(prompt)
```

---

## Version Control Best Practices

### 1. Document Changes

```python
# prompts.py

# Version: 2.1
# Last Updated: 2026-01-24
# Changes: Added code block requirements to ANSWER_GENERATION_TEMPLATE

ANSWER_GENERATION_TEMPLATE = """..."""
```

### 2. A/B Testing

```python
# prompts.py

# Version A (Current)
ANSWER_GENERATION_TEMPLATE_V1 = """..."""

# Version B (Experimental)
ANSWER_GENERATION_TEMPLATE_V2 = """..."""

# Select version
ANSWER_GENERATION_TEMPLATE = ANSWER_GENERATION_TEMPLATE_V1
```

### 3. Git Commits

```bash
git add kb-rag/prompts.py
git commit -m "Update system prompt to be more technical"
```

---

## Integration with Config

Prompts work with `config.py` settings:

```python
# config.py controls model behavior
TEMPERATURE = 0.3      # How creative (0=precise, 1=creative)
LLM_MODEL = "gpt-4o-mini"

# prompts.py controls what the model is asked
SYSTEM_PROMPT_DEVOPS_ASSISTANT = """..."""
```

**Rule of Thumb**:
- Change `config.py` to adjust **HOW** the model responds (creativity, length)
- Change `prompts.py` to adjust **WHAT** the model is asked to do (format, style)

---

## Advanced Features

### Dynamic Prompt Generation

```python
# prompts.py

def generate_dynamic_prompt(question: str, context: str, user_level: str = "intermediate") -> str:
    """Generate prompt based on user expertise level"""

    if user_level == "beginner":
        instructions = """
        - Use simple language
        - Explain technical terms
        - Provide detailed step-by-step instructions
        - Include screenshots references
        """
    elif user_level == "expert":
        instructions = """
        - Use technical terminology
        - Focus on architecture and best practices
        - Assume familiarity with DevOps tools
        - Provide optimization tips
        """
    else:  # intermediate
        instructions = """
        - Balance technical and accessible language
        - Provide clear steps with explanations
        - Include relevant examples
        """

    return f"""Use the following documentation to answer the question.

Documentation:
{context}

User Question: {question}

Instructions:
{instructions}

Answer:"""
```

### Multi-Language Support

```python
# prompts.py

SYSTEM_PROMPTS = {
    "en": "You are a helpful DevOps assistant...",
    "es": "Eres un asistente de DevOps útil...",
    "fr": "Vous êtes un assistant DevOps utile..."
}

def get_system_prompt(language: str = "en") -> str:
    return SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS["en"])
```

---

## Troubleshooting

### Error: "No module named 'prompts'"

**Solution**: Make sure `prompts.py` is in the `kb-rag/` directory

### Prompts not being used

**Check**:
1. `answer_generator.py` imports from `prompts.py`
2. Restart Streamlit app after changing prompts
3. Check logs for prompt content

### Testing prompt changes

```python
# Quick test script
from prompts import *

question = "What causes OOM errors?"
context = "Memory limits..."

template = get_prompt_template(detect_question_type(question))
prompt = format_prompt(template, question=question, context=context)

print(prompt)
```

---

## Summary

**Centralized Prompts System**:
- ✅ All prompts in `prompts.py`
- ✅ Auto-detect question type
- ✅ Specialized templates (troubleshooting, how-to, explanation)
- ✅ Easy to modify and version control
- ✅ Consistent across entire chatbot

**Quick Reference**:

| Prompt | File | Variable |
|--------|------|----------|
| System prompt | prompts.py | `SYSTEM_PROMPT_DEVOPS_ASSISTANT` |
| Answer template | prompts.py | `ANSWER_GENERATION_TEMPLATE` |
| Fallback message | prompts.py | `FALLBACK_NO_CONTEXT_MESSAGE` |
| Troubleshooting | prompts.py | `TROUBLESHOOTING_TEMPLATE` |
| How-to guide | prompts.py | `HOW_TO_TEMPLATE` |
| Explanation | prompts.py | `EXPLANATION_TEMPLATE` |

**To Modify Prompts**:
1. Edit `kb-rag/prompts.py`
2. Update the relevant template variable
3. Restart Streamlit app
4. Test with example questions

**Best Practices**:
- Document changes with version comments
- Test prompts before deploying
- Use git to track prompt evolution
- Keep prompts clear and specific
- Avoid overly complex instructions

🚀 Your prompts are now centralized and easy to manage!
