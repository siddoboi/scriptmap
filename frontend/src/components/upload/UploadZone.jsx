import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import useGraphStore from '../../store/graphStore'
import { uploadScript } from '../../api/parse'

const MAX_SIZE_BYTES = Number(import.meta.env.VITE_MAX_FILE_MB || 5) * 1024 * 1024

export default function UploadZone() {
  const { status, setStatus, setSessionId, setCharacterList, setError } = useGraphStore()
  const [shaking, setShaking] = useState(false)

  const triggerShake = () => {
    setShaking(true)
    setTimeout(() => setShaking(false), 400)
  }

  const onDrop = useCallback(async (acceptedFiles, rejectedFiles) => {
    if (rejectedFiles.length > 0) {
      triggerShake()
      const code = rejectedFiles[0].errors[0]?.code
      if (code === 'file-too-large') {
        setError({ error_code: 'FILE_TOO_LARGE', message: `File exceeds ${import.meta.env.VITE_MAX_FILE_MB || 5}MB limit.` })
      } else {
        setError({ error_code: 'UNSUPPORTED_FORMAT', message: 'Only PDF and FDX files are supported.' })
      }
      return
    }
    if (acceptedFiles.length === 0) return

    const file = acceptedFiles[0]
    setStatus('uploading')
    try {
      const data = await uploadScript(file)
      setSessionId(data.session_id)
      setCharacterList(data.character_list)
      setStatus('alias_review')
    } catch (err) {
      const detail = err.response?.data?.detail
      setError(detail || { error_code: 'NETWORK_ERROR', message: 'Could not reach the server. Please try again.' })
    }
  }, [setStatus, setSessionId, setCharacterList, setError])

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/octet-stream': ['.fdx'],
    },
    maxSize: MAX_SIZE_BYTES,
    multiple: false,
    disabled: status === 'uploading',
  })

  return (
    <div
      {...getRootProps()}
      className={`
        upload-zone
        relative flex flex-col items-center justify-center
        w-full max-w-xl mx-auto
        border-2 border-dashed rounded-lg
        px-8 py-14 cursor-pointer
        ${isDragReject ? 'border-red-500' : isDragActive ? 'drag-active border-ember' : 'border-dusk'}
        ${isDragActive ? 'drag-active' : ''}
        ${shaking ? 'shake' : ''}
        ${status === 'uploading' ? 'opacity-50 cursor-not-allowed' : ''}
      `}
    >
      <input {...getInputProps()} aria-label="Upload a screenplay file - PDF or FDX format" />
      <div className="flex flex-col items-center gap-4 text-center">
        <svg className="w-10 h-10 text-dusk" fill="none" stroke="currentColor"
          strokeWidth={1.5} viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round"
            d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
        </svg>
        <div>
          <p className="text-parchment font-medium text-base">
            {isDragActive ? 'Drop it here' : 'Drop your screenplay here'}
          </p>
          <p className="text-dusk text-sm mt-1">
            or click to browse &mdash; PDF or FDX
          </p>
        </div>
      </div>
    </div>
  )
}