import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { Download, Plus, Trash2, X } from 'lucide-react'
import api from '../api/client'
import { Inspection, ISAByTypeResult, ISAResult, Measurement, Room } from '../types'
import ISAGauge from '../components/ISAGauge'
import PhotoUpload from '../components/PhotoUpload'
import RoomCard from '../components/RoomCard'

const ROOM_TYPES: Record<string, string> = {
  bedroom: 'Quarto',
  living_room: 'Sala de Estar',
  kitchen: 'Cozinha',
  bathroom: 'Banheiro',
  office: 'Escritório',
  hallway: 'Corredor',
  basement: 'Porão',
  attic: 'Sótão',
  other: 'Outro',
}

const SUB_LOCATIONS = [
  { value: 'wall_1', label: 'Parede 1' },
  { value: 'wall_2', label: 'Parede 2' },
  { value: 'wall_3', label: 'Parede 3' },
  { value: 'wall_4', label: 'Parede 4' },
  { value: 'ceiling', label: 'Teto' },
  { value: 'floor', label: 'Chão' },
  { value: '', label: 'Geral (cômodo inteiro)' },
]

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

export default function InspectionDetail() {
  const { id } = useParams<{ id: string }>()
  const [inspection, setInspection] = useState<Inspection | null>(null)
  const [rooms, setRooms] = useState<Room[]>([])
  const [isaResult, setIsaResult] = useState<ISAResult | null>(null)
  const [isaByType, setIsaByType] = useState<ISAByTypeResult | null>(null)
  const [activeRoom, setActiveRoom] = useState<number | null>(null)
  const [measurements, setMeasurements] = useState<Measurement[]>([])
  const [loading, setLoading] = useState(true)
  const [subLocation, setSubLocation] = useState('')
  const [saving, setSaving] = useState(false)
  const [activeMeasSub, setActiveMeasSub] = useState<string>('')
  const [showPhotos, setShowPhotos] = useState(false)
  const [showNewRoom, setShowNewRoom] = useState(false)
  const [newRoomName, setNewRoomName] = useState('')
  const [newRoomType, setNewRoomType] = useState('bedroom')

  const fetchInspection = () => {
    api.get(`/inspections/${id}`).then((res) => setInspection(res.data))
  }

  const fetchRooms = () => {
    api.get(`/inspections/${id}/rooms`).then((res) => {
      setRooms(res.data)
      if (res.data.length > 0 && activeRoom === null) {
        setActiveRoom(res.data[0].id)
      }
    })
  }

  const fetchISA = () => {
    api.get(`/inspections/${id}/reports/isa`).then((res) => {
      setIsaResult(res.data)
      fetchInspection()
    }).catch(() => {})
    api.get(`/inspections/${id}/reports/isa-by-type`).then((res) => {
      setIsaByType(res.data)
    }).catch(() => {})
  }

  const fetchMeasurements = (roomId: number) => {
    api.get(`/rooms/${roomId}/measurements`).then((res) => setMeasurements(res.data))
  }

  useEffect(() => {
    if (!id) return
    setLoading(true)
    Promise.all([
      api.get(`/inspections/${id}`),
      api.get(`/inspections/${id}/rooms`),
    ]).then(([inspectionRes, roomsRes]) => {
      setInspection(inspectionRes.data)
      setRooms(roomsRes.data)
      if (roomsRes.data.length > 0) {
        setActiveRoom(roomsRes.data[0].id)
      }
    }).finally(() => setLoading(false))
  }, [id])

  useEffect(() => {
    if (activeRoom !== null) {
      fetchMeasurements(activeRoom)
      setSubLocation('')
      setActiveMeasSub('')
    }
  }, [activeRoom])

  const handleAddRoom = async () => {
    setNewRoomName('')
    setNewRoomType('bedroom')
    setShowNewRoom(true)
  }

  const handleSubmitRoom = async () => {
    if (!newRoomName.trim()) return
    try {
      await api.post(`/inspections/${id}/rooms`, { name: newRoomName.trim(), room_type: newRoomType, floor_level: 0 })
      setShowNewRoom(false)
      fetchRooms()
    } catch (e: any) {
      alert('Erro ao criar cômodo. Verifique o nome e tipo.')
    }
  }

  const handleDeleteRoom = async (roomId: number) => {
    if (!confirm('Remover este cômodo e todas as medições?')) return
    await api.delete(`/inspections/${id}/rooms/${roomId}`)
    if (activeRoom === roomId) setActiveRoom(null)
    fetchRooms()
  }

  const getVal = (field: string): number | null => {
    const el = document.getElementById(`meas-${field}`) as HTMLInputElement | null
    if (!el) return null
    const val = el.value.trim()
    if (val === '') return null
    const num = parseFloat(val)
    return isNaN(num) ? null : num
  }

  const handleSaveMeasurement = async () => {
    if (activeRoom === null) return
    setSaving(true)
    try {
      const m: Record<string, any> = {
        sub_location: subLocation || null,
        temperature: getVal('temperature'),
        relative_humidity: getVal('relative_humidity'),
        co2: getVal('co2'),
        surface_temperature: getVal('surface_temperature'),
        material_moisture: getVal('material_moisture'),
        illuminance: getVal('illuminance'),
        observations: (document.getElementById('meas-observations') as HTMLTextAreaElement)?.value?.trim() || null,
      }
      await api.post(`/rooms/${activeRoom}/measurements`, m)
      fetchMeasurements(activeRoom)
      fetchISA()
    } catch (e: any) {
      alert('Erro ao salvar medição. Verifique os valores digitados.')
    } finally {
      setSaving(false)
    }
  }

  const handleDeleteMeasurement = async (measurementId: number) => {
    if (!confirm('Remover esta medição?')) return
    try {
      await api.delete(`/rooms/${activeRoom}/measurements/${measurementId}`)
      fetchMeasurements(activeRoom!)
      fetchISA()
    } catch {}
  }

  const handleDownloadPDF = () => {
    const baseURL = (import.meta.env.VITE_API_URL as string | undefined) || '/api/v1'
    const url = `${baseURL}/inspections/${id}/reports/pdf`
    window.open(url, '_blank')
  }

  if (loading) return <p className="text-gray-500">Carregando...</p>
  if (!inspection) return <p className="text-red-500">Inspeção não encontrada.</p>

  const activeRoomData = rooms.find((r) => r.id === activeRoom)

  const measBySub = measurements.reduce<Record<string, Measurement[]>>((acc, m) => {
    const key = m.sub_location || ''
    if (!acc[key]) acc[key] = []
    acc[key].push(m)
    return acc
  }, {})

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold">{inspection.client_name}</h1>
          <p className="text-gray-500">{inspection.property_address}</p>
          <p className="text-sm text-gray-400">
            Inspetor: {inspection.inspector_name} — Data: {inspection.inspection_date}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {rooms.length > 0 && (
            <button
              onClick={handleDownloadPDF}
              className="flex items-center gap-1 bg-red-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-red-700 transition-colors"
            >
              <Download size={16} /> PDF
            </button>
          )}
          <button
            onClick={handleAddRoom}
            className="flex items-center gap-1 bg-slate-800 text-white px-4 py-2 rounded-lg text-sm hover:bg-slate-700 transition-colors"
          >
            <Plus size={16} /> Cômodo
          </button>
        </div>
      </div>

      {/* New Room Form Modal */}
      {showNewRoom && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl p-6 w-full max-w-md mx-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Novo Cômodo</h3>
              <button onClick={() => setShowNewRoom(false)} className="text-gray-400 hover:text-gray-600">
                <X size={20} />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-600 mb-1">Nome do cômodo</label>
                <input
                  value={newRoomName}
                  onChange={(e) => setNewRoomName(e.target.value)}
                  placeholder="Ex: Sala Principal"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500"
                  autoFocus
                />
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">Tipo do cômodo</label>
                <select
                  value={newRoomType}
                  onChange={(e) => setNewRoomType(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500"
                >
                  {Object.entries(ROOM_TYPES).map(([value, label]) => (
                    <option key={value} value={value}>{label}</option>
                  ))}
                </select>
              </div>
              <button
                onClick={handleSubmitRoom}
                className="w-full bg-slate-800 text-white py-2 rounded-lg text-sm hover:bg-slate-700 transition-colors"
              >
                Criar Cômodo
              </button>
            </div>
          </div>
        </div>
      )}

      {isaByType && (
        <div className="bg-white rounded-xl shadow p-5 border border-gray-200">
          <div className="flex items-center justify-center mb-4">
            <ISAGauge score={isaByType.overall_score} size={160} label="ISA Geral" />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {Object.entries(isaByType.by_type).map(([rt, group]) => (
              <div key={rt} className="border border-gray-200 rounded-lg p-3">
                <h4 className="text-sm font-semibold text-gray-700 mb-1">
                  {ROOM_TYPES[rt] || rt}
                </h4>
                <p className="text-lg font-bold">{group.average_score.toFixed(0)}</p>
                <p className="text-xs text-gray-500">
                  {CATEGORY_LABELS[group.category] || group.category} — {group.rooms.length} cômodo(s)
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {isaResult && isaResult.rooms.length > 0 && (
        <div className="bg-white rounded-xl shadow p-5 border border-gray-200">
          <h3 className="text-sm font-semibold text-gray-500 mb-3">ISA por Cômodo</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {isaResult.rooms.map((room) => (
              <RoomCard key={room.room_id} room={room} />
            ))}
          </div>
        </div>
      )}

      {!isaResult && rooms.length > 0 && (
        <div className="text-center py-4">
          <button
            onClick={fetchISA}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Calcular ISA
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-1">
          <h2 className="text-lg font-semibold mb-3">Cômodos</h2>
          {rooms.length === 0 && (
            <p className="text-sm text-gray-400">Nenhum cômodo cadastrado.</p>
          )}
          <ul className="space-y-2">
            {rooms.map((room) => (
              <li key={room.id}>
                <button
                  onClick={() => setActiveRoom(room.id)}
                  className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                    activeRoom === room.id
                      ? 'bg-slate-800 text-white'
                      : 'bg-white border border-gray-200 hover:bg-gray-50'
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <span>{room.name}</span>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleDeleteRoom(room.id) }}
                      className="text-red-400 hover:text-red-600"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                  <span className="text-xs opacity-70">
                    {ROOM_TYPES[room.room_type] || room.room_type}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        </div>

        <div className="lg:col-span-3 space-y-6">
          {activeRoomData ? (
            <>
              {/* Medições */}
              <div className="bg-white rounded-xl shadow p-5 border border-gray-200">
                <h2 className="text-lg font-semibold mb-4">
                  {activeRoomData.name} — Medições
                </h2>

                <div className="mb-4">
                  <label className="block text-sm text-gray-600 mb-1">Local da Medição</label>
                  <select
                    value={subLocation}
                    onChange={(e) => setSubLocation(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500"
                  >
                    {SUB_LOCATIONS.map((sl) => (
                      <option key={sl.value} value={sl.value}>{sl.label}</option>
                    ))}
                  </select>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {[
                    { key: 'temperature', label: 'Temperatura (°C)', step: '0.1' },
                    { key: 'relative_humidity', label: 'Humidade Relativa (%)', step: '0.1' },
                    { key: 'co2', label: 'CO₂ (ppm)', step: '1' },
                    { key: 'surface_temperature', label: 'Temp. Superfície (°C)', step: '0.1' },
                    { key: 'material_moisture', label: 'Humidade dos Materiais (%)', step: '0.1' },
                    { key: 'illuminance', label: 'Iluminância (lux)', step: '1' },
                  ].map((field) => {
                    const latestForLoc = subLocation
                      ? measurements.filter(m => (m.sub_location || '') === subLocation).pop()
                      : measurements[measurements.length - 1]
                    return (
                      <div key={field.key}>
                        <label className="block text-sm text-gray-600 mb-1">{field.label}</label>
                        <input
                          id={`meas-${field.key}`}
                          type="number"
                          step={field.step}
                          defaultValue={latestForLoc?.[field.key as keyof Measurement] ?? ''}
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500"
                        />
                      </div>
                    )
                  })}
                </div>

                <div className="mt-4">
                  <label className="block text-sm text-gray-600 mb-1">Observações</label>
                  <textarea
                    id="meas-observations"
                    rows={2}
                    defaultValue={measurements[measurements.length - 1]?.observations ?? ''}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500"
                  />
                </div>

                <button
                  onClick={handleSaveMeasurement}
                  disabled={saving}
                  className="mt-4 bg-slate-800 text-white px-6 py-2 rounded-lg text-sm hover:bg-slate-700 disabled:opacity-50 transition-colors"
                >
                  {saving ? 'Salvando...' : 'Salvar Medição'}
                </button>

                {/* Measurement history grouped by sub-location */}
                {Object.keys(measBySub).length > 0 && (
                  <div className="mt-6">
                    <h3 className="text-sm font-semibold text-gray-500 mb-2">
                      Medições por Local ({measurements.length} total)
                    </h3>
                    <div className="max-h-64 overflow-y-auto space-y-2">
                      {Object.entries(measBySub).map(([loc, ms]) => (
                        <div key={loc} className="border border-gray-100 rounded-lg p-2">
                          <p className="text-xs font-semibold text-blue-600 mb-1">
                            {SUB_LOCATIONS.find(sl => sl.value === loc)?.label || 'Geral'} ({ms.length})
                          </p>
                          {[...ms].reverse().slice(0, 10).map((m) => (
                            <div key={m.id} className="text-xs text-gray-500 flex gap-1 items-center border-b border-gray-50 py-0.5">
                              <span className="text-gray-400 w-14 shrink-0">
                                {new Date(m.measured_at).toLocaleTimeString('pt-BR')}
                              </span>
                              <span className="w-10">{m.temperature ?? '—'}°C</span>
                              <span className="w-10">{m.relative_humidity ?? '—'}%</span>
                              <span className="w-12">{m.co2 ?? '—'}ppm</span>
                              <span className="w-10">{m.illuminance ?? '—'}lux</span>
                              <button
                                onClick={() => handleDeleteMeasurement(m.id)}
                                className="ml-auto text-red-300 hover:text-red-500"
                              >
                                <Trash2 size={11} />
                              </button>
                            </div>
                          ))}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Fotos */}
              <div className="bg-white rounded-xl shadow p-5 border border-gray-200">
                <div className="flex items-center justify-between mb-3">
                  <h2 className="text-lg font-semibold">Fotos</h2>
                  <button
                    onClick={() => setShowPhotos(!showPhotos)}
                    className="text-sm text-blue-600 hover:underline"
                  >
                    {showPhotos ? 'Ocultar' : 'Gerenciar Fotos'}
                  </button>
                </div>
                {showPhotos && activeRoom !== null && (
                  <div className="space-y-4">
                    <PhotoUpload
                      roomId={activeRoom as number}
                      photoType="before"
                      label="Fotos ANTES da intervenção"
                      onUploaded={fetchISA}
                    />
                    <PhotoUpload
                      roomId={activeRoom as number}
                      photoType="after"
                      label="Fotos DEPOIS da intervenção"
                      onUploaded={fetchISA}
                    />
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="text-center py-10 text-gray-400">
              <p>Nenhum cômodo cadastrado.</p>
              <button
                onClick={handleAddRoom}
                className="mt-2 text-blue-600 hover:underline text-sm"
              >
                Adicionar primeiro cômodo
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
