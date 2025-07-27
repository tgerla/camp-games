import json
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.platypus.frames import Frame
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import os

class MarkovPDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom styles for the PDF."""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=HexColor('#2E4057'),
            fontName='Helvetica-Bold'
        )
        
        # Subtitle style
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=HexColor('#048A81'),
            fontName='Helvetica-Bold'
        )
        
        # Section heading style
        self.section_style = ParagraphStyle(
            'SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=HexColor('#2E4057'),
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=HexColor('#048A81'),
            borderPadding=8,
            backColor=HexColor('#F0F8FF')
        )
        
        # Instructions style
        self.instructions_style = ParagraphStyle(
            'Instructions',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=8,
            leftIndent=20,
            fontName='Helvetica',
            textColor=HexColor('#333333')
        )
        
        # Word style for transitions
        self.word_style = ParagraphStyle(
            'WordStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Helvetica-Bold',
            textColor=HexColor('#2E4057'),
            spaceAfter=3,
            spaceBefore=8,
            borderWidth=1,
            borderColor=HexColor('#048A81'),
            backColor=HexColor('#F0F8FF'),
            borderPadding=4,
            alignment=TA_LEFT
        )
    
    def load_json_data(self, filename):
        """Load transition data from JSON file."""
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Could not find {filename}")
            return None
    
    def create_transition_table(self, state, mappings):
        """Create a nicely formatted table for a single state's transitions."""
        # Sort mappings by dice roll
        sorted_mappings = []
        for word, rolls in mappings.items():
            min_roll = min(rolls)
            max_roll = max(rolls)
            if min_roll == max_roll:
                range_str = str(min_roll)
            else:
                range_str = f"{min_roll}-{max_roll}"
            
            # Handle special cases
            if word == '.':
                display_word = 'END SENTENCE'
            else:
                display_word = word
            
            sorted_mappings.append((min_roll, range_str, display_word))
        
        sorted_mappings.sort()
        
        # Create table data
        table_data = [['Roll', 'Next Word']]
        for _, range_str, word in sorted_mappings:
            table_data.append([range_str, word])
        
        # Create table - smaller for two column layout
        table = Table(table_data, colWidths=[0.7*inch, 1.8*inch])
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#048A81')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            
            # Data rows
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#F8F9FA')),
            ('TEXTCOLOR', (0, 1), (-1, -1), black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            
            # Borders
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#CCCCCC')),
            ('LINEBELOW', (0, 0), (-1, 0), 2, HexColor('#048A81')),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#F8F9FA'), HexColor('#FFFFFF')])
        ]))
        
        return table
    
    def create_two_column_document(self, output_filename):
        """Create a two-column document template."""
        doc = BaseDocTemplate(
            output_filename,
            pagesize=letter,
            rightMargin=36,  # Reduced margins
            leftMargin=36,
            topMargin=72,
            bottomMargin=72
        )
        
        # Calculate frame dimensions for two columns
        frame_width = (letter[0] - 36*2 - 20) / 2  # 20pt gap between columns
        frame_height = letter[1] - 72*2
        
        # Create two frames (columns)
        left_frame = Frame(
            36, 72, frame_width, frame_height,
            leftPadding=10, rightPadding=10,
            topPadding=10, bottomPadding=10
        )
        
        right_frame = Frame(
            36 + frame_width + 20, 72, frame_width, frame_height,
            leftPadding=10, rightPadding=10,
            topPadding=10, bottomPadding=10
        )
        
        # Create page template with two columns
        two_column_template = PageTemplate(
            id='two_column',
            frames=[left_frame, right_frame]
        )
        
        # Single column template for title page
        single_frame = Frame(
            72, 72, letter[0] - 72*2, letter[1] - 72*2,
            leftPadding=20, rightPadding=20,
            topPadding=20, bottomPadding=20
        )
        
        single_column_template = PageTemplate(
            id='single_column',
            frames=[single_frame]
        )
        
        doc.addPageTemplates([single_column_template, two_column_template])
        return doc
    def generate_pdf(self, json_filename, output_filename="markov_exercise.pdf"):
        """Generate the complete PDF from JSON data."""
        # Load data
        data = self.load_json_data(json_filename)
        if not data:
            return
        
        # Create two-column document
        doc = self.create_two_column_document(output_filename)
        
        # Build story content
        story = []
        
        # Title page (single column)
        story.append(Paragraph("Markov Chain Story Generator", self.title_style))
        story.append(Spacer(1, 20))
        story.append(Paragraph("A Fun Probability Exercise", self.subtitle_style))
        story.append(Spacer(1, 40))
        
        # Introduction
        intro_text = """
        Welcome to the Markov Chain Story Generator! This exercise teaches you about probability 
        and how computers can generate text. You'll use dice rolls to create unique stories by 
        following probability rules, just like how large language models work!
        """
        story.append(Paragraph(intro_text, self.instructions_style))
        story.append(Spacer(1, 30))
        
        # Instructions
        story.append(Paragraph("How to Play:", self.section_style))
        
        instructions = [
            "1. Start with the word 'the'",
            "2. Find your current word in the transition tables",
            "3. Roll a six-sided die",
            "4. Use the dice roll to find your next word",
            "5. Keep rolling until you get 'END SENTENCE'",
            "6. Start sentence 2 with 'the' or another starter",
            "7. Continue until you have two complete sentences",
            "8. Read your story aloud and compare!"
        ]
        
        for instruction in instructions:
            story.append(Paragraph(instruction, self.instructions_style))
        
        story.append(Spacer(1, 20))
        
        # Example
        story.append(Paragraph("Example Story:", self.section_style))
        example_text = """
        <i>"The cat ran home. The dog played outside."</i><br/><br/>
        Notice how each sentence is complete!
        """
        story.append(Paragraph(example_text, self.instructions_style))
        
        # Switch to two-column layout for transition tables
        story.append(PageBreak())
        
        # Transition tables header
        story.append(Paragraph("Transition Tables", self.title_style))
        story.append(Spacer(1, 15))
        
        # Sort states - put "the" first, then alphabetical
        sorted_states = sorted([k for k in data.keys() if k != "the" and k != "."])
        if "the" in data:
            sorted_states.insert(0, "the")
        sorted_states = [state for state in sorted_states if state != "."]
        
        # Create transition tables for two-column layout
        for state in sorted_states:
            mappings = data[state]
            
            # Create a keep-together group for each word and its table
            elements = []
            
            # State header with better visual separation
            state_header = f"Current word: <b>'{state}'</b>"
            elements.append(Paragraph(state_header, self.word_style))
            elements.append(Spacer(1, 3))
            
            # Create transition table
            table = self.create_transition_table(state, mappings)
            elements.append(table)
            
            # Add horizontal rule after each word section
#            elements.append(Spacer(1, 5))
#            elements.append(HRFlowable(width="100%", thickness=1, 
#                                    color=HexColor('#CCCCCC'), 
#                                    spaceBefore=2, spaceAfter=8))
            
            # Keep each word and its table together
            story.append(KeepTogether(elements))
        
        # Extension activities (single column)
        story.append(PageBreak())
        story.append(Paragraph("Extension Activities", self.title_style))
        story.append(Spacer(1, 20))
        
        activities = [
            "<b>Story Comparison:</b> Compare stories with classmates",
            "<b>Pattern Recognition:</b> Which words appear together?",
            "<b>Probability Discussion:</b> Why some transitions more common?",
            "<b>Creative Writing:</b> Try different starting words",
            "<b>Math Connection:</b> Count and graph word frequencies",
            "<b>Real-World:</b> How is this like predictive text?"
        ]
        
        for activity in activities:
            story.append(Paragraph(activity, self.instructions_style))
            story.append(Spacer(1, 8))
        
        # Build PDF
        doc.build(story)
        print(f"PDF generated successfully: {output_filename}")
        return output_filename

def main():
    """Main function to generate PDF from JSON file."""
    generator = MarkovPDFGenerator()
    
    # Look for JSON file
    json_files = [f for f in os.listdir('.') if f.endswith('.json') and 'markov' in f.lower()]
    
    if not json_files:
        print("No Markov JSON files found. Please run the transition generator first.")
        return
    
    # Use the first JSON file found
    json_filename = json_files[0]
    print(f"Using JSON file: {json_filename}")
    
    # Generate PDF
    pdf_filename = generator.generate_pdf(json_filename)
    print(f"PDF ready for printing: {pdf_filename}")

if __name__ == "__main__":
    main()
