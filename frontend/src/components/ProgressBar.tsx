interface ProgressBarProps {
  current: number
  total: number
  status: string
}

export default function ProgressBar({ current, total, status }: ProgressBarProps) {
  const percentage = Math.round((current / total) * 100)

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-4">
      <div className="mb-4">
        <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-2">
          <span>{status}</span>
          <span>{current} / {total}</span>
        </div>
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
          <div
            className="bg-blue-500 h-2 rounded-full transition-all duration-300"
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>
      <p className="text-center text-2xl font-bold text-gray-900 dark:text-white">
        {percentage}%
      </p>
    </div>
  )
}
