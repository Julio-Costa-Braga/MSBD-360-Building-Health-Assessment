import { RoomISAResult } from '../types'
import ISAGauge from './ISAGauge'

interface RoomCardProps {
  room: RoomISAResult
}

const PILLAR_LABELS: Record<string, string> = {
  thermal: 'Térmicas',
  humidity: 'Humidade',
  ventilation: 'Ventilação',
  materials: 'Materiais',
  lighting: 'Iluminação',
  visual: 'Evidências',
}

const CATEGORY_LABELS: Record<string, string> = {
  excellent: 'Excelente',
  acceptable: 'Aceitável',
  needs_intervention: 'Necessita Intervenção',
  high_risk: 'Risco Elevado',
}

export default function RoomCard({ room }: RoomCardProps) {
  return (
    <div className="bg-white rounded-xl shadow p-4 border border-gray-200">
      <div className="flex items-center gap-4 mb-4">
        <ISAGauge score={room.overall_score} size={100} />
        <div>
          <h3 className="text-lg font-semibold">{room.room_name}</h3>
          <p className="text-sm text-gray-500">{CATEGORY_LABELS[room.category] || room.category}</p>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-2">
        {Object.entries(room.pillars).map(([key, p]) => (
          <div key={key} className="flex justify-between text-sm">
            <span className="text-gray-600">{PILLAR_LABELS[key] || key}</span>
            <span className="font-medium">{p.score.toFixed(0)}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
