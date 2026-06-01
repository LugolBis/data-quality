# data-quality
A reference implementation of the data quality metrics introduced in my **Master’s research project**, documented in ```doc/*/paper.typ``` (Property Graph Quality Assessment). This project provides a systematic framework for evaluating **completeness**, **validity**, **consistency**, **integrity**, and **uniqueness** in labeled property graphs (e.g., _Neo4j_).

## Architecture

```mermaid
flowchart TD
    subgraph SOURCES["Data Sources"]
        DB[(Relational DB)]
        CSV[/CSV/]
        JSON[/JSON/]
        TSV[/TSV/]
        OTHER[/Other formats.../]
    end

    subgraph GRAPH[ ]
        NEO4J[("Graph Database\n(Neo4j)")]
    end

    subgraph USAGES["Consumers"]
        AI[AI / ML]
        CRM[CRM]
        BI[BI]
    end

    subgraph FRAMEWORK[data-quality]
        DQ[Data Quality\nAssesment & Profiling]
    end

    DB -->|ETL / Ingestion| NEO4J
    CSV -->|ETL / Ingestion| NEO4J
    JSON -->|ETL / Ingestion| NEO4J
    TSV -->|ETL / Ingestion| NEO4J
    OTHER -->|ETL / Ingestion| NEO4J

    NEO4J -->|Analyzes & Improves| DQ
    DQ -->|Analyzes & Improves| NEO4J

    NEO4J -->|Supplies| AI
    NEO4J -->|Supplies| CRM
    NEO4J -->|Supplies| BI
    
    style DB fill:#2a7d56,stroke:#ffffff,color:#ffffff,stroke-width:1px
    style CSV fill:#2a7d56,stroke:#ffffff,color:#ffffff,stroke-width:1px
    style JSON fill:#2a7d56,stroke:#ffffff,color:#ffffff,stroke-width:1px
    style TSV fill:#2a7d56,stroke:#ffffff,color:#ffffff,stroke-width:1px
    style OTHER fill:#2a7d56,stroke:#ffffff,color:#ffffff,stroke-width:1px

    style AI fill:#da8f74,stroke:#ffffff,color:#ffffff,stroke-width:1px
    style BI fill:#da8f74,stroke:#ffffff,color:#ffffff,stroke-width:1px
    style CRM fill:#da8f74,stroke:#ffffff,color:#ffffff,stroke-width:1px

    style NEO4J fill:#014063,stroke:#ffffff,color:#ffffff,stroke-width:1px
    style DQ fill:#5db3f3,stroke:#ffffff,color:#ffffff,stroke-width:1px
```

## Why measure data quality in a property graph ?

Property graphs are schema‑flexible and semantically rich, but this freedom makes them prone to :
- Missing relationships or nodes → **completeness** issues
- Invalid label sets or malformed property values → **conformity** violations
- Inconsistent functional dependencies → **coherence** flaws
- Structural anomalies (duplicate edges, missing mandatory properties) → **integrity** / **uniqueness** degradation

Automated quality profiling helps:
- Validate graph‑based ETL pipelines
- Enforce domain constraints without a rigid schema
- Detect semantic drift in labels and relationships
- Improve downstream analytics (e.g., graph ML, path queries)

## Getting started

Requires Python 3.14 and [uv](https://github.com/astral-sh/uv).

```bash
# Clone the repository
git clone https://github.com/LugolBis/data-quality.git
cd data-quality

# Create virtual environment and install dependencies
uv venv .venv && source .venv/bin/activate && uv sync
```

Create a ```.env``` file and configure it :
```bash
echo '' > .env
```
and copy-paste in it
```plaintext
URI="neo4j://127.0.0.1:7687"
DB_USER="your_neo4j_user"
DB_PW="your_neo4j_password"
DB_NAME="your_database"
```

## Usage
Launch the interactive profiler (Streamlit UI) :
```bash
streamlit run src/main.py
```
Then :
1. Connect to a Neo4j database (or upload a Cypher dump).
1. Define constraints based on your domain rules.
1. Run the assessment and easily export them as CSV.

## For Developers :
Set up the local git hooks (specifically for pre-commit) with :
```bash
git config --local core.hooksPath .githooks && chmod +x .githooks/pre-commit
```
And add the permissions for the shell script who compile the documentation :
```bash
chmod +x doc/deploy.sh
```
