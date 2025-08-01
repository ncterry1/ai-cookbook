async function fetchGraph() {
  const res = await fetch('/api/get_graph');
  const data = await res.json();
  visualizeGraph(data.graph);
}

function visualizeGraph(graphData) {
  const links = graphData.map(d => ({
    source: d.source,
    target: d.target,
    relationship: d.relationship
  }));

  const nodesSet = new Set(links.flatMap(l => [l.source, l.target]));
  const nodes = Array.from(nodesSet).map(id => ({id}));

  const svg = d3.select("#graph").append("svg")
                .attr("width", "100%")
                .attr("height", "600px");

  const simulation = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(links).id(d => d.id).distance(100))
      .force("charge", d3.forceManyBody())
      .force("center", d3.forceCenter(window.innerWidth / 2, 300));

  const link = svg.selectAll(".link")
      .data(links)
      .enter().append("line")
      .attr("stroke", "#aaa");

  const node = svg.selectAll(".node")
      .data(nodes)
      .enter().append("circle")
      .attr("r", 10)
      .attr("fill", "#69b3a2");

  node.append("title").text(d => d.id);

  simulation.on("tick", () => {
    link.attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

    node.attr("cx", d => d.x)
        .attr("cy", d => d.y);
  });
}

fetchGraph();
