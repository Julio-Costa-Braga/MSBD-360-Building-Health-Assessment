import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'

export default function NewInspection() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    client_name: '',
    property_address: '',
    inspector_name: '',
    inspection_date: new Date().toISOString().split('T')[0],
    notes: '',
  })
  const [saving, setSaving] = useState(false)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    try {
      const res = await api.post('/inspections', form)
      navigate(`/inspections/${res.data.id}`)
    } catch {
      alert('Erro ao criar inspeção. Verifique os dados e tente novamente.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Nova Inspeção</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Cliente</label>
          <input
            name="client_name"
            value={form.client_name}
            onChange={handleChange}
            required
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-slate-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Endereço do Imóvel</label>
          <input
            name="property_address"
            value={form.property_address}
            onChange={handleChange}
            required
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-slate-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Inspetor</label>
          <input
            name="inspector_name"
            value={form.inspector_name}
            onChange={handleChange}
            required
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-slate-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Data da Inspeção</label>
          <input
            type="date"
            name="inspection_date"
            value={form.inspection_date}
            onChange={handleChange}
            required
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-slate-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Observações</label>
          <textarea
            name="notes"
            value={form.notes}
            onChange={handleChange}
            rows={3}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-slate-500"
          />
        </div>
        <button
          type="submit"
          disabled={saving}
          className="w-full bg-slate-800 text-white py-2 rounded-lg font-medium hover:bg-slate-700 disabled:opacity-50 transition-colors"
        >
          {saving ? 'Criando...' : 'Criar Inspeção'}
        </button>
      </form>
    </div>
  )
}
