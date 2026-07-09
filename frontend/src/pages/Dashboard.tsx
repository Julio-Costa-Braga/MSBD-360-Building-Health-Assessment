import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { ClipboardList, Eye } from 'lucide-react'
import api from '../api/client'
import { InspectionListItem } from '../types'

export default function Dashboard() {
  const [inspections, setInspections] = useState<InspectionListItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/inspections').then((res) => {
      setInspections(res.data)
    }).finally(() => setLoading(false))
  }, [])

  const chartData = inspections
    .filter((i) => i.overall_isa_score !== null)
    .map((i) => ({
      name: i.client_name.length > 15
        ? i.client_name.slice(0, 15) + '...'
        : i.client_name,
      ISA: i.overall_isa_score,
    }))

  const completedCount = inspections.filter((i) => i.status === 'completed').length
  const avgScore = inspections
    .filter((i) => i.overall_isa_score !== null)
    .reduce((acc, i) => acc + (i.overall_isa_score || 0), 0)
  const avgScoreDisplay = completedCount > 0
    ? (avgScore / completedCount).toFixed(1)
    : '—'

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl shadow p-5 border border-gray-200">
          <p className="text-sm text-gray-500">Total de Inspeções</p>
          <p className="text-3xl font-bold mt-1">{inspections.length}</p>
        </div>
        <div className="bg-white rounded-xl shadow p-5 border border-gray-200">
          <p className="text-sm text-gray-500">Concluídas</p>
          <p className="text-3xl font-bold mt-1">{completedCount}</p>
        </div>
        <div className="bg-white rounded-xl shadow p-5 border border-gray-200">
          <p className="text-sm text-gray-500">ISA Médio</p>
          <p className="text-3xl font-bold mt-1">{avgScoreDisplay}</p>
        </div>
      </div>

      {chartData.length > 0 && (
        <div className="bg-white rounded-xl shadow p-5 border border-gray-200">
          <h2 className="text-lg font-semibold mb-3">ISA por Inspeção</h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={chartData}>
              <XAxis dataKey="name" fontSize={12} />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Bar dataKey="ISA" fill="#1e293b" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="bg-white rounded-xl shadow border border-gray-200">
        <div className="px-5 py-4 border-b border-gray-200 flex justify-between items-center">
          <h2 className="text-lg font-semibold">Inspeções Recentes</h2>
          <Link
            to="/inspections/new"
            className="text-sm bg-slate-800 text-white px-4 py-2 rounded-lg hover:bg-slate-700 transition-colors"
          >
            + Nova Inspeção
          </Link>
        </div>
        {loading ? (
          <p className="p-5 text-gray-500">Carregando...</p>
        ) : inspections.length === 0 ? (
          <div className="p-10 text-center text-gray-400">
            <ClipboardList size={48} className="mx-auto mb-3 opacity-50" />
            <p>Nenhuma inspeção ainda.</p>
            <Link to="/inspections/new" className="text-blue-600 hover:underline text-sm">
              Criar primeira inspeção
            </Link>
          </div>
        ) : (
          <ul className="divide-y divide-gray-100">
            {inspections.slice(0, 10).map((insp) => (
              <li key={insp.id}>
                <Link
                  to={`/inspections/${insp.id}`}
                  className="flex items-center justify-between px-5 py-4 hover:bg-gray-50 transition-colors"
                >
                  <div>
                    <p className="font-medium">{insp.client_name}</p>
                    <p className="text-sm text-gray-500">
                      {insp.property_address} — {insp.inspector_name}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`text-sm font-medium ${insp.overall_isa_score !== null ? '' : 'text-gray-400'}`}>
                      {insp.overall_isa_score !== null ? `ISA: ${insp.overall_isa_score}` : 'Rascunho'}
                    </span>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      insp.status === 'completed'
                        ? 'bg-green-100 text-green-700'
                        : 'bg-yellow-100 text-yellow-700'
                    }`}>
                      {insp.status === 'completed' ? 'Concluído' : 'Rascunho'}
                    </span>
                    <Eye size={16} className="text-gray-400" />
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
