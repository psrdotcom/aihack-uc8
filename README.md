# UC8 Outcome Agents Project

This project contains:
- `frontend/`: A React application bootstrapped with Vite.
- `backend/`: A Python FastAPI backend designed to support outcome agents (intelligent agents that process tasks and return results).

## Getting Started

### Use Case
#### Use Case 8 - News Digest
##### TABLE OF CONTENTS
1. Welcome from Andhra Pradesh Police
2. Use Case: Problem Statement & Future Vision
3. Expected Outcome
4. Master Data & Input Data
5. Evaluation Criteria

###### 1. Welcome From Andhra Pradesh Police
Greetings from the Andhra Pradesh Police Department!
Preparation Tips:
1. Synthetic Data Generation: Much of the test data can be synthesized using any capable LLM. You’re encouraged to generate synthetic messages, documents, and conversational snippets to prototype workflows and validate approaches.
2. Tool & Technique Exploration: Use this pre-hackathon period to evaluate candidate libraries and platforms—whether open-source transformers, local LLMs (for data-sensitive tasks), or specialized APIs.
3. Data Sensitivity Considerations: Many of these use cases involve sensitive police data. Wherever feasible, favor on-premise or local-model solutions (e.g., running transformers in a secure environment) to keep simulated datasets and prototypes compliant with privacy requirements.

###### 2. Use Case: Problem Statement & Future Vision
1. Problem Statement:District-level SPs depend on timely, accurate intelligence from daily news to coordinate VIP movements, preempt public disturbances, and respond to emerging crime trends. Yet the current process has critical shortcomings.
2. Time Constraints & Manual Overhead: A constable spends 1–2 hours each morning clipping printed articles from multiple newspapers. This delays delivery to the SP, reducing situational responsiveness.
3. Language Barriers: Officers often lack full proficiency in Telugu and other regional languages, relying on staff translations that can misinterpret nuance or introduce errors.
4. Redundancy & Missed Follow-Ups: Related events (e.g., a protest that turns violent) appear over several days and across outlets. Manual grouping is inconsistent, so developing storylines can be overlooked.
5. Lack of Comparative Analysis: Different sources frame the same event divergently—one labels a campus protest “peaceful demonstration,” another highlights “student clashes.” Without side-by-side comparison, SPs cannot quickly discern the most actionable narrative.
6. No Archival or Cross-Day Linking: Historical context (e.g., last week’s similar incidents) remains buried in past bulletins, hindering trend detection and preventive action.
7. Emerging Media Gaps: Printed newspapers omit real-time social-media reports and video feeds—critical for awareness of viral incidents (e.g., local WhatsApp videos showing roadblocks).
Real-World Scenarios (MVP Focus):
1. VIP Security Adjustment: During a political rally in Kakinada, regional outlets report crowd size differently. Automated consolidation allows the SP to redeploy officers before tensions escalate.
2. Crime Trend Detection: Over three days in Visakhapatnam, small-scale ATM thefts go unnoticed manually. AI clustering links these reports, triggering an early security alert.
3. Unrest Monitoring: A viral social-media video shows agitation near a college campus. Without integration, this footage is missed; with AI flagging, the SP can dispatch units proactively.
Future Vision:
Long-term, integrate online news APIs, web-page scraping, social-media feeds, and video flagging based on Superintendent-defined criteria to provide fully automated, multi-modal situational awareness.

###### 3. EXPECTED OUTCOME
1. Relevance Filtering: DistrictRelevanceGenAI applies the SP’s keywords/themes.
2. Clustering & Linking: TopicClusteringGenAI groups same-day reports and links them to a 7-day rolling history.
3. Comparative Insights: SourceComparisonGenAI produces side-by-side summaries of how different outlets frame the same event.
4. Digest Rendering: DigestAssemblyAgent outputs a polished HTML dashboard or styled PDF suitable for morning briefings.

Additional Notes & Expectations:
1. Depth of Relevance: 
Relevance isn’t limited to matching keywords. Participants should account for an item’s potential operational impact (for example, recognizing that a large gathering—even if not explicitly flagged by keywords—may pose a security concern).
2. Nuanced Clustering: 
Effective grouping requires balancing completeness (capturing all related items) with precision (avoiding irrelevant linkages). Thoughtful design is expected to manage this trade-off within the hackathon session.
3. Explainability: 
Every relevance decision or cluster assignment should be accompanied by a clear rationale. For instance, highlight the specific sentences, themes, or risk factors that led to an article’s inclusion or its grouping with other reports. This transparency is critical for SPs to trust and act on the digest.

###### 4. MASTER DATA & INPUT DATA
4.1 Master Data Types
1. News Source Master: Approved English/Telugu newspapers
    a. English - Times of India, Deccan Chronicle, Hindu, Hindustan times, Hans India
    b. Telugu - Eenadu, Sakshi, AndhraJyothi,andhra prabha,Vishalandhra, prajasakti, surya vizianagaram
2. SP Relevance Criteria: Superintendent-defined keywords, themes and weights for each district (minimum two per district)
3. Comparison Criteria: Rules to compare tone, bias and factual differences between sources (minimum two rules)
4.2 Master Data Preparation
1. MS Word / PDF files containing the last seven days of English/Telugu news articles
4.3 Article Fields
1. title (required): The article’s headline
2. body (required): Full text of the article
3. source (required): Identifier for the news outlet
4. publishedDate (required): Publication date in DD/MM/YYYY format
5. extractedLocations (optional): Named places mentioned in the text
6. districtMapping (optional): Assigned district based on content
7. tags (optional): Pre-tagged keywords or themes
(Participants should ingest these files directly and apply the master data types and preparation rules when building their pipelines.)

###### 5. EVALUATION CRITERIA
####### Functional Evaluation
1. News Relevance Criteria – Design
Clarity and completeness of the relevance template, including keywords, themes and priorities.
2. News Relevance Criteria – Execution
Accuracy in applying criteria to filter relevant articles.
3. Grouping News – Design
Clarity and efficiency of grouping rules for both single-day and cross-day linkages.
4. Grouping News – Execution
Correctness and consistency in clustering articles.
5. Creating Competing Views
Quality and clarity of comparative summaries across sources.
6. Processing Telugu Text News (Optional)
Accuracy and readability of translated or NLP-processed Telugu text.
7. Processing News Images (Optional)
OCR accuracy and relevance tagging from images.

####### Technical Evaluation
8. Adoptability
Ease of integration with existing police workflows and infrastructure.
9. Changeability
Flexibility to adjust relevance criteria, clustering rules, and processing pipelines.
10. Efficiency
Processing speed, resource utilization, latency, and API usage.

##### Note
Use these criteria to guide your development and verify that key capabilities meet operational needs.

### Frontend
```
cd frontend
npm run dev
```

### Backend
```
# (Recommended) Activate your Python virtual environment
source ../backend-venv/bin/activate

# Run the FastAPI server
cd backend
uvicorn main:app --reload
```

## Outcome Agents
- The backend exposes `/agent/execute` for agent task execution.
- Extend `backend/main.py` to add more agent logic.

---

For more details, see `.github/copilot-instructions.md`.
