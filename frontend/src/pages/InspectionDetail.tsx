import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { Download, Plus, Trash2 } from 'lucide-react'
import api from '../api/client'
import { Inspection, Room, Measurement, ISAResult } from '../types'
import ISAGauge from '../components/ISAGauge'
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
  { value: '', label: 'Geral (cômodo inteiro)' },
  { value: 'wall_1', label: 'Parede 1' },
  { value: 'wall_2', label: 'Parede 2' },
  { value: 'wall_3', label: 'Parede 3' },
  { value: 'wall_4', label: 'Parede 4' },
  { value: 'ceiling', label: 'Teto' },
  { value: 'floor', label: 'Chão' },
]

export default function InspectionDetail() {
  const { id } = useParams<{ id: string }>()
  const [inspection, setInspection] = useState<Inspection | null>(null)
  const [rooms, setRooms] = useState<Room[]>([])
  const [isaResult, setIsaResult] = useState<ISAResult | null>(null)
  const [activeRoom, setActiveRoom] = useState<number | null>(null)
  const [measurements, setMeasurements] = useState<Measurement[]>([])
  const [loading, setLoading] = useState(true)
  const [subLocation, setSubLocation] = useState('')
  const [saving, setSaving] = useState(false)

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
    }
  }, [activeRoom])

  const handleAddRoom = async () => {
    const name = prompt('Nome do cômodo:')
    if (!name) return
    const typeMap: Record<string, string> = {
      'quarto': 'bedroom',
      'sala': 'living_room',
      'cozinha': 'kitchen',
      'banheiro': 'bathroom',
      'escritorio': 'office',
      'corredor': 'hallway',
      'porao': 'basement',
      'sotao': 'attic',
      'outro': 'other',
    }
    const typeInput = prompt(
      'Tipo do cômodo:\n' +
      'quarto / sala / cozinha / banheiro / escritorio / corredor / porao / sotao / outro',
      'quarto'
    )
    if (!typeInput) return
    const roomType = typeMap[typeInput.toLowerCase().trim()] || typeInput
    await api.post(`/inspections/${id}/rooms`, { name, room_type: roomType, floor_level: 0 })
    fetchRooms()
  }

  const handleDeleteRoom = async (roomId: number) => {
    if (!confirm('Remover este cômodo e todas as medições?')) return
    await api.delete(`/inspections/${id}/rooms/${roomId}`)
    if (activeRoom === roomId) setActiveRoom(null)
    fetchRooms()
  }

  const getVal = (id: string): number | null => {
    const el = document.getElementById(id) as HTMLInputElement | null
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
        temperature: getVal('meas-temperature'),
        relative_humidity: getVal('meas-relative_humidity'),
        co2: getVal('meas-co2'),
        surface_temperature: getVal('meas-surface_temperature'),
        material_moisture: getVal('meas-material_moisture'),
        illuminance: getVal('meas-illuminance'),
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

  const handleDownloadPDF = () => {
    window.open(`/api/v1/inspections/${id}/reports/pdf`, '_blank')
  }

  if (loading) return <p className="text-gray-500">Carregando...</p>
  if (!inspection) return <p className="text-red-500">Inspeção não encontrada.</p>

  const activeRoomData = rooms.find((r) => r.id === activeRoom)
  const latestMeas = measurements[measurements.length - 1]

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
          {isaResult && (
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

      {isaResult && (
        <div className="bg-white rounded-xl shadow p-6 border border-gray-200">
          <div className="flex items-center justify-center mb-4">
            <ISAGauge score={isaResult.overall_score} size={180} label={`ISA Geral`} />
          </div>
          {isaResult.rooms.length > 0 && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {isaResult.rooms.map((room) => (
                <RoomCard key={room.room_id} room={room} />
              ))}
            </div>
          )}
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

        <div className="lg:col-span-3">
          {activeRoomData ? (
            <div className="bg-white rounded-xl shadow p-5 border border-gray-200">
              <h2 className="text-lg font-semibold mb-4">
                {activeRoomData.name} — Medições
              </h2>

              <div className="mb-4">
                <label className="block text-sm text-gray-600 mb-1">Local da medição</label>
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
                ].map((field) => (
                  <div key={field.key}>
                    <label className="block text-sm text-gray-600 mb-1">{field.label}</label>
                    <input
                      id={`meas-${field.key}`}
                      type="number"
                      step={field.step}
                      defaultValue={latestMeas?.[field.key as keyof Measurement] ?? ''}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500"
                    />
                  </div>
                ))}
              </div>

              <div className="mt-4">
                <label className="block text-sm text-gray-600 mb-1">Observações</label>
                <textarea
                  id="meas-observations"
                  rows={2}
                  defaultValue={latestMeas?.observations ?? ''}
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

              {measurements.length > 0 && (
                <div className="mt-6">
                  <h3 className="text-sm font-semibold text-gray-500 mb-2">
                    Histórico ({measurements.length} medições)
                  </h3>
                  <div className="max-h-48 overflow-y-auto space-y-1">
                    {[...measurements].reverse().slice(0, 20).map((m) => (
                      <div key={m.id} className="text-xs text-gray-500 flex gap-3 border-b border-gray-100 py-1">
                        <span className="text-gray-400 w-20 shrink-0">
                          {new Date(m.measured_at).toLocaleTimeString('pt-BR')}
                        </span>
                        {m.sub_location && (
                          <span className="text-blue-500 w-16 shrink-0">
                            {SUB_LOCATIONS.find(sl => sl.value === m.sub_location)?.label || m.sub_location}
                          </span>
                        )}
                        <span>{m.temperature ?? '—'}°C</span>
                        <span>{m.relative_humidity ?? '—'}%</span>
                        <span>{m.co2 ?? '—'}ppm</span>
                        <span>{m.illuminance ?? '—'}lux</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
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
