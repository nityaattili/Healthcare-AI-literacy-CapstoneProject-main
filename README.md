# AI Literacy in Healthcare: An NLP-Based Knowledge Mapping System

# Overview
---

The rapid growth of Artificial Intelligence (AI) in healthcare has resulted in a large increase in research publications across domains such as clinical decision support, medical imaging, predictive analytics, natural language processing, and healthcare automation. While this growth accelerates innovation, it also creates challenges in organizing, understanding, and exploring large volumes of research literature.

**AI Literacy in Healthcare: An NLP-Based Knowledge Mapping System** is an NLP-driven research exploration platform designed to analyze, organize, summarize, and visualize healthcare AI literature using semantic analysis and interactive knowledge mapping techniques.

The platform integrates:
- Real-time PubMed data ingestion
- Natural Language Processing (NLP)
- Topic modeling and LLM-assisted labeling
- Semantic similarity analysis
- AI-powered research summarization
- Knowledge graph visualization
- Multi-user role-based interaction

to transform unstructured healthcare AI literature into a searchable and interpretable knowledge ecosystem.

# Project Goals
---

The primary objectives of this project are to:

- Improve AI literacy in healthcare research domains
- Develop an intelligent platform for healthcare AI literature exploration
- Extract meaningful insights from large-scale research publications
- Enable semantic and contextual paper discovery
- Generate interpretable knowledge maps and topic relationships
- Support interactive exploration for technical and non-technical users

# Workflow & Methodology
---

### 1. Real-Time Research Data Collection

The platform dynamically retrieves healthcare AI research publications using:
- PubMed API
- PubMed Central (PMC)

#### Metadata Retrieved
- Research titles
- Abstracts
- Authors
- Journals
- Publication years
- Keywords

The real-time ingestion pipeline allows newly published healthcare AI literature to be continuously integrated into the system.

### 2. Data Cleaning & Preprocessing

Collected research data undergoes preprocessing before NLP analysis.

#### Preprocessing Steps
- Duplicate removal
- Missing value handling
- Text normalization
- Stop-word removal
- Tokenization
- Noise filtering

This improves consistency and enhances downstream NLP performance.

### 3. NLP Processing Pipeline

The platform applies multiple NLP techniques to extract insights from healthcare AI literature.

#### A.TF-IDF Keyword Extraction

TF-IDF vectorization is used to identify important terms across research titles and abstracts.

##### Purpose
- Extract domain-relevant keywords
- Identify recurring healthcare AI concepts
- Support semantic retrieval and topic analysis

#### B. Topic Modeling & Theme Discovery

Latent Dirichlet Allocation (LDA) is used to discover thematic structures within the literature corpus.

This enables:
- Discovery of emerging research themes
- Categorization of healthcare AI domains
- Identification of interdisciplinary topic relationships

#### C. LLM-Assisted Topic Labeling

Large Language Models (LLMs) are used to generate human-readable topic labels from extracted keywords and representative abstracts.

This improves:
- Topic interpretability
- Semantic understanding
- User readability

#### D. Semantic Similarity Analysis

Semantic embeddings are generated to identify contextually related research papers.

##### Capabilities
- Context-aware literature retrieval
- Similar paper recommendations
- Relationship discovery beyond keyword matching

This enables intelligent exploration of healthcare AI research.

#### E. AI-Powered Research Summarization

The platform integrates LLM-based summarization techniques to generate concise summaries of research papers and topic clusters.

##### Features
- Abstract summarization
- Topic-level summaries
- Simplified research interpretation

This functionality improves accessibility for both technical and non-technical users.

# Knowledge Mapping & Visualization
---

The project generates interactive graph-based visualizations to represent conceptual relationships between research topics and publications.

### Keyword Knowledge Graph

Built using keyword co-occurrence analysis to visualize relationships between healthcare AI concepts.

#### Examples
- Machine Learning ↔ Clinical Decision Support
- Deep Learning ↔ Medical Imaging
- NLP ↔ Electronic Health Records

### Semantic Similarity Graph

Constructed using embedding similarity scores to identify semantically related publications and research themes.

The graph supports:
- Relationship exploration
- Intelligent paper navigation
- Discovery of interconnected research areas

# Interactive Web Application
---

A Streamlit-based web application was developed to provide real-time research exploration capabilities.

### Core Features

- Semantic research paper search
- Topic exploration dashboards
- Knowledge graph visualization
- Publication trend analytics
- AI-generated summaries
- Metadata exploration

### Multi-User Authentication & Role-Based Access

The platform includes authentication and role-based access functionality to support different user groups.

#### Supported Roles
- Admin
- Researcher
- Student/User

#### Role-Based Features

- Controlled dashboard access ensures that different user roles can securely interact with features and datasets relevant to their permissions.

- Research management functionality allows administrative users to monitor, organize, and manage research workflows and platform content efficiently.

- User-specific exploration capabilities provide personalized access to research search, visualization, and analysis features based on assigned roles.

# Evaluation Methodology
---

The system was evaluated using both analytical and qualitative approaches.

### 1.Topic Modeling Evaluation

Topic modeling outputs were evaluated using coherence analysis and manual validation to ensure that generated themes were semantically meaningful and interpretable.

### 2.Keyword Extraction Evaluation

TF-IDF generated keywords were assessed for contextual relevance and their ability to accurately represent important healthcare AI research concepts.

### 3.Semantic Similarity Evaluation

Semantic retrieval performance was evaluated by analyzing whether embedding-based similarity methods correctly identified conceptually related research publications.

### 4.LLM Topic Label Evaluation

LLM-generated topic labels were reviewed for semantic accuracy, readability, and alignment with extracted keywords and representative abstracts.

### 5.Research Summarization Evaluation

AI-generated summaries were evaluated based on clarity, contextual relevance, and preservation of important research insights from original publications.

### 6.Knowledge Graph Validation

Knowledge graph outputs were assessed to verify the accuracy and interpretability of relationships between healthcare AI concepts and publications.

### 7.System-Level Evaluation

The overall platform was evaluated based on search effectiveness, visualization usability, workflow scalability, and user interaction experience.

# Technologies Used
---

### Programming & Data Processing
- Python
- Pandas
- NumPy

### NLP & Machine Learning
- Scikit-learn
- TF-IDF Vectorization
- Latent Dirichlet Allocation (LDA)
- Semantic Embeddings
- Large Language Models (LLMs)

### Visualization & Graph Analysis
- Plotly
- Matplotlib
- NetworkX

### Database & Retrieval
- ChromaDB

### Web Framework
- Streamlit

### APIs & External Resources
- PubMed API
- PubMed Central (PMC)

# Project Structure
---

```text
AI-Literacy-Healthcare/
│
├── app/                     # Streamlit web application
├── assets/                  # Static assets and visual resources
├── config/                  # Configuration files
├── data/                    # Raw and processed datasets
├── notebooks/               # Exploratory analysis notebooks
├── output/                  # Generated visualizations and graphs
├── scripts/                 # Data ingestion and preprocessing scripts
├── src/                     # Core NLP and application modules
├── requirements.txt         # Project dependencies
├── Dockerfile               # Container configuration
└── README.md
```

# Setup Instructions
---

### 1. Clone Repository

```bash
git clone https://github.com/your-username/AI-Literacy-Healthcare.git
cd AI-Literacy-Healthcare
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

#### Activate Environment

Mac/Linux:
```bash
source venv/bin/activate
```

Windows:
```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Access

Example:
```bash
PUBMED_API_KEY=your_api_key
```

### 5. Run the Application

```bash
streamlit run app/app.py
```

The application will run locally at:

```text
http://localhost:8501
```

# Key Features Summary
---

- Real-time PubMed research ingestion enables the platform to continuously retrieve and process newly published healthcare AI literature for up-to-date analysis and exploration.

- Semantic healthcare AI paper search allows users to discover contextually relevant research papers using NLP-based retrieval instead of relying only on exact keyword matches.

- NLP-based topic modeling automatically identifies major healthcare AI research themes and organizes publications into interpretable topic clusters.

- LLM-assisted topic labeling improves topic interpretability by generating meaningful human-readable labels from extracted keywords and research abstracts.

- AI-powered research summarization helps users quickly understand complex research papers and topic clusters through concise automated summaries.

- Interactive knowledge graph visualization enables users to explore conceptual relationships and interconnected healthcare AI domains through graph-based representations.

- Semantic similarity analysis identifies contextually related publications using embedding-based similarity techniques to improve intelligent literature discovery.

- Publication trend analytics provides insights into the growth, evolution, and distribution of healthcare AI research across different domains and time periods.

- Multi-user authentication and role-based access supports secure and personalized platform interaction for administrators, researchers, and student users.

# Challenges Addressed
---

This project addresses several challenges associated with healthcare AI literature exploration:

1. Information overload in rapidly growing healthcare AI research
2. Difficulty identifying semantic relationships between publications
3. Limited accessibility of technical research for non-technical users
4. Challenges in thematic organization of interdisciplinary literature

# Future Enhancements
---

- Advanced transformer-based retrieval models can be integrated to improve semantic search accuracy and enhance contextual understanding of healthcare AI literature.

- Personalized recommendation systems can be developed to provide users with customized research suggestions based on their search patterns and interests.

- Citation network analysis can be incorporated to visualize relationships between referenced publications and identify influential research contributions.

- Cloud-native deployment and scalability optimization can be implemented to support larger datasets, improved system performance, and multi-user scalability.

# Research Contribution
---

This project demonstrates how NLP, semantic retrieval, LLM-assisted interpretation, and knowledge mapping techniques can improve accessibility and understanding of healthcare AI research.

The platform contributes toward:
- Improving healthcare AI literacy
- Supporting interdisciplinary research discovery
- Enhancing semantic understanding of research literature

# Author
---

**Nitya Tejaswi Attili**  
Master of Science in Information Science & Machine Learning  
University of Arizona

# Acknowledgements
---

Special thanks to:
- Dr. Xiao Hu — Faculty Advisor
- University of Arizona
- PubMed & NCBI Research Resources

# License
---

This project is intended for educational and research purposes.
