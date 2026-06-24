import useGraphStore from '../../store/graphStore'

const ACTS = [
  { label: 'All', value: 'all' },
  { label: 'Act 1', value: 1 },
  { label: 'Act 2', value: 2 },
  { label: 'Act 3', value: 3 },
]

export default function GraphControls() {
  const { activeAct, setActiveAct, graphData } = useGraphStore()

  if (!graphData) return null

  return (
    <div className="flex flex-col gap-6 w-60 shrink-0 py-4 px-4 rounded-lg"
      style={{ backgroundColor: 'var(--color-slate)' }}>

      {/* Act filter */}
      <div>
        <p className="text-dusk text-xs font-semibold uppercase tracking-widest mb-3">
          Act Filter
        </p>
        <div className="flex flex-col gap-1">
          {ACTS.map(({ label, value }) => (
            <button
              key={value}
              onClick={() => setActiveAct(value)}
              className={`text-left px-3 py-1.5 rounded text-sm transition-colors ${
                activeAct === value
                  ? 'text-white font-medium'
                  : 'text-dusk hover:text-parchment'
              }`}
              style={activeAct === value
                ? { backgroundColor: 'var(--color-ember)' }
                : {}}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Stats */}
      <div>
        <p className="text-dusk text-xs font-semibold uppercase tracking-widest mb-3">
          Stats
        </p>
        <div className="space-y-1 text-xs font-mono text-dusk">
          <p>{graphData.nodes.length} characters</p>
          <p>{graphData.edges.length} connections</p>
          <p>{graphData.metadata.total_scenes} scenes</p>
          <p>{graphData.metadata.total_pages} pages</p>
        </div>
      </div>
    </div>
  )
}