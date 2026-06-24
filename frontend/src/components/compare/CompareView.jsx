import { useEffect, useRef } from 'react'
import * as d3 from 'd3'
import useCompareStore from '../../store/compareStore'

const COLOR_SCALE = d3.schemeTableau10

function CompareGraphView({ graphData }) {
  const svgRef = useRef(null)

  useEffect(() => {
    if (!graphData || !svgRef.current) return

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const width = svgRef.current.clientWidth || 600
    const height = svgRef.current.clientHeight || 500

    const nodes = graphData.nodes.map(n => ({ ...n }))
    const edges = graphData.edges.map(e => ({ ...e }))

    const maxLines = d3.max(nodes, n => n.line_count) || 1
    const nodeRadius = d3.scaleSqrt().domain([0, maxLines]).range([6, 32])

    const g = svg.append('g')
    svg.call(d3.zoom().scaleExtent([0.15, 4])
      .on('zoom', (event) => g.attr('transform', event.transform)))

    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(edges).id(d => d.id).distance(100).strength(0.4))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(d => nodeRadius(d.line_count) + 8))

    const edgeEls = g.append('g').selectAll('line')
      .data(edges).join('line')
      .attr('stroke', '#5C5470').attr('stroke-opacity', 0.5).attr('stroke-width', 1)

    const nodeEls = g.append('g').selectAll('g')
      .data(nodes).join('g')

    nodeEls.append('circle')
      .attr('r', d => nodeRadius(d.line_count))
      .attr('fill', d => COLOR_SCALE[d.color_index] + '33')
      .attr('stroke', d => COLOR_SCALE[d.color_index])
      .attr('stroke-width', 2)

    nodeEls.append('text')
      .text(d => d.label)
      .attr('text-anchor', 'middle')
      .attr('dy', d => nodeRadius(d.line_count) + 12)
      .attr('fill', '#E8C4A0')
      .attr('font-size', '9px')
      .attr('pointer-events', 'none')

    simulation.on('tick', () => {
      edgeEls
        .attr('x1', d => d.source.x).attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x).attr('y2', d => d.target.y)
      nodeEls.attr('transform', d => `translate(${d.x},${d.y})`)
    })

    return () => simulation.stop()
  }, [graphData])

  return <svg ref={svgRef} className="w-full h-full" style={{ minHeight: '500px' }} />
}

function ComparePanel({ graphData, label }) {
  if (!graphData) return null
  return (
    <div className="flex flex-col flex-1 gap-2 overflow-hidden">
      <div className="flex items-center justify-between px-2">
        <p className="text-dusk text-xs font-semibold uppercase tracking-widest">{label}</p>
        <div className="text-xs font-mono text-dusk">
          {graphData.nodes.length} characters · {graphData.edges.length} connections
        </div>
      </div>
      <div className="flex-1 rounded-lg overflow-hidden"
        style={{ backgroundColor: 'rgba(255,255,255,0.02)' }}>
        <CompareGraphView graphData={graphData} />
      </div>
    </div>
  )
}

export default function CompareView() {
  const { graphDataA, graphDataB } = useCompareStore()
  return (
    <div className="flex gap-4 flex-1 overflow-hidden p-4" style={{ height: 'calc(100vh - 65px)' }}>
      <ComparePanel graphData={graphDataA} label="Script A" />
      <div className="w-px bg-slate" />
      <ComparePanel graphData={graphDataB} label="Script B" />
    </div>
  )
}