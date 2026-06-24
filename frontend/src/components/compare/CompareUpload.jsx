import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import useCompareStore from '../../store/compareStore'
import { uploadScript, getGraph } from '../../api/parse'

const MAX_SIZE_BYTES = Number(import.meta.env.VITE_MAX_FILE_MB || 5) * 1024 * 1024

function SingleUploadZone({ label, status, onFile, error }) {
  const onDrop = useCallback(async (accepted, rejected) => {
    if (rejected.length > 0) {
      onFile(null, { error_code: 'UNSUPPORTED_FORMAT', message: 'Only PDF and FDX files are supported.' })
      return
    }
    if (accepted.length === 0) return
    onFile(accepted[0], null)
  }, [onFile])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'], 'application/octet-stream': ['.fdx'] },
    maxSize: MAX_SIZE_BYTES,
    multiple: false,
    disabled: status === 'uploading' || status === 'parsed',
  })

  const borderColor = status === 'parsed'
    ? 'border-green-600'
    : status === 'error'
    ? 'border-red-600'
    : isDragActive
    ? 'border-ember'
    : 'border-dusk'

  return (
    <div className="flex flex-col gap-2 flex-1">
      <p className="text-dusk text-xs font-semibold uppercase tracking-widest">{label}</p>
      <div {...getRootProps()}
        className={`border-2 border-dashed rounded-lg px-6 py-10 cursor-pointer
          flex flex-col items-center justify-center text-center transition-colors
          ${borderColor}`}>
        <input {...getInputProps()} />
        {status === 'parsed' ? (
          <div className="flex flex-col items-center gap-2">
            <span className="text-green-400 text-2xl">✓</span>
            <p className="text-parchment text-sm font-medium">Ready</p>
          </div>
        ) : status === 'uploading' ? (
          <div className="flex flex-col items-center gap-2">
            <div className="w-6 h-6 rounded-full border-2 border-slate animate-spin"
              style={{ borderTopColor: 'var(--color-ember)' }} />
            <p className="text-dusk text-xs">Parsing...</p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2">
            <p className="text-parchment text-sm">Drop screenplay here</p>
            <p className="text-dusk text-xs">PDF or FDX</p>
          </div>
        )}
      </div>
      {error && <p className="text-red-400 text-xs">{error.message}</p>}
    </div>
  )
}

export default function CompareUpload({ onBothReady }) {
  const {
    statusA, statusB,
    setStatusA, setStatusB,
    setSessionA, setSessionB,
    setGraphDataA, setGraphDataB,
    setErrorA, setErrorB,
    errorA, errorB,
  } = useCompareStore()

  const handleFileA = async (file, err) => {
    if (err) { setErrorA(err); return }
    setStatusA('uploading')
    try {
      const data = await uploadScript(file)
      setSessionA(data.session_id)
      setStatusA('parsed')
    } catch (e) {
      setErrorA(e.response?.data?.detail || { error_code: 'ERROR', message: 'Upload failed.' })
    }
  }

  const handleFileB = async (file, err) => {
    if (err) { setErrorB(err); return }
    setStatusB('uploading')
    try {
      const data = await uploadScript(file)
      setSessionB(data.session_id)
      setStatusB('parsed')
    } catch (e) {
      setErrorB(e.response?.data?.detail || { error_code: 'ERROR', message: 'Upload failed.' })
    }
  }

  const handleCompare = async () => {
    const { sessionA, sessionB } = useCompareStore.getState()
    const [dataA, dataB] = await Promise.all([
      getGraph(sessionA),
      getGraph(sessionB),
    ])
    setGraphDataA(dataA)
    setGraphDataB(dataB)
    onBothReady()
  }

  const bothParsed = statusA === 'parsed' && statusB === 'parsed'

  return (
    <div className="flex flex-col items-center gap-8 w-full max-w-3xl mx-auto py-16 px-8">
      <div className="text-center">
        <h1 className="text-parchment text-2xl font-bold mb-2">Compare Mode</h1>
        <p className="text-dusk text-sm">Upload two screenplays to compare their character networks.</p>
      </div>

      <div className="flex gap-6 w-full">
        <SingleUploadZone label="Script A" status={statusA} onFile={handleFileA} error={errorA} />
        <SingleUploadZone label="Script B" status={statusB} onFile={handleFileB} error={errorB} />
      </div>

      <button
        onClick={handleCompare}
        disabled={!bothParsed}
        className={`px-8 py-2.5 rounded font-medium text-sm transition-all ${
          bothParsed ? 'text-white cursor-pointer' : 'text-dusk cursor-not-allowed opacity-40'
        }`}
        style={bothParsed
          ? { backgroundColor: 'var(--color-ember)' }
          : { backgroundColor: 'var(--color-slate)' }}>
        Compare
      </button>
    </div>
  )
}