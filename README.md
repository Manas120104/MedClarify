# MedClarify 🏥

<div align="center">
  <img src="https://biteable.com/wp-content/uploads/2022/11/Healthcare01.gif" alt="Healthcare" width="400"/>
</div>

> A modular, domain-specialized artificial intelligence system designed to address distinct yet interconnected challenges in the medical domain through Health Claim Verification and Medical Report Analysis.
<table>
<tr>
<td width="50%" valign="top">
## 📋 Table of Contents
- [Overview](#-overview)
- [Problem Statement](#-problem-statement)
- [System Components](#️-system-components)
- [Health Claim Verification Module](#-health-claim-verification-module)
- [Medical Report Analysis Module](#-medical-report-analysis-module)
- [Technology Stack](#️-technology-stack)
- [Data Sources](#-data-sources--knowledge-base)
- [Getting Started](#-getting-started)
</td>
<td width="50%" valign="top" align="center">
<img src="https://cdn.dribbble.com/userupload/26434877/file/original-14e9fb98d7146baae3b39c2fc5fd11bc.gif" alt="Medical Analysis" width="100%"/>
</td>
</tr>
</table>
## 🎯 Overview

MedClarify tackles two major challenges in healthcare:

1. **⚡ Inefficiencies and complexities** involved in manually verifying health claims
2. **📄 Difficulties in interpreting** dense medical documentation for non-specialist users

The system is built around **two principal components** that work together to make medical information more accessible while maintaining accuracy and reliability.

## 🚨 Problem Statement

### Current Challenges
- **⏰ Time-consuming** manual health claim verification processes
- **❌ Error-prone** manual interpretation of medical documents  
- **🚫 Inaccessible** medical information for non-specialists
- **🔍 Complex medical terminology** that's difficult to understand

### What MedClarify Solves
- Automates health claim verification with evidence-based analysis
- Transforms complex medical reports into patient-friendly summaries
- Provides reliable, source-backed medical information
- Bridges the gap between medical expertise and patient understanding

## 🏗️ System Components

MedClarify consists of **two strategically developed modules**:

```
┌─────────────────────────────────────────────────────────┐
│                    MedClarify System                    │
├─────────────────────┬───────────────────────────────────┤
│  🔍 Health Claim    │  📋 Medical Report Analysis       │
│     Verification    │      Module                       │
│     Module          │                                   │
└─────────────────────┴───────────────────────────────────┘
```

## 🔍 Health Claim Verification Module

### 🎯 Purpose
Leverages **Mistral-7B-Instruct-v0.3** within a **Retrieval-Augmented Generation (RAG) framework** to verify health claims using authoritative medical sources.

### 🔄 How It Works

#### Step 1: Claim Input 📝
Users can submit various types of health queries:
- **Specific assertions**: *"Dark chocolate improves cognitive function"*
- **Comparative statements**: *"Vitamin D is more effective than calcium for bone health"*, *"Covishield has better efficacy than Covaxin"*
- **General inquiries**: *"Garlic and health"*, *"Benefits and risks of intermittent fasting"*
- **Treatment queries**: *"Does garlic lower blood pressure?"*, *"Inhaling steam with eucalyptus oil can eliminate the coronavirus from the
lungs"*, *"Mixing Covaxin and Covishield vaccines may result in harmful side effects"*

#### Step 2: Semantic Search Retrieval 🔎
- Uses **Sentence Transformer** to create semantic embeddings of the query
- Searches **Pinecone-powered vector database** using vector similarity search
- Retrieves relevant passages from the curated medical knowledge base

#### Step 3: Web Search Retrieval 🌐
When internal database lacks relevant information:
- Activates **Google Search API** as fallback mechanism
- **Constrains searches** to predefined credible health sources only
- Forwards retrieved web content to the language model

#### Step 4: Claim Validation ✅
- **Mistral-7B-Instruct-v0.3** processes all retrieved evidence
- Generates natural language response with **judgement on the health claim**
- **Strictly grounds decisions** in factual information from provided sources
- **Avoids speculation** - only evidence-based conclusions

#### Step 5: Structured Knowledge Storage 💾
For new information from web searches (i.e., not already present in the internal vector database), the system creates **structured JSON objects** that encapsulate the essence of the claim evaluation. These JSON objects include the original claim, an evidence level tag (e.g., High, Medium, Low), an explanatory reasoning passage summarising the model’s inference, and a list of source references with URLs. The JSON structure is illustrated as follows:

```json
{
  "health_claims": [{
    "claim": "Eating garlic lowers blood pressure",
    "evidence_level": "Medium",
    "explanation": "Some studies suggest that garlic supplementation may lead to modest reductions in blood pressure, particularly in individuals with hypertension. However, most research consists of small, preliminary, or low-quality studies, and more extensive research is needed to confirm these findings.",
    "sources": [
      {
        "name": "National Center for Complementary and Integrative Health",
        "url": "https://www.nccih.nih.gov/health/garlic"
      }
    ]
  }]
}
```
By organizing the information retrieved from the web into a well-defined JSON schema, MedClarify transforms raw, unstructured web content into distilled, high-utility **Knowledge Artefacts**.

These **Knowledge Artefacts** are stored in the **Pinecone Vector Database** and later used for reference in case of **semantically similar health queries in future**. Hence, it facilitates **Knowledge Reuse** as the previous LLM responses are stored, and the system doesn't need to re-initiate a full **web-retrieval-and-reasoning pipeline** — which involves performing another web search, extracting content, and invoking the LLM for reasoning across the web contents. The system can directly fetch the precomputed structured response, so that the LLM can refer to its previous response and doesn’t have to perform complex reasoning from scratch again and again.

### 🚀 Key Benefits
- **⚡ Avoids redundant processing** for similar future queries
- **🏃‍♂️ Accelerates inference time** through cached responses  
- **📊 Reduces server load** and computational overhead
- **🎯 Ensures consistency** across similar health claim queries
- **🔄 Promotes data reuse** and minimizes discrepancies from changing web content

## 📋 Medical Report Analysis Module

### 🎯 Purpose
**Bridges the gap** between complex clinical documentation and patient comprehension by automating extraction, explanation, and summarization of medical reports.

### 🔄 Multi-Stage Processing Pipeline

#### Step 1: PDF Text Extraction 📄
- Uses **PyPDF2 library** for robust text extraction
- **Maintains original formatting, structure, and contextual coherence**
- Preserves relationships between sections (diagnoses, findings, medications, observations)

#### Step 2: Named Entity Recognition (NER) 🏷️
- Processes extracted text with **BIOMed NER model**
- **Transformer-based biomedical NER framework** trained specifically for medical content
- **Detects and classifies** medically relevant entities:
  - 🦠 Diseases
  - 💊 Drug names  
  - 🩺 Treatment protocols
  - 🫀 Anatomical terms
  - 🤒 Symptoms
  - 🧪 Biomarkers
  - 🔬 Diagnostic procedures

#### Step 3: Medical Terminology Explanation 📚
- Uses **BioMistral-7B model** for domain-specialized explanations
- **Fine-tuned on medical literature and clinical data**
- Generates **medically reliable explanations** for extracted biomedical entities
- **Simplifies complex terms** without compromising factual integrity

#### Step 4: Comprehensive Summarization 📝
- **Mistral-7B-Instruct-v0.3** processes complete medical content:
  - Original report text
  - Identified entities  
  - Generated explanations
- Creates **cohesive, concise, and conversational summary**
- **Preserves clinical relevance** while being accessible to patients
- Presents information in **reassuring format** for patient understanding

### 🎯 Final Output
- **Patient-friendly summary** displayed on user interface
- **Holistic and comprehensible overview** of medical reports
- **Clinical accuracy maintained** throughout the simplification process

## 🛠️ Technology Stack

### Core Models
- **🤖 Mistral-7B-Instruct-v0.3**: Primary LLM for reasoning and generation
- **🧬 BioMistral-7B**: Medical domain-specialized model for terminology explanation
- **🏷️ BIOMed NER**: Transformer-based biomedical entity recognition
- **🔤 Sentence Transformer**: Semantic embedding generation

### Infrastructure
- **🗄️ Pinecone**: Vector database for knowledge storage and retrieval
- **🔍 Google Search API**: Web search fallback mechanism  
- **📄 PyPDF2**: PDF document text extraction library

### Data Format
- **📋 JSON structured output** for machine-readable results
- **🔗 Source attribution** with URLs and citations
- **📊 Evidence level tagging** (High, Medium, Low)

## 📚 Data Sources & Knowledge Base

The system is **anchored to authoritative medical domains** including:

- **🏛️ Centers for Disease Control and Prevention (CDC)**
- **🌍 World Health Organization (WHO)**  
- **🔬 National Institutes of Health (NIH)**
- **📖 National Center for Biotechnology Information (NCBI)**
- **➕ Additional trusted medical and public health sources**

This ensures **verifiably grounded responses** in credible evidence and maintains the highest standards of medical accuracy.

## 🚀 Getting Started

### Health Claim Verification
1. **📝 Submit your health claim** or question
2. **⏳ Wait for semantic search** through medical knowledge base
3. **📊 Receive evidence-based assessment** with source citations
4. **💾 System stores structured knowledge** for future similar queries

### Medical Report Analysis  
1. **📤 Upload your PDF medical report**
2. **🔍 System extracts and analyzes** medical entities
3. **📚 Receives explanations** of medical terminology
4. **📋 Get patient-friendly summary** of your report

## 💡 Key Features

### Health Claim Verification ✅
- **🎯 Evidence-based claim assessment** 
- **📊 Confidence levels** (High/Medium/Low)
- **🔗 Direct source citations** with URLs
- **💾 Intelligent knowledge caching** for efficiency
- **🌐 Fallback web search** for comprehensive coverage

### Medical Report Analysis 📄
- **📝 Robust PDF text extraction**
- **🏷️ Advanced biomedical entity recognition**  
- **📚 Plain-language medical term explanations**
- **👥 Patient-centered report summaries**
- **🎯 Clinical accuracy preservation**

---

**⚠️ Disclaimer**: MedClarify is designed to assist with medical information analysis and should not replace professional medical advice. Always consult healthcare providers for medical decisions.
