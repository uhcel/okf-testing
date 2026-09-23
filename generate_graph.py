#!/usr/bin/env python3
"""
Generates:
1. okf_bundle/viz.html & graph.html (Interactive Force-Directed Graph using D3.js)
2. okf_knowledge_graph.svg (Static high-resolution vector diagram for GitHub markdown embedding)
"""

import json
import os
import re

bundle_dir = "okf_bundle"

TYPE_COLORS = {
    "Root Index": "#1e293b",
    "Directory Index": "#475569",
    "Playbook": "#2563eb",
    "Service": "#059669",
    "Configuration": "#d97706",
    "Attested Computation": "#7c3aed",
    "Reference": "#0891b2",
    "Attester": "#e11d48",
    "Update Log": "#64748b"
}

def extract_bundle_graph():
    nodes = []
    edges = []
    
    # Walk all files
    for root, _, files in os.walk(bundle_dir):
        for f in sorted(files):
            if not f.endswith(".md") and not f.endswith(".py"):
                continue
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, bundle_dir)
            
            with open(full_path, "r") as fp:
                content = fp.read()
                
            if f == "exit_code_zero.py":
                nodes.append({
                    "id": "references/attesters/exit_code_zero.py",
                    "label": "exit_code_zero.py",
                    "type": "Attester",
                    "title": "Exit Code Zero Attester",
                    "description": "Deterministic Python receipt validator",
                    "status": "stable",
                    "trust": "deterministic"
                })
                continue
                
            m_type = re.search(r"^type:\s*(.+)$", content, re.M)
            m_title = re.search(r"^title:\s*(.+)$", content, re.M)
            m_desc = re.search(r"^description:\s*(.+)$", content, re.M)
            m_status = re.search(r"^status:\s*(.+)$", content, re.M)
            m_verified = re.search(r"verified:\s*\n\s*-\s*by:\s*(.+)", content, re.M)
            
            if rel_path == "index.md":
                c_type = "Root Index"
                c_title = "Full Stack Knowledge Bundle (Root)"
            elif rel_path.endswith("index.md"):
                c_type = "Directory Index"
                c_title = f"{rel_path.split('/')[0].capitalize()} Index"
            elif rel_path == "log.md":
                c_type = "Update Log"
                c_title = "Bundle Update Log"
            else:
                c_type = m_type.group(1).strip() if m_type else "Concept"
                c_title = m_title.group(1).strip() if m_title else rel_path
                
            c_desc = m_desc.group(1).strip() if m_desc else ""
            c_status = m_status.group(1).strip() if m_status else "stable"
            c_verified = m_verified.group(1).strip() if m_verified else "human:uhcel"
            
            node_obj = {
                "id": rel_path,
                "label": os.path.basename(rel_path).replace(".md", ""),
                "type": c_type,
                "title": c_title,
                "description": c_desc,
                "status": c_status,
                "trust": "human-reviewed" if "human" in c_verified else "machine-confirmed"
            }
            nodes.append(node_obj)
            
            # Find markdown links
            links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)
            for text, link in links:
                if link.startswith("http") or link.startswith("#"):
                    continue
                # Normalize link
                norm_target = link.lstrip("/")
                if not norm_target.endswith(".md") and not norm_target.endswith(".py"):
                    norm_target += ".md"
                # If relative link within same folder
                if not "/" in norm_target and "/" in rel_path:
                    norm_target = os.path.join(os.path.dirname(rel_path), norm_target)
                edges.append({
                    "source": rel_path,
                    "target": norm_target,
                    "label": text,
                    "kind": "hierarchy" if rel_path.endswith("index.md") else "semantic"
                })
                
            # Attester references in Attested Computations
            if "attester:" in content:
                m_att = re.search(r"attester:\s*\n\s*resource:\s*(.+)", content)
                if m_att:
                    att_path = m_att.group(1).strip().lstrip("/")
                    edges.append({
                        "source": rel_path,
                        "target": att_path,
                        "label": "attested_by",
                        "kind": "attestation"
                    })

    # Deduplicate edges and filter targets that exist
    node_ids = {n["id"] for n in nodes}
    clean_edges = []
    seen = set()
    for e in edges:
        if e["target"] in node_ids and e["source"] != e["target"]:
            pair = (e["source"], e["target"])
            if pair not in seen:
                seen.add(pair)
                clean_edges.append(e)
                
    return nodes, clean_edges

def generate_interactive_html(nodes, edges, output_path):
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Open Knowledge Format (OKF) v0.2 Visual Graph</title>
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #0f172a; color: #e2e8f0; overflow: hidden; height: 100vh; display: flex; }}
    #sidebar {{ width: 380px; background: #1e293b; border-right: 1px solid #334155; display: flex; flex-direction: column; z-index: 10; padding: 24px; box-shadow: 4px 0 24px rgba(0,0,0,0.3); overflow-y: auto; }}
    #graph-container {{ flex: 1; position: relative; height: 100%; }}
    svg {{ width: 100%; height: 100%; }}
    h1 {{ font-size: 20px; font-weight: 700; color: #38bdf8; margin-bottom: 8px; display: flex; align-items: center; gap: 8px; }}
    .badge {{ font-size: 11px; background: #0284c7; color: #fff; padding: 2px 8px; border-radius: 9999px; font-weight: 600; text-transform: uppercase; }}
    .subtitle {{ font-size: 13px; color: #94a3b8; margin-bottom: 20px; line-height: 1.4; }}
    .legend {{ background: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 12px; margin-bottom: 20px; }}
    .legend-title {{ font-size: 12px; font-weight: 600; color: #94a3b8; text-transform: uppercase; margin-bottom: 8px; }}
    .legend-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 12px; }}
    .legend-item {{ display: flex; align-items: center; gap: 6px; }}
    .legend-dot {{ width: 10px; height: 10px; border-radius: 50%; }}
    .panel {{ background: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 16px; margin-top: auto; }}
    .panel-title {{ font-size: 14px; font-weight: 700; color: #f8fafc; margin-bottom: 6px; }}
    .panel-type {{ font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 4px; display: inline-block; margin-bottom: 10px; }}
    .panel-desc {{ font-size: 13px; color: #cbd5e1; line-height: 1.5; margin-bottom: 12px; }}
    .panel-meta {{ font-size: 11px; color: #64748b; border-top: 1px solid #1e293b; pt: 10px; }}
    .panel-meta div {{ margin-top: 4px; }}
    .panel-meta span {{ color: #94a3b8; font-weight: 600; }}
    .controls {{ position: absolute; bottom: 20px; right: 20px; display: flex; gap: 8px; background: #1e293b; padding: 8px; border-radius: 8px; border: 1px solid #334155; }}
    .btn {{ background: #334155; border: none; color: #f8fafc; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 12px; font-weight: 600; }}
    .btn:hover {{ background: #475569; }}
    .node circle {{ stroke: #f8fafc; stroke-width: 1.5px; cursor: pointer; transition: all 0.2s; }}
    .node text {{ font-size: 11px; font-weight: 500; fill: #f8fafc; pointer-events: none; text-anchor: middle; }}
    .link {{ stroke-opacity: 0.6; }}
    .link.hierarchy {{ stroke: #475569; stroke-dasharray: 4,4; stroke-width: 1.5px; }}
    .link.semantic {{ stroke: #38bdf8; stroke-width: 2px; }}
    .link.attestation {{ stroke: #f43f5e; stroke-dasharray: 2,2; stroke-width: 2px; }}
  </style>
</head>
<body>
  <div id="sidebar">
    <h1>OKF Knowledge Graph <span class="badge">v0.2</span></h1>
    <div class="subtitle">Interactive progressive disclosure and semantic relationship graph for the Full Stack FastAPI & React knowledge bundle.</div>
    
    <div class="legend">
      <div class="legend-title">Concept Types</div>
      <div class="legend-grid">
        <div class="legend-item"><div class="legend-dot" style="background:#1e293b;border:1px solid #fff;"></div>Root Index</div>
        <div class="legend-item"><div class="legend-dot" style="background:#475569;"></div>Directory Index</div>
        <div class="legend-item"><div class="legend-dot" style="background:#2563eb;"></div>Playbook</div>
        <div class="legend-item"><div class="legend-dot" style="background:#059669;"></div>Service</div>
        <div class="legend-item"><div class="legend-dot" style="background:#d97706;"></div>Configuration</div>
        <div class="legend-item"><div class="legend-dot" style="background:#7c3aed;"></div>Attested Comp.</div>
        <div class="legend-item"><div class="legend-dot" style="background:#0891b2;"></div>Reference</div>
        <div class="legend-item"><div class="legend-dot" style="background:#e11d48;"></div>Attester</div>
      </div>
    </div>

    <div class="legend">
      <div class="legend-title">Edge Relationships</div>
      <div style="font-size:12px;display:flex;flex-direction:column;gap:6px;">
        <div style="display:flex;align-items:center;gap:8px;"><span style="width:20px;height:2px;border-top:2px dashed #64748b;display:inline-block;"></span> Progressive Disclosure</div>
        <div style="display:flex;align-items:center;gap:8px;"><span style="width:20px;height:2px;background:#38bdf8;display:inline-block;"></span> Semantic Cross-Link</div>
        <div style="display:flex;align-items:center;gap:8px;"><span style="width:20px;height:2px;border-top:2px dashed #f43f5e;display:inline-block;"></span> Attestation Contract</div>
      </div>
    </div>

    <div id="inspector" class="panel">
      <div id="ins-type" class="panel-type" style="background:#1e293b;">Click any node</div>
      <div id="ins-title" class="panel-title">Explore OKF Concepts</div>
      <div id="ins-desc" class="panel-desc">Click or hover over any node in the graph to inspect its frontmatter, trust tier, role, and progressive disclosure hierarchy.</div>
      <div id="ins-meta" class="panel-meta">
        <div><span>Concept ID:</span> <span id="ins-id" style="font-family:monospace;color:#38bdf8;">-</span></div>
        <div><span>Status:</span> <span id="ins-status">-</span></div>
        <div><span>Trust Tier:</span> <span id="ins-trust">-</span></div>
      </div>
    </div>
  </div>

  <div id="graph-container">
    <svg id="graph"></svg>
    <div class="controls">
      <button class="btn" id="btn-reset">Reset View</button>
      <button class="btn" id="btn-fit">Fit Center</button>
    </div>
  </div>

  <script>
    const data = {{
      nodes: {json.dumps(nodes)},
      links: {json.dumps(edges)}
    }};

    const colors = {json.dumps(TYPE_COLORS)};

    const width = document.getElementById("graph-container").clientWidth;
    const height = document.getElementById("graph-container").clientHeight;

    const svg = d3.select("#graph")
      .attr("viewBox", [0, 0, width, height]);

    const g = svg.append("g");

    const zoom = d3.zoom()
      .scaleExtent([0.2, 4])
      .on("zoom", (event) => g.attr("transform", event.transform));

    svg.call(zoom);

    // Arrow markers
    const defs = svg.append("defs");
    ["semantic", "attestation"].forEach(kind => {{
      defs.append("marker")
        .attr("id", `arrow-${{kind}}`)
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 22)
        .attr("refY", 0)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
        .append("path")
        .attr("fill", kind === "attestation" ? "#f43f5e" : "#38bdf8")
        .attr("d", "M0,-5L10,0L0,5");
    }});

    const simulation = d3.forceSimulation(data.nodes)
      .force("link", d3.forceLink(data.links).id(d => d.id).distance(d => d.kind === "hierarchy" ? 80 : 130))
      .force("charge", d3.forceManyBody().strength(-350))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(40));

    const link = g.append("g")
      .selectAll("line")
      .data(data.links)
      .join("line")
      .attr("class", d => `link ${{d.kind}}`)
      .attr("marker-end", d => d.kind !== "hierarchy" ? `url(#arrow-${{d.kind}})` : null);

    const node = g.append("g")
      .selectAll(".node")
      .data(data.nodes)
      .join("g")
      .attr("class", "node")
      .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

    node.append("circle")
      .attr("r", d => d.type === "Root Index" ? 18 : (d.type.includes("Index") ? 14 : 11))
      .attr("fill", d => colors[d.type] || "#64748b");

    node.append("text")
      .attr("dy", 22)
      .text(d => d.label);

    node.on("click", (event, d) => {{
      document.getElementById("ins-type").textContent = d.type;
      document.getElementById("ins-type").style.background = colors[d.type] || "#334155";
      document.getElementById("ins-title").textContent = d.title;
      document.getElementById("ins-desc").textContent = d.description || "Progressive disclosure concept document.";
      document.getElementById("ins-id").textContent = d.id;
      document.getElementById("ins-status").textContent = d.status;
      document.getElementById("ins-trust").textContent = d.trust;
      
      // Highlight node
      node.selectAll("circle").attr("stroke-width", n => n.id === d.id ? 4 : 1.5);
    }});

    simulation.on("tick", () => {{
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

      node
        .attr("transform", d => `translate(${{d.x}},${{d.y}})`);
    }});

    function dragstarted(event, d) {{
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }}

    function dragged(event, d) {{
      d.fx = event.x;
      d.fy = event.y;
    }}

    function dragended(event, d) {{
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }}

    document.getElementById("btn-reset").onclick = () => {{
      svg.transition().duration(750).call(zoom.transform, d3.zoomIdentity);
    }};

    document.getElementById("btn-fit").onclick = () => {{
      svg.transition().duration(750).call(zoom.scaleTo, 0.85);
    }};
  </script>
</body>
</html>
"""
    with open(output_path, "w") as f:
        f.write(html_content)
    print(f"Generated interactive HTML graph at: {output_path}")

def generate_static_svg(nodes, edges, output_path):
    # Generates a clear, beautiful SVG vector layout
    # Layout using circular/hierarchical grouping
    width = 1100
    height = 780
    
    # Pre-assign coordinates to domains for beautiful static presentation
    domain_positions = {
        "index.md": (550, 80),
        "log.md": (950, 80),
        "playbooks/index.md": (200, 220),
        "services/index.md": (450, 220),
        "configurations/index.md": (700, 220),
        "computations/index.md": (920, 220),
        "references/index.md": (320, 480),
        
        "playbooks/database_migrations.md": (120, 340),
        "playbooks/local_development.md": (120, 420),
        "playbooks/backend_testing.md": (120, 500),
        "playbooks/production_deployment.md": (120, 580),
        
        "services/stack_topology.md": (450, 340),
        "services/backend_api.md": (450, 430),
        "services/frontend_client.md": (450, 520),
        
        "configurations/environment_variables.md": (700, 360),
        "configurations/docker_compose_files.md": (700, 470),
        
        "computations/run_backend_tests.md": (940, 360),
        "computations/apply_migrations.md": (940, 470),
        
        "references/tech_stack.md": (320, 600),
        "references/attesters/exit_code_zero.py": (940, 600)
    }
    
    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%" style="background:#0f172a;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;">',
        '<defs>',
        '  <marker id="arrow" viewBox="0 -5 10 10" refX="18" refY="0" markerWidth="6" markerHeight="6" orient="auto">',
        '    <path fill="#38bdf8" d="M0,-5L10,0L0,5" />',
        '  </marker>',
        '  <marker id="arrow-att" viewBox="0 -5 10 10" refX="18" refY="0" markerWidth="6" markerHeight="6" orient="auto">',
        '    <path fill="#f43f5e" d="M0,-5L10,0L0,5" />',
        '  </marker>',
        '  <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">',
        '    <feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="#000" flood-opacity="0.5"/>',
        '  </filter>',
        '</defs>',
        '<!-- Title & Legend -->',
        '<text x="40" y="45" fill="#38bdf8" font-size="22" font-weight="700">OKF v0.2 Knowledge Architecture &amp; Progressive Disclosure Graph</text>',
        '<text x="40" y="70" fill="#94a3b8" font-size="13">Hierarchy edges (dashed) show O(1) progressive traversal; colored edges (solid) represent cross-domain semantic links.</text>'
    ]
    
    # Draw Edges
    for e in edges:
        s_pos = domain_positions.get(e["source"])
        t_pos = domain_positions.get(e["target"])
        if s_pos and t_pos:
            x1, y1 = s_pos
            x2, y2 = t_pos
            if e["kind"] == "hierarchy":
                stroke = "#475569"
                dash = 'stroke-dasharray="4,4"'
                marker = ""
                width_line = "1.5"
            elif e["kind"] == "attestation":
                stroke = "#f43f5e"
                dash = 'stroke-dasharray="2,2"'
                marker = 'marker-end="url(#arrow-att)"'
                width_line = "2"
            else:
                stroke = "#38bdf8"
                dash = ""
                marker = 'marker-end="url(#arrow)"'
                width_line = "2"
            svg_lines.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{width_line}" stroke-opacity="0.65" {dash} {marker} />')
            
    # Draw Nodes
    for n in nodes:
        pos = domain_positions.get(n["id"])
        if pos:
            x, y = pos
            color = TYPE_COLORS.get(n["type"], "#64748b")
            r = 18 if n["type"] == "Root Index" else (14 if "Index" in n["type"] else 11)
            svg_lines.append(f'<g filter="url(#glow)" transform="translate({x},{y})">')
            svg_lines.append(f'  <circle r="{r}" fill="{color}" stroke="#f8fafc" stroke-width="2"/>')
            
            # Label
            label = n["label"]
            anchor = "middle"
            dy = -24 if y > 300 and y < 600 else 26
            if "database" in label or "local" in label or "backend_test" in label or "production" in label:
                anchor = "end"
                dx = -18
                dy = 4
                svg_lines.append(f'  <text x="{dx}" y="{dy}" fill="#f8fafc" font-size="11" font-weight="600" text-anchor="{anchor}">{label}</text>')
            elif "run_" in label or "apply_" in label or "exit_" in label:
                anchor = "start"
                dx = 18
                dy = 4
                svg_lines.append(f'  <text x="{dx}" y="{dy}" fill="#f8fafc" font-size="11" font-weight="600" text-anchor="{anchor}">{label}</text>')
            else:
                svg_lines.append(f'  <text x="0" y="{dy}" fill="#f8fafc" font-size="11" font-weight="600" text-anchor="{anchor}">{label}</text>')
            svg_lines.append('</g>')
            
    # Add Legend Box
    svg_lines.append('<g transform="translate(40, 680)">')
    svg_lines.append('  <rect width="1020" height="70" rx="8" fill="#1e293b" stroke="#334155" />')
    svg_lines.append('  <text x="20" y="24" fill="#94a3b8" font-size="11" font-weight="700" text-transform="uppercase">LEGEND</text>')
    
    legend_items = [
        ("Root Index", "#1e293b", 120, 24),
        ("Directory Index", "#475569", 230, 24),
        ("Playbook", "#2563eb", 370, 24),
        ("Service", "#059669", 480, 24),
        ("Configuration", "#d97706", 580, 24),
        ("Attested Computation", "#7c3aed", 710, 24),
        ("Reference", "#0891b2", 890, 24),
        ("Progressive Traversal (Dashed)", "#64748b", 120, 52),
        ("Semantic Cross-Link (Solid Blue)", "#38bdf8", 380, 52),
        ("Attestation Link (Dashed Rose)", "#f43f5e", 680, 52)
    ]
    
    for label, col, lx, ly in legend_items:
        if "Link" in label or "Traversal" in label:
            svg_lines.append(f'  <line x1="{lx}" y1="{ly-4}" x2="{lx+24}" y2="{ly-4}" stroke="{col}" stroke-width="2.5" />')
            svg_lines.append(f'  <text x="{lx+32}" y="{ly}" fill="#e2e8f0" font-size="11">{label}</text>')
        else:
            svg_lines.append(f'  <circle cx="{lx}" cy="{ly-4}" r="5" fill="{col}" stroke="#fff" stroke-width="1" />')
            svg_lines.append(f'  <text x="{lx+12}" y="{ly}" fill="#e2e8f0" font-size="11">{label}</text>')
            
    svg_lines.append('</g>')
    svg_lines.append('</svg>')
    
    with open(output_path, "w") as f:
        f.write("\n".join(svg_lines))
    print(f"Generated static SVG diagram at: {output_path}")

if __name__ == "__main__":
    nodes, edges = extract_bundle_graph()
    generate_interactive_html(nodes, edges, "okf_bundle/viz.html")
    generate_interactive_html(nodes, edges, "viz.html")
    generate_static_svg(nodes, edges, "okf_knowledge_graph.svg")
