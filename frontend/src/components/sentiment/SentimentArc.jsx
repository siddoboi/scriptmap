import { useState } from 'react'
import {
  LineChart, Line, XAxis, YAxis, ReferenceLine,
  Tooltip, ResponsiveContainer, Legend
} from 'recharts'
import * as d3 from 'd3'
import useGraphStore from '../../store/graphStore'

const COLOR_SCALE = d3.schemeTableau10

export default function SentimentArc() {
  const { graphData } = useGraphStore()
  const [hiddenChars, setHiddenChars] = useState(new Set())

  if (!graphData) return null

  const { sentiment_arcs, act_breaks, nodes } = graphData

  // Only show top 8 characters by default
  const topChars = nodes.slice(0, 8).map(n => n.id)

  const toggleChar = (charId) => {
    setHiddenChars(prev => {
      const next = new Set(prev)
      next.has(charId) ? next.delete(charId) : next.add(charId)
      return next
    })
  }

  // Build unified data array keyed by page
  const allPages = new Set()
  topChars.forEach(char => {
    if (sentiment_arcs[char]) {
      sentiment_arcs[char].forEach(p => allPages.add(p.page))
    }
  })

  const pageData = Array.from(allPages).sort((a, b) => a - b).map(page => {
    const point = { page }
    topChars.forEach(char => {
      const arc = sentiment_arcs[char]
      if (!arc) return
      const match = arc.find(p => p.page === page)
      if (match) point[char] = match.score
    })
    return point
  })

  const getColor = (charId) => {
    const node = nodes.find(n => n.id === charId)
    return node ? COLOR_SCALE[node.color_index] : '#5C5470'
  }

  return (
    <div className="flex flex-col w-full h-full p-4 gap-4">
      <div className="flex items-center justify-between">
        <h2 className="text-parchment font-semibold text-base">Sentiment Arc</h2>
        <p className="text-dusk text-xs">VADER compound score per page</p>
      </div>

      {/* Chart */}
      <div className="flex-1" style={{ minHeight: '400px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={pageData} margin={{ top: 10, right: 20, bottom: 20, left: 0 }}>
            <XAxis
              dataKey="page"
              stroke="#5C5470"
              tick={{ fill: '#5C5470', fontSize: 11, fontFamily: 'JetBrains Mono, monospace' }}
              label={{ value: 'Page', position: 'insideBottom', offset: -10, fill: '#5C5470', fontSize: 11 }}
            />
            <YAxis
              domain={[-1, 1]}
              stroke="#5C5470"
              tick={{ fill: '#5C5470', fontSize: 11, fontFamily: 'JetBrains Mono, monospace' }}
              tickFormatter={v => v.toFixed(1)}
            />

            {/* Zero line */}
            <ReferenceLine y={0} stroke="#5C5470" strokeOpacity={0.4} strokeWidth={1} />

            {/* Act break markers */}
            {act_breaks.map((page, i) => (
              <ReferenceLine
                key={i}
                x={page}
                stroke="#C8522A"
                strokeDasharray="4 4"
                strokeWidth={1}
                label={{
                  value: `Act ${i + 2}`,
                  position: 'top',
                  fill: '#C8522A',
                  fontSize: 10,
                  fontFamily: 'Inter, sans-serif',
                }}
              />
            ))}

            <Tooltip
              contentStyle={{
                backgroundColor: '#2A2A3C',
                border: 'none',
                borderRadius: '4px',
                fontSize: '11px',
                fontFamily: 'JetBrains Mono, monospace',
                color: '#E8C4A0',
              }}
              formatter={(value, name) => [value?.toFixed(3), name]}
              labelFormatter={(label) => `Page ${label}`}
            />

            {topChars.map(char => (
              <Line
                key={char}
                type="monotone"
                dataKey={char}
                stroke={getColor(char)}
                strokeWidth={hiddenChars.has(char) ? 0 : 1.5}
                strokeOpacity={hiddenChars.has(char) ? 0.1 : 0.85}
                dot={false}
                connectNulls={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Character toggles */}
      <div className="flex flex-wrap gap-2">
        {topChars.map(char => {
          const color = getColor(char)
          const hidden = hiddenChars.has(char)
          return (
            <button
              key={char}
              onClick={() => toggleChar(char)}
              className="flex items-center gap-1.5 px-2 py-1 rounded text-xs transition-opacity"
              style={{
                border: `1px solid ${color}`,
                opacity: hidden ? 0.35 : 1,
                color: hidden ? '#5C5470' : '#E8C4A0',
              }}
            >
              <span className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
              {char}
            </button>
          )
        })}
      </div>
    </div>
  )
}