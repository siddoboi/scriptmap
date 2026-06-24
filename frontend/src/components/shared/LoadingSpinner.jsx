export default function LoadingSpinner({ onCancel }) {
  return (
    <div className="fixed inset-0 z-50 flex flex-col items-center justify-center"
      style={{ backgroundColor: 'rgba(13,13,20,0.92)' }}>

      <div className="flex flex-col items-center gap-6">
        {/* Spinner */}
        <div className="w-10 h-10 rounded-full border-4 border-slate animate-spin"
          style={{ borderTopColor: 'var(--color-ember)' }} />

        <p className="text-parchment text-base font-medium tracking-wide">
          Analysing screenplay...
        </p>

        {onCancel && (
          <button
            onClick={onCancel}
            className="text-dusk text-sm hover:text-parchment transition-colors mt-2"
          >
            Cancel
          </button>
        )}
      </div>
    </div>
  )
}