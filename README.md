# Markov Chain Story Generator

A fun educational tool that teaches kids about probability and language modeling through dice-based story generation. Students roll dice to create unique stories following Markov chain transitions, providing hands-on experience with the concepts behind large language models.

## Prerequisites

This project uses `uv` for fast Python package management. You'll need Python 3.8+ installed on your system.

## Installation

### 1. Install uv

**On macOS and Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**On Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Alternative (using pip):**
```bash
pip install uv
```

### 2. Set up the Python environment

```bash
# Set up the Python environment
uv sync 
```

## Customizing Input Text

To modify the stories your Markov chain will generate, edit the `sample_texts` list in the first script (`markov_generator.py`):

```python
sample_texts = [
    # Add your custom sentences here
    "The cat ran home. The cat walked home. The cat jumped home.",
    "The dog played outside. The dog ran outside. The dog slept outside.",
    # ... add more variations
]
```

### Tips for Good Input Text:

- **Use repetitive patterns** with variations (same structure, different words)
- **Include sentence endings** (periods) so the system knows when to end sentences
- **Create multiple examples** of each pattern to give students more choices
- **Keep vocabulary simple** and age-appropriate
- **Use parallel structures** like "The [animal] [verb] [location]"

### Example patterns that work well:

```python
sample_texts = [
    # Animal actions
    "The cat ran quickly. The dog ran slowly. The bird ran nowhere.",
    "The mouse was happy. The mouse was sad. The mouse was excited.",
    
    # Daily activities  
    "I like pizza. I like cookies. I like ice cream.",
    "We go to school. We go to work. We go to bed.",
    
    # Story templates
    "The hero found treasure. The hero found danger. The hero found friends.",
]
```

## Running the Scripts

### Step 1: Generate the Transition Table

Run the first script to analyze your input text and create the JSON transition file:

```bash
uv run markov_generator.py
```

This will:
- Analyze your input texts
- Generate probability-based dice mappings
- Save transitions to `markov_transitions.json`
- Print a preview of the transition table
- Show sample generated stories

### Step 2: Create the PDF

Run the second script to generate a beautiful, printable PDF:

```bash
uv run pdf_generator.py
```

This will:
- Load the `markov_transitions.json` file
- Create a professional two-column PDF layout
- Save as `markov_exercise.pdf`
- Include instructions, transition tables, and extension activities

## Output Files

After running both scripts, you'll have:

- **`markov_transitions.json`** - Raw transition data (for debugging/inspection)
- **`markov_exercise.pdf`** - Printer-ready classroom handout

## How Students Use the Exercise

1. **Start with 'the'** (always the first word)
2. **Find current word** in the transition tables
3. **Roll a die** and look up the result
4. **Write the next word** based on dice roll
5. **Continue until "END SENTENCE"** completes the first sentence  
6. **Start sentence 2** with 'the' or another starter word
7. **Create two complete sentences** to form a story
8. **Compare stories** with classmates!

## Troubleshooting

**"No module named 'reportlab'"**
```bash
uv add reportlab
```

**"No Markov JSON files found"**
- Make sure you ran `python markov_generator.py` first
- Check that `markov_transitions.json` exists in the same directory

**PDF looks crowded**
- Reduce the number of input texts
- Simplify your vocabulary to create fewer unique words

**Too many single-choice transitions**
- Add more variety to your input texts
- Use the repetitive pattern examples above
- Make sure you have multiple examples of each sentence structure

## Educational Extensions

The PDF includes several extension activities:
- Story comparison and analysis
- Pattern recognition exercises  
- Probability discussions
- Creative writing variations
- Math connections (graphing word frequencies)
- Real-world connections to predictive text

## Learning Objectives

Students will understand:
- Basic probability concepts
- How current state influences future outcomes
- Pattern recognition in language
- Foundations of how AI language models work
- The role of randomness in text generation

---

*Happy story generating! 🎲📖*
