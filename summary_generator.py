import streamlit as st
import fitz  # PyMuPDF
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

nltk.download('punkt')
nltk.download('stopwords')

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text

# Function to calculate TF-IDF scores
def tfidf_scores(sentences, topic):
    vectorizer = TfidfVectorizer(stop_words='english')
    vectors = vectorizer.fit_transform(sentences)
    words = vectorizer.get_feature_names_out()
    
    topic_vector = vectorizer.transform([topic])
    topic_words = set()
    for idx, val in enumerate(topic_vector.todense().tolist()[0]):
        if val > 0:
            topic_words.add(words[idx])
    
    sentence_scores = {}
    for i, sentence in enumerate(sentences):
        score = sum(vectors[i, vectorizer.vocabulary_[word]] for word in topic_words)
        sentence_scores[sentence] = score
    
    return sentence_scores

# Function to summarize text based on TF-IDF scores
def summarize_text(text, topic, num_sentences=8):
    stop_words = set(stopwords.words('english'))
    sentences = sent_tokenize(text)
    
    sentence_scores = tfidf_scores(sentences, topic)
    
    sorted_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
    
    summary_sentences = [sentence for sentence, score in sorted_sentences[:num_sentences]]
    
    summary = '\n'.join(f"• {sent}" for sent in summary_sentences)
    
    return summary

# Function to save summary to PDF
def save_summary_to_pdf(summary_text, topic, output_file):
    c = canvas.Canvas(output_file, pagesize=letter)
    c.setFont("Helvetica", 16)
    c.drawString(50, 750, "Summary")

    c.setFont("Helvetica", 12)
    c.drawString(50, 730, f"Topic: {topic}")
    
    c.setFont("Helvetica", 12)
    text_lines = summary_text.split('\n')
    y = 700  # Adjust starting y-coordinate for text content
    for line in text_lines:
        c.drawString(50, y, line)
        y -= 15  # Adjust vertical spacing
    c.save()

# Main Streamlit function
def summary_generator():
    # Custom CSS to change background color
    st.markdown(
        """
        <style>
        .stApp {
            background-color: 7091E6;
        }
        header, .stButton > button {
            background-color: #9cc3d5ff;
        }
        .stButton > button {
            color: ;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("PDF Summarizer")
    st.write("Welcome to the PDF Summarizer!")
    
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
    if uploaded_file is not None:
        topic = st.text_input("Enter the topic you want summarized", "")
        if st.button("Summarize"):
            try:
                # Save the uploaded PDF file
                with open("temp_pdf.pdf", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                    
                # Extract text from the PDF
                text = extract_text_from_pdf("temp_pdf.pdf")
                
                # Summarize text based on the topic
                summary = summarize_text(text, topic)
                
                # Save summary to PDF
                output_pdf = f"{topic}_summary.pdf"
                save_summary_to_pdf(summary, topic, output_pdf)
                
                # Display success message and provide download link
                st.success(f"Summary saved to {output_pdf}")
                st.markdown(f"Download [summary PDF]({output_pdf})")
                
            except Exception as e:
                st.error(f"Error: {e}")
