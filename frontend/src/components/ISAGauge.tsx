interface ISAGaugeProps {
  score: number
  size?: number
  label?: string
}

function getColor(score: number): string {
  if (score >= 80) return '#22c55e'
  if (score >= 60) return '#eab308'
  if (score >= 40) return '#f97316'
  return '#ef4444'
}

function getLabel(score: number): string {
  if (score >= 80) return 'Excelente'
  if (score >= 60) return 'Aceitável'
  if (score >= 40) return 'Intervenção'
  return 'Risco Elevado'
}

export default function ISAGauge({ score, size = 160, label }: ISAGaugeProps) {
  const radius = size * 0.35
  const strokeWidth = size * 0.06
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (score / 100) * circumference
  const color = getColor(score)

  return (
    <div className="flex flex-col items-center gap-1">
      <svg width={size} height={size * 0.55} viewBox={`0 0 ${size} ${size * 0.55}`}>
        <path
          d={`M ${size * 0.1} ${size * 0.45}
              A ${radius} ${radius} 0 0 1 ${size * 0.9} ${size * 0.45}`}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
        <path
          d={`M ${size * 0.1} ${size * 0.45}
              A ${radius} ${radius} 0 0 1 ${size * 0.9} ${size * 0.45}`}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: 'stroke-dashoffset 0.8s ease' }}
        />
      </svg>
      <span className="text-3xl font-bold" style={{ color }}>
        {score}
      </span>
      <span className="text-sm font-medium text-gray-500">
        {label || getLabel(score)}
      </span>
    </div>
  )
}
