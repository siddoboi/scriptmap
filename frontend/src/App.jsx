import { useState } from 'react'
import useGraphStore from './store/graphStore'
import UploadZone from './components/upload/UploadZone'
import LoadingSpinner from './components/shared/LoadingSpinner'
import ErrorBanner from './components/shared/ErrorBanner'
import AliasReview from './components/upload/AliasReview'
import GraphView from './components/graph/GraphView'
import GraphControls from './components/graph/GraphControls'
import SentimentArc from './components/sentiment/SentimentArc'

export default function App() {
  const [mode, setMode] = useState('single')
  const { status, error, graphData, activeTab, reset, setError, setStatus } = useGraphStore()

  const handleModeSwitch = (newMode) => {
    if (newMode === mode) return
    if (status === 'graph_ready') {
      if (!window.confirm('Switching modes will clear your current graph. Continue?')) return
    }
    reset()
    setMode(newMode)
  }

  const handleNewAnalysis = () => {
    if (window.confirm('This will clear your current graph. Continue?')) reset()
  }

  return (
    <div className="min-h-screen flex flex-col" style={{ backgroundColor: 'var(--color-void)' }}>

      <nav className="sticky top-0 z-40 flex items-center justify-between px-8 py-4 border-b border-slate"
        style={{ backgroundColor: 'var(--color-void)' }}>
        <span className="text-parchment font-bold text-xl tracking-tight">ScriptMap</span>
        <div className="flex items-center gap-4">
          {status === 'graph_ready' && (
            <button onClick={handleNewAnalysis}
              className="text-dusk text-sm hover:text-parchment transition-colors">
              New Analysis
            </button>
          )}
          <div className="flex items-center gap-2">
            {['single', 'compare'].map((m) => (
              <button key={m} onClick={() => handleModeSwitch(m)}
                className={`px-4 py-1.5 rounded text-sm font-medium transition-colors ${
                  mode === m ? 'text-white' : 'text-dusk hover:text-parchment'
                }`}
                style={mode === m ? { backgroundColor: 'var(--color-ember)' } : {}}>
                {m.charAt(0).toUpperCase() + m.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {status === 'uploading' && <LoadingSpinner />}
      {status === 'alias_review' && <AliasReview />}

      {status === 'graph_ready' && graphData && (
        <div className="flex flex-1 gap-4 p-4 overflow-hidden" style={{ height: 'calc(100vh - 65px)' }}>
          <GraphControls />
          <div className="flex flex-col flex-1 overflow-hidden">
            {/* Tabs */}
            <div className="flex gap-6 mb-3 border-b border-slate pb-2">
              {['graph', 'sentiment'].map(tab => (
                <button
                  key={tab}
                  onClick={() => useGraphStore.getState().setActiveTab(tab)}
                  className={`text-sm font-medium transition-colors ${
                    activeTab === tab
                      ? 'text-parchment border-b-2 border-ember pb-2 -mb-[10px]'
                      : 'text-dusk hover:text-parchment pb-2'
                  }`}
                >
                  {tab === 'graph' ? 'Graph' : 'Sentiment Arc'}
                </button>
              ))}
            </div>
            <div className="flex-1 rounded-lg overflow-hidden">
              {activeTab === 'graph' ? <GraphView /> : <SentimentArc />}
            </div>
          </div>
        </div>
      )}

      {(status === 'idle' || status === 'error') && (
        <main className="flex flex-col items-center px-8 py-16">
          <div className="flex flex-col items-center gap-8 w-full max-w-xl">
            <div className="text-center">
              <h1 className="text-parchment text-3xl font-bold mb-2">
                Every character. Every connection.
              </h1>
              <p className="text-dusk text-base">
                Upload a screenplay to visualise its character network and emotional arcs.
              </p>
            </div>
            <UploadZone />
            {error && (
              <ErrorBanner
                error={error}
                onDismiss={() => { setError(null); setStatus('idle') }}
              />
            )}
            <div className="flex gap-6 text-dusk text-sm">
              <span>PDF or FDX</span>
              <span>&middot;</span>
              <span>Sentiment arcs</span>
              <span>&middot;</span>
              <span>Compare mode</span>
            </div>
          </div>
        </main>
      )}
    </div>
  )
}