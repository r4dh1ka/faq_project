from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("updated features.pdf", pagesize=letter)
styles = getSampleStyleSheet()

TitleStyle = styles['Heading1']
HeadingStyle = styles['Heading2']
BodyStyle = styles['BodyText']

story = []

story.append(Paragraph("Project Update Report: FAQ & Q&A Platform", TitleStyle))
story.append(Spacer(1, 12))

content = [
    ("H2", "1. Reddit-Style Threaded Q&A Architecture"),
    ("P", "- Nested Tree Structure: Upgraded the simple Q&A layout to a full Reddit-style threaded tree. Comments and replies can be infinitely nested."),
    ("P", "- Interactive Threadlines: Implemented visual vertical threadlines that connect parent comments to their children. These threadlines dynamically illuminate on hover."),
    ("P", "- Minimalist Action Bars: Replaced bulky UI buttons with classic horizontal action bars featuring inline upvote/downvote scores, reply buttons, and compressed inline avatar headers."),
    
    ("H2", "2. High-Concurrency Database Optimizations"),
    ("P", "- Scalability for 2000-3000 Users: Anticipating heavy concurrent usage, optimized the underlying database architecture to prevent performance bottlenecks."),
    ("P", "- N+1 Query Resolution: Heavily utilized Django's select_related and prefetch_related ORM methods in the views to ensure the complex nested comment trees can be queried and rendered in a single, highly efficient database trip."),
    
    ("H2", "3. YakshaBot AI Auto-Answer Integration (RAG)"),
    ("P", "- Instant AI Responses: Bridged the static FAQ database with the live Community Q&A. The moment a user posts a new question, the backend instantly runs a Retrieval-Augmented Generation (RAG) query against published FAQs."),
    ("P", "- Auto-Posting & Citations: If relevant context is found, a system profile named 'YakshaBot' automatically generates and posts the first answer to the question instantly, complete with hyperlinks citing the exact FAQ sources used."),
    ("P", "- Distinct AI Badging: Added custom robot avatars and 'AI' UI badges so users clearly recognize the response is automated.")
]

for style, text in content:
    if style == "H2":
        story.append(Paragraph(text, HeadingStyle))
        story.append(Spacer(1, 6))
    elif style == "P":
        story.append(Paragraph(text, BodyStyle))
        story.append(Spacer(1, 4))

doc.build(story)
print("PDF generated successfully with reportlab.")
