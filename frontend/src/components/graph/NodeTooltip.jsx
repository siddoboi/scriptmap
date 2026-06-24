export default function NodeTooltip({ node, position }) {
  if (!node) return null

  return (
    <div
      className="fixed z-50 pointer-events-none rounded px-3 py-2 text-sm shadow-lg"
      style={{
        left: position.x + 12,
        top: position.y - 8,
        backgroundColor: 'var(--color-slate)',
        maxWidth: '200px',
      }}
    >
      <p className="text-parchment font-semibold mb-1">{node.label}</p>
      <p className="text-dusk text-xs">{node.line_count} dialogue lines</p>
      <div className="mt-1 text-xs text-dusk space-y-0.5">
        <p>Act 1: {node.act_counts.act_1}</p>
        <p>Act 2: {node.act_counts.act_2}</p>
        <p>Act 3: {node.act_counts.act_3}</p>
      </div>
    </div>
  )
}