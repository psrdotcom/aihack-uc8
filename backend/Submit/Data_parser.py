import re
import csv
from docx import Document

# Step 1: Read DOCX text
def read_docx_text(file_path):
    doc = Document(file_path)
    return "\n".join(p.text for p in doc.paragraphs)

# Step 2: Extract articles using regex
def extract_articles(text):
    pattern = re.compile(
        r'Title:\s*(.*?)\s*Source:\s*(.*?)\s*Date:\s*(.*?)\s*(?=(?:\d{1,2}\)|Title:)|\Z)',
        re.DOTALL
    )
    matches = pattern.findall(text)
    articles = []
    for match in matches:
        title = match[0].strip()
        source = match[1].strip()
        date_parts = match[2].strip().split("\n", 1)
        date = date_parts[0].strip()
        content = date_parts[1].strip() if len(date_parts) > 1 else ""
        articles.append([title, source, date, content])
    return articles

# Step 3: Save to CSV
def save_to_csv(articles, csv_path):
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Source", "Date", "Body"])
        writer.writerows(articles)

# Usage
docx_file = "D:\\Hackathon\\aihack-uc8\\backend\\MixedArticles _SameArticle_DiffSources.docx"  # your input DOCX file
csv_file = "articles_parsed.csv"       # output CSV file

text = read_docx_text(docx_file)
articles = extract_articles(text)
save_to_csv(articles, csv_file)

print(f"✅ Extracted {len(articles)} articles to {csv_file}")
