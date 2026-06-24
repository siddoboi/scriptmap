import { useEffect, useRef, useState } from 'react'
import * as d3 from 'd3'
import useGraphStore from '../../store/graphStore'
import NodeTooltip from './NodeTooltip'

const COLOR_SCALE = d3.schemeTableau10

export default function GraphView() {
  const svgRef = useRef(null)
  const simulationRef = useRef(null)
  const [tooltip, setTooltip] = useState({ node: null, position: { x: 0, y: 0 } })
  const { graphData, activeAct } = useGraphStore()

  useEffect(() => {
    if (!graphData || !svgRef.current) return

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const width = svgRef.current.clientWidth || 800
    const height = svgRef.current.clientHeight || 600

    const visibleNodes = activeAct === 'all'
      ? graphData.nodes.map(n => ({ ...n }))
      : graphData.nodes
          .filter(n => n.act_counts[`act_${activeAct}`] > 0)
          .map(n => ({ ...n }))

    const visibleNodeIds = new Set(visibleNodes.map(n => n.id))
    const visibleEdges = graphData.edges
      .filter(e => visibleNodeIds.has(e.source) && visibleNodeIds.has(e.target))
      .map(e => ({ ...e }))

    if (visibleNodes.length === 0) return

    const maxLines = d3.max(visibleNodes, n => n.line_count) || 1
    const nodeRadius = d3.scaleSqrt().domain([0, maxLines]).range([8, 40])

    const maxWeight = d3.max(visibleEdges, e => e.weight) || 1
    const edgeWidth = d3.scaleLinear().domain([1, maxWeight]).range([1, 4])

    const g = svg.append('g')
    svg.call(
      d3.zoom()
        .scaleExtent([0.15, 4])
        .on('zoom', (event) => g.attr('transform', event.transform))
    )

    const simulation = d3.forceSimulation(visibleNodes)
      .force('link', d3.forceLink(visibleEdges)
        .id(d => d.id)
        .distance(d => Math.max(80, 150 - (d.weight || 1) * 5))
        .strength(0.5)
      )
      .force('charge', d3.forceManyBody().strength(-400))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(d => nodeRadius(d.line_count) + 10))

    simulationRef.current = simulation

    const edgeGroup = g.append('g')
    const nodeGroup = g.append('g')

    const edges = edgeGroup.selectAll('line')
      .data(visibleEdges)
      .join('line')
      .attr('stroke', '#5C5470')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', d => edgeWidth(d.weight))

    const nodes = nodeGroup.selectAll('g')
      .data(visibleNodes)
      .join('g')
      .attr('cursor', 'grab')
      .on('mouseenter', (event, d) => {
        setTooltip({ node: d, position: { x: event.clientX, y: event.clientY } })
        // Highlight connected edges
        edges
          .attr('stroke-opacity', e =>
            e.source.id === d.id || e.target.id === d.id ? 0.9 : 0.1
          )
          .attr('stroke', e =>
            e.source.id === d.id || e.target.id === d.id ? '#C8522A' : '#5C5470'
          )
      })
      .on('mousemove', (event) => {
        setTooltip(prev => ({ ...prev, position: { x: event.clientX, y: event.clientY } }))
      })
      .on('mouseleave', () => {
        setTooltip({ node: null, position: { x: 0, y: 0 } })
        edges
          .attr('stroke-opacity', 0.6)
          .attr('stroke', '#5C5470')
      })
      .call(
        d3.drag()
          .on('start', (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart()
            d.fx = d.x
            d.fy = d.y
          })
          .on('drag', (event, d) => {
            d.fx = event.x
            d.fy = event.y
          })
          .on('end', (event, d) => {
            if (!event.active) simulation.alphaTarget(0)
            d.fx = null
            d.fy = null
          })
      )

    nodes.append('circle')
      .attr('r', d => nodeRadius(d.line_count))
      .attr('fill', d => COLOR_SCALE[d.color_index] + '33')
      .attr('stroke', d => COLOR_SCALE[d.color_index])
      .attr('stroke-width', 2.5)

    nodes.append('text')
      .text(d => d.label)
      .attr('text-anchor', 'middle')
      .attr('dy', d => nodeRadius(d.line_count) + 14)
      .attr('fill', '#E8C4A0')
      .attr('font-size', '11px')
      .attr('font-family', 'Inter, sans-serif')
      .attr('pointer-events', 'none')

    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (!prefersReducedMotion) {
      nodes.attr('opacity', 0)
        .transition()
        .delay((d, i) => i * (1500 / visibleNodes.length))
        .duration(400)
        .attr('opacity', 1)

      edges.attr('opacity', 0)
        .transition()
        .delay(1700)
        .duration(500)
        .attr('opacity', 1)
    }

    simulation.on('tick', () => {
      edges
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y)

      nodes.attr('transform', d => `translate(${d.x},${d.y})`)
    })

    return () => {
      simulation.stop()
      setTooltip({ node: null, position: { x: 0, y: 0 } })
    }
  }, [graphData, activeAct])

  return (
    <div className="relative w-full h-full">
      <svg
        ref={svgRef}
        className="w-full h-full"
        style={{ minHeight: '600px' }}
      />
      <NodeTooltip node={tooltip.node} position={tooltip.position} />
    </div>
  )
}