const ERROR_MESSAGES = {
  SCANNED_PDF: {
    title: 'Scanned PDF detected',
    body: 'This PDF has no extractable text. Please use a digital PDF exported from screenwriting software, or an FDX file.',
  },
  FILE_TOO_LARGE: {
    title: 'File too large',
    body: `Maximum file size is ${import.meta.env.VITE_MAX_FILE_MB || 5}MB. Most screenplays are well under this limit.`,
  },
  UNSUPPORTED_FORMAT: {
    title: 'Unsupported file type',
    body: 'Only PDF and FDX files are supported.',
  },
  PARSE_TIMEOUT: {
    title: 'Parse timed out',
    body: 'Parsing took too long. Please try a shorter script or check the file is not corrupted.',
  },
  NETWORK_ERROR: {
    title: 'Could not reach the server',
    body: 'The server may be waking up from sleep. Wait 30 seconds and try again.',
  },
  INTERNAL_ERROR: {
    title: 'Something went wrong',
    body: 'An unexpected error occurred. Please try again.',
  },
  PARSE_ERROR: {
    title: 'Could not parse this file',
    body: 'The file may be corrupted or use an unsupported format variant.',
  },
}

export default function ErrorBanner({ error, onRetry, onDismiss }) {
  if (!error) return null

  const info = ERROR_MESSAGES[error.error_code] || {
    title: 'Error',
    body: error.message || 'An unexpected error occurred.',
  }

  const isNetworkError = error.error_code === 'NETWORK_ERROR' ||
                         error.error_code === 'INTERNAL_ERROR'

  return (
    <div className="w-full max-w-xl mx-auto mt-4 rounded-lg overflow-hidden
      border border-red-900 fade-in">

      <div className="px-4 py-3 flex items-start gap-3"
        style={{ backgroundColor: '#2A1020' }}>

        <svg className="w-5 h-5 mt-0.5 shrink-0 text-red-400"
          fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round"
            d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
        </svg>

        <div className="flex-1">
          <p className="text-red-300 font-medium text-sm">{info.title}</p>
          <p className="text-red-400 text-sm mt-0.5 opacity-80">{info.body}</p>
        </div>

        {onDismiss && (
          <button
            onClick={onDismiss}
            className="text-red-400 hover:text-red-200 transition-colors
              duration-150 text-lg leading-none active:scale-95">
            &times;
          </button>
        )}
      </div>

      {(onRetry || isNetworkError) && (
        <div className="px-4 py-2 flex gap-3 border-t border-red-900"
          style={{ backgroundColor: '#200A16' }}>
          {onRetry && (
            <button
              onClick={onRetry}
              className="text-sm text-red-300 hover:text-parchment
                transition-colors duration-150 active:scale-95">
              Try again
            </button>
          )}
          {isNetworkError && (
            <span className="text-red-900 text-sm">
              If the server is cold-starting, wait 30s and retry.
            </span>
          )}
        </div>
      )}
    </div>
  )
}