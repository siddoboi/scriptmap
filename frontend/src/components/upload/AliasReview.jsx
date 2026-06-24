import useGraphStore from '../../store/graphStore'
import { mergeAliases, getGraph } from '../../api/parse'

export default function AliasReview() {
  const { sessionId, characterList, setGraphData, setSentimentArcs, setStatus } = useGraphStore()

  const handleSkip = async () => {
    setStatus('uploading')
    try {
      const data = await getGraph(sessionId)
      setGraphData(data)
      setSentimentArcs(data.sentiment_arcs)
      setStatus('graph_ready')
    } catch {
      setStatus('error')
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center"
      style={{ backgroundColor: 'rgba(13,13,20,0.85)' }}>
      <div className="rounded-lg p-8 w-full max-w-lg"
        style={{ backgroundColor: 'var(--color-slate)' }}>

        <h2 className="text-parchment text-xl font-bold mb-2">Review Characters</h2>
        <p className="text-dusk text-sm mb-6">
          {characterList.length} characters detected. Full alias merge UI coming soon.
        </p>

        <div className="max-h-64 overflow-y-auto mb-6 space-y-1">
          {characterList.map((name) => (
            <div key={name} className="text-parchment text-sm py-1 px-2 rounded"
              style={{ backgroundColor: 'rgba(255,255,255,0.04)' }}>
              {name}
            </div>
          ))}
        </div>

        <div className="flex gap-3 justify-end">
          <button onClick={handleSkip}
            className="px-4 py-2 text-sm text-dusk hover:text-parchment transition-colors">
            Skip
          </button>
          <button onClick={handleSkip}
            className="px-4 py-2 text-sm text-white rounded font-medium"
            style={{ backgroundColor: 'var(--color-ember)' }}>
            Confirm
          </button>
        </div>
      </div>
    </div>
  )
}