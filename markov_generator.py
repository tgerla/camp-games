import re
from collections import defaultdict, Counter
import random
import json

class MarkovTransitionGenerator:
    def __init__(self, order=1):
        """
        Initialize the Markov chain generator.
        
        Args:
            order (int): Order of the Markov chain (1 = current word, 2 = current 2 words, etc.)
        """
        self.order = order
        self.transitions = defaultdict(Counter)
        self.word_counts = Counter()
    
    def clean_text(self, text):
        """Clean and tokenize text into words, preserving sentence endings."""
        # Convert to lowercase and split into words, keeping sentence endings
        words = re.findall(r'\b[a-zA-Z]+\b|[.!?]', text.lower())
        return words
    
    def train(self, texts):
        """
        Train the Markov chain on input texts.
        
        Args:
            texts (list): List of text strings to analyze
        """
        all_words = []
        
        # Process each text
        for text in texts:
            words = self.clean_text(text)
            all_words.extend(words)
            
            # Build transitions based on order
            for i in range(len(words) - self.order):
                # Current state (1 or more words)
                if self.order == 1:
                    current_state = words[i]
                else:
                    current_state = tuple(words[i:i+self.order])
                
                next_word = words[i + self.order]
                
                # Record transition
                self.transitions[current_state][next_word] += 1
                self.word_counts[current_state] += 1
    
    def generate_dice_mapping(self, max_dice_sides=6):
        """
        Generate dice mappings for each state.
        
        Args:
            max_dice_sides (int): Maximum number of sides on dice to use
        
        Returns:
            dict: Mapping of states to dice roll outcomes
        """
        dice_mappings = {}
        
        for state, next_words in self.transitions.items():
            # Get most common next words
            common_words = next_words.most_common()
            
            # Determine how many dice sides we need
            num_outcomes = len(common_words)
            
            if num_outcomes <= max_dice_sides:
                # Use single die
                dice_mappings[state] = self._create_single_die_mapping(
                    common_words, max_dice_sides
                )
            else:
                # Use multiple dice or truncate to most common words
                truncated_words = common_words[:max_dice_sides]
                dice_mappings[state] = self._create_single_die_mapping(
                    truncated_words, max_dice_sides
                )
        
        return dice_mappings
    
    def _create_single_die_mapping(self, word_counts, die_sides):
        """Create a mapping of die rolls to words based on frequency."""
        total_count = sum(count for word, count in word_counts)
        
        # Calculate proportional dice assignments
        dice_mapping = {}
        current_roll = 1
        
        for word, count in word_counts:
            # Calculate how many sides this word should get
            proportion = count / total_count
            sides_for_word = max(1, round(proportion * die_sides))
            
            # Assign dice rolls to this word
            roll_range = []
            for _ in range(sides_for_word):
                if current_roll <= die_sides:
                    roll_range.append(current_roll)
                    current_roll += 1
            
            if roll_range:
                dice_mapping[word] = roll_range
        
        # Fill remaining sides with most common word if needed
        if current_roll <= die_sides:
            most_common_word = word_counts[0][0]
            remaining_sides = list(range(current_roll, die_sides + 1))
            if most_common_word in dice_mapping:
                dice_mapping[most_common_word].extend(remaining_sides)
            else:
                dice_mapping[most_common_word] = remaining_sides
        
        return dice_mapping
    
    def save_to_json(self, dice_mappings, filename="markov_transitions.json"):
        """Save dice mappings to JSON file."""
        # Convert tuples to strings for JSON serialization
        json_data = {}
        for state, mappings in dice_mappings.items():
            if isinstance(state, tuple):
                state_key = " ".join(state)
            else:
                state_key = state
            json_data[state_key] = mappings
        
        with open(filename, 'w') as f:
            json.dump(json_data, f, indent=2)
        
        print(f"Transition table saved to {filename}")
        return filename
    def print_transition_table(self, dice_mappings):
        """Print a formatted transition table for the exercise."""
        print("MARKOV CHAIN TRANSITION TABLE")
        print("=" * 50)
        print()
        
        for state, word_mappings in dice_mappings.items():
            if self.order == 1:
                print(f"If current word is '{state}':")
            else:
                state_str = " ".join(state)
                print(f"If current words are '{state_str}':")
            
            print("  Roll 1 die:")
            
            # Sort by dice values for cleaner presentation
            sorted_mappings = []
            for word, rolls in word_mappings.items():
                min_roll = min(rolls)
                max_roll = max(rolls)
                if min_roll == max_roll:
                    range_str = str(min_roll)
                else:
                    range_str = f"{min_roll}-{max_roll}"
                sorted_mappings.append((min_roll, range_str, word))
            
            sorted_mappings.sort()
            
            for _, range_str, word in sorted_mappings:
                if word == '.':
                    print(f"    {range_str} = 'END SENTENCE'")
                else:
                    print(f"    {range_str} = '{word}'")
            
            print()
    
    def generate_sample_story(self, dice_mappings, start_word=None, num_sentences=2):
        """Generate a sample story with complete sentences."""
        if not start_word:
            start_word = random.choice([k for k in dice_mappings.keys() if k != '.'])
        
        story_sentences = []
        current_state = start_word
        
        for sentence_num in range(num_sentences):
            sentence = []
            
            # Generate words until we hit a sentence ending
            while True:
                if self.order == 1:
                    if current_state != '.':  # Don't add periods to the sentence
                        sentence.append(current_state)
                else:
                    # For higher order, add words that aren't periods
                    for word in current_state:
                        if word != '.':
                            sentence.append(word)
                
                if current_state not in dice_mappings:
                    # If we can't continue, force a sentence ending
                    sentence.append('.')
                    break
                
                # Simulate dice roll
                word_mappings = dice_mappings[current_state]
                roll = random.randint(1, 6)
                
                # Find which word this roll corresponds to
                next_word = None
                for word, rolls in word_mappings.items():
                    if roll in rolls:
                        next_word = word
                        break
                
                if not next_word:
                    sentence.append('.')
                    break
                
                # Check if we've reached a sentence ending
                if next_word in ['.', '!', '?']:
                    sentence.append('.')
                    current_state = self._get_sentence_starter(dice_mappings)
                    break
                
                # Update current state
                if self.order == 1:
                    current_state = next_word
                else:
                    current_state = current_state[1:] + (next_word,)
            
            # Join the sentence and add to story
            if sentence:
                sentence_text = ' '.join(sentence)
                # Clean up spacing around periods
                sentence_text = sentence_text.replace(' .', '.')
                # Capitalize first word
                if sentence_text:
                    sentence_text = sentence_text[0].upper() + sentence_text[1:]
                story_sentences.append(sentence_text)
        
        return ' '.join(story_sentences)
    
    def _get_sentence_starter(self, dice_mappings):
        """Get a good word to start a new sentence."""
        # Look for common sentence starters
        starters = ['the', 'a', 'an', 'i', 'you', 'he', 'she', 'it', 'they', 'we']
        available_starters = [word for word in starters if word in dice_mappings]
        
        if available_starters:
            return random.choice(available_starters)
        else:
            # Fall back to any available word that's not a period
            non_period_words = [k for k in dice_mappings.keys() if k != '.']
            return random.choice(non_period_words) if non_period_words else 'the'

# Example usage
if __name__ == "__main__":
    # Sample texts designed for diverse transitions with sentence endings
    sample_texts = [
        "The camper was happy to make art and the camper was tired of swimming. The camper was excited to hike.",
        "The leader was happy to sleep and the leader was tired of art. The leader ran from bees.",
        "The weather was sunny. The weather was rainy. The weather was cloudy. The camper ran from friends.",
        "The food tastes good. The food tastes salty. The food tastes sweet. The food tastes fresh.", 
        "The river is deep. The river is shallow. The river is refreshing. The river tastes like worms.",
        "The river tastes like fish.", 
]
    
    # Create and train the generator
    generator = MarkovTransitionGenerator(order=1)
    generator.train(sample_texts)
    
    # Generate dice mappings
    dice_mappings = generator.generate_dice_mapping()
    
    # Save to JSON file
    json_filename = generator.save_to_json(dice_mappings)
    
    # Print the transition table
    generator.print_transition_table(dice_mappings)
    
    # Generate sample stories
    print("SAMPLE GENERATED STORIES:")
    print("=" * 30)
    for i in range(3):
        story = generator.generate_sample_story(dice_mappings, start_word="the", num_sentences=2)
        print(f"Story {i+1}: {story}")
    
    print("\n" + "=" * 50)
    print("INSTRUCTIONS FOR KIDS:")
    print("1. Start with 'the'")
    print("2. Find your current word in the table above")
    print("3. Roll a die and use the table to find your next word")
    print("4. Keep going until you roll a period (.) - that ends your sentence!")
    print("5. Start a new sentence with 'the' (or another starter word)")
    print("6. Write 2 complete sentences to make your story!")
    print("7. Compare stories with your friends!")
