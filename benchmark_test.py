#!/usr/bin/env python3
"""
Empirical Benchmark Harness: Baseline Documentation vs OKF v0.2 Knowledge Bundle.
Measures:
  1. File read I/O & context tokens (BPE tokenization via cl100k_base)
  2. Traversal hops / tool calls needed to locate and verify target facts
  3. Retrieval latency (wall-clock time in milliseconds)
  4. Signal-to-noise ratio (relevant fact bytes vs total ingested context bytes)
  5. Conformance and trust verification signals
"""

import time
import os
import re
import json
import tiktoken
from typing import Dict, List, Any, Tuple

enc = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    return len(enc.encode(text))

BENCHMARK_QUERIES = [
    {
        "id": "Q1",
        "title": "Database Migrations Workflow",
        "query": "What are the exact commands and steps to create a new database migration using Alembic and SQLModel, and apply the migration locally?",
        "keywords": ["alembic", "migration", "revision", "upgrade head"],
        "baseline_search_paths": [
            "baseline_repo/backend/README.md",
            "baseline_repo/development.md",
            "baseline_repo/README.md"
        ],
        "baseline_primary_doc": "baseline_repo/backend/README.md",
        "okf_domain": "playbooks",
        "okf_concept": "okf_bundle/playbooks/database_migrations.md",
        "required_facts": [
            "uv run alembic revision --autogenerate",
            "uv run alembic upgrade head",
            "backend/app/models.py"
        ]
    },
    {
        "id": "Q2",
        "title": "Stack Topology & Local Port Mappings",
        "query": "List all services running in the local Docker Compose development stack, including their container/service names, the ports exposed on localhost, and their purpose.",
        "keywords": ["localhost", "port", "8000", "5173", "8025", "8080", "8090"],
        "baseline_search_paths": [
            "baseline_repo/development.md",
            "baseline_repo/README.md",
            "baseline_repo/backend/README.md"
        ],
        "baseline_primary_doc": "baseline_repo/development.md",
        "okf_domain": "services",
        "okf_concept": "okf_bundle/services/stack_topology.md",
        "required_facts": [
            "8000",
            "5173",
            "8025",
            "8080",
            "8090",
            "mailpit",
            "adminer",
            "traefik"
        ]
    },
    {
        "id": "Q3",
        "title": "Production Deployment & TLS Configuration",
        "query": "When deploying to production with Docker Compose and Traefik, which specific environment variables must be configured for domain routing and automatic Let's Encrypt TLS certificates, and what compose files must be combined?",
        "keywords": ["compose.deploy.yml", "DOMAIN", "FIRST_SUPERUSER", "POSTGRES_PASSWORD", "HTTPS", "Traefik"],
        "baseline_search_paths": [
            "baseline_repo/deployment-docker-compose.md",
            "baseline_repo/deployment.md",
            "baseline_repo/development.md"
        ],
        "baseline_primary_doc": "baseline_repo/deployment-docker-compose.md",
        "okf_domain": "playbooks",
        "okf_concept": "okf_bundle/playbooks/production_deployment.md",
        "required_facts": [
            "compose.deploy.yml",
            "compose.yml",
            "DOMAIN",
            "FIRST_SUPERUSER",
            "POSTGRES_PASSWORD",
            "SECRET_KEY"
        ]
    },
    {
        "id": "Q4",
        "title": "Frontend Build & FastAPI Static Serving",
        "query": "How does the frontend production build get served by FastAPI in production? Specify the frontend build command, the destination directory for build artifacts, and the URL where FastAPI serves the built frontend.",
        "keywords": ["bun run build", "backend/app/frontend", "http://localhost:8000", "served by FastAPI"],
        "baseline_search_paths": [
            "baseline_repo/development.md",
            "baseline_repo/frontend/README.md",
            "baseline_repo/deployment-docker-compose.md"
        ],
        "baseline_primary_doc": "baseline_repo/development.md",
        "okf_domain": "services",
        "okf_concept": "okf_bundle/services/frontend_client.md",
        "required_facts": [
            "bun run build",
            "backend/app/frontend",
            "8000"
        ]
    },
    {
        "id": "Q5",
        "title": "Backend Test Suite & Coverage Execution",
        "query": "What is the exact command to run the backend test suite with coverage in Docker Compose, and what file controls the environment variables used during tests?",
        "keywords": ["tests-start.sh", "docker compose exec backend", "coverage", "FASTAPI_ENV"],
        "baseline_search_paths": [
            "baseline_repo/backend/README.md",
            "baseline_repo/development.md"
        ],
        "baseline_primary_doc": "baseline_repo/backend/README.md",
        "okf_domain": "playbooks",
        "okf_concept": "okf_bundle/playbooks/backend_testing.md",
        "required_facts": [
            "docker compose exec backend bash scripts/tests-start.sh",
            "FASTAPI_ENV=development",
            "coverage report"
        ]
    }
]

def simulate_baseline_retrieval(q: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulates real-world agent retrieval on unstructured documentation:
    1. Search across repository docs to identify which files match the query keywords.
    2. Read the matching documentation files to extract and verify the needed facts.
    """
    t0 = time.perf_counter()
    hops = 0
    total_bytes = 0
    total_text = ""
    files_read = []
    
    # Step 1: Lexical scan / grep across repo markdown docs
    hops += 1  # grep/find hop
    candidate_scores = {}
    for doc_path in q["baseline_search_paths"]:
        if os.path.exists(doc_path):
            with open(doc_path, "r") as f:
                content = f.read()
            score = sum(1 for kw in q["keywords"] if kw.lower() in content.lower())
            candidate_scores[doc_path] = (score, content)
    
    # Step 2: Ingest top candidate documentation files
    # The agent reads candidate docs until all required facts are identified or exhausted
    for doc_path, (score, content) in sorted(candidate_scores.items(), key=lambda x: x[1][0], reverse=True):
        hops += 1  # file read hop
        files_read.append(doc_path)
        total_bytes += len(content)
        total_text += content + "\n\n"
        # Check if all required facts are present
        all_found = all(f.lower() in total_text.lower() for f in q["required_facts"])
        if all_found:
            break
            
    latency_ms = (time.perf_counter() - t0) * 1000
    token_count = count_tokens(total_text)
    
    # Calculate relevant fact density (length of target fact statements vs total ingested text)
    fact_bytes = sum(len(f) for f in q["required_facts"])
    signal_ratio = (fact_bytes / total_bytes) * 100 if total_bytes > 0 else 0
    
    return {
        "latency_ms": latency_ms,
        "hops": hops,
        "files_read": files_read,
        "total_bytes": total_bytes,
        "tokens": token_count,
        "signal_ratio": signal_ratio,
        "facts_found": sum(1 for f in q["required_facts"] if f.lower() in total_text.lower()),
        "total_facts": len(q["required_facts"])
    }

def simulate_okf_retrieval(q: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulates real-world agent retrieval on OKF v0.2 bundle via Progressive Disclosure:
    1. Read root index.md (progressive disclosure layer 1) -> select domain
    2. Read domain index.md (progressive disclosure layer 2) -> select concept
    3. Read target concept.md (progressive disclosure layer 3) -> exact concept metadata + body
    """
    t0 = time.perf_counter()
    hops = 0
    total_bytes = 0
    total_text = ""
    files_read = []
    
    # Step 1: Read root index.md
    hops += 1
    root_path = "okf_bundle/index.md"
    with open(root_path, "r") as f:
        root_content = f.read()
    files_read.append(root_path)
    total_bytes += len(root_content)
    total_text += root_content + "\n\n"
    
    # Step 2: Read domain index.md
    hops += 1
    domain_path = f"okf_bundle/{q['okf_domain']}/index.md"
    with open(domain_path, "r") as f:
        domain_content = f.read()
    files_read.append(domain_path)
    total_bytes += len(domain_content)
    total_text += domain_content + "\n\n"
    
    # Step 3: Read target concept.md
    hops += 1
    concept_path = q["okf_concept"]
    with open(concept_path, "r") as f:
        concept_content = f.read()
    files_read.append(concept_path)
    total_bytes += len(concept_content)
    total_text += concept_content + "\n\n"
    
    latency_ms = (time.perf_counter() - t0) * 1000
    token_count = count_tokens(total_text)
    
    # Calculate relevant fact density
    fact_bytes = sum(len(f) for f in q["required_facts"])
    signal_ratio = (fact_bytes / total_bytes) * 100 if total_bytes > 0 else 0
    
    # Check OKF specific trust metadata
    has_trust = "verified:" in concept_content and "generated:" in concept_content
    has_sources = "sources:" in concept_content
    
    return {
        "latency_ms": latency_ms,
        "hops": hops,
        "files_read": files_read,
        "total_bytes": total_bytes,
        "tokens": token_count,
        "signal_ratio": signal_ratio,
        "facts_found": sum(1 for f in q["required_facts"] if f.lower() in concept_content.lower()),
        "total_facts": len(q["required_facts"]),
        "has_trust": has_trust,
        "has_sources": has_sources
    }

def run_benchmarks(iterations=50):
    print(f"Executing benchmark with {iterations} iterations per query...")
    results = []
    
    for q in BENCHMARK_QUERIES:
        b_times, b_tokens, b_bytes, b_hops, b_facts = [], [], [], [], []
        o_times, o_tokens, o_bytes, o_hops, o_facts = [], [], [], [], []
        
        for _ in range(iterations):
            b_res = simulate_baseline_retrieval(q)
            b_times.append(b_res["latency_ms"])
            b_tokens.append(b_res["tokens"])
            b_bytes.append(b_res["total_bytes"])
            b_hops.append(b_res["hops"])
            b_facts.append(b_res["facts_found"])
            
            o_res = simulate_okf_retrieval(q)
            o_times.append(o_res["latency_ms"])
            o_tokens.append(o_res["tokens"])
            o_bytes.append(o_res["total_bytes"])
            o_hops.append(o_res["hops"])
            o_facts.append(o_res["facts_found"])
            
        b_avg_time = sum(b_times) / len(b_times)
        o_avg_time = sum(o_times) / len(o_times)
        b_tok = b_tokens[0]
        o_tok = o_tokens[0]
        b_byt = b_bytes[0]
        o_byt = o_bytes[0]
        b_hop = b_hops[0]
        o_hop = o_hops[0]
        
        token_reduction_pct = ((b_tok - o_tok) / b_tok) * 100
        byte_reduction_pct = ((b_byt - o_byt) / b_byt) * 100
        speedup = b_avg_time / o_avg_time if o_avg_time > 0 else 1.0
        
        results.append({
            "id": q["id"],
            "title": q["title"],
            "baseline": {
                "latency_ms": b_avg_time,
                "tokens": b_tok,
                "bytes": b_byt,
                "hops": b_hop,
                "facts_found": b_facts[0],
                "total_facts": q["required_facts"]
            },
            "okf": {
                "latency_ms": o_avg_time,
                "tokens": o_tok,
                "bytes": o_byt,
                "hops": o_hop,
                "facts_found": o_facts[0],
                "total_facts": q["required_facts"]
            },
            "token_reduction_pct": token_reduction_pct,
            "byte_reduction_pct": byte_reduction_pct,
            "speedup": speedup
        })
        
    return results

if __name__ == "__main__":
    benchmark_results = run_benchmarks(50)
    with open("benchmark_results.json", "w") as f:
        json.dump(benchmark_results, f, indent=2)
    print("Benchmark complete! Results saved to benchmark_results.json")
