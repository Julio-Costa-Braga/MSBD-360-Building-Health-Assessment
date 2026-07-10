import { useEffect, useRef, useState } from 'react'
import { Camera, Trash2 } from 'lucide-react'
import api from '../api/client'
import { Photo } from '../types'

interface PhotoUploadProps {
  roomId: number
  photoType: 'before' | 'after'
  label: string
  onUploaded?: () => void
}

export default function PhotoUpload({ roomId, photoType, label, onUploaded }: PhotoUploadProps) {
  const [photos, setPhotos] = useState<Photo[]>([])
  const [uploading, setUploading] = useState(false)
  const fileRef = useRef<HTMLInputElement>(null)

  const fetchPhotos = () => {
    api.get(`/rooms/${roomId}/photos`).then((res) => {
      setPhotos(res.data.filter((p: Photo) => p.photo_type === photoType))
    }).catch(() => {})
  }

  useEffect(() => {
    if (roomId) fetchPhotos()
  }, [roomId])

  const handleFiles = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files || files.length === 0) return

    setUploading(true)
    try {
      const batch: { caption: string; photo_type: string; photo_data: string }[] = []
      for (const file of files) {
        const b64 = await toBase64(file)
        batch.push({ caption: file.name, photo_type: photoType, photo_data: b64 })
      }
      await api.post(`/rooms/${roomId}/photos/bulk`, { photos: batch })
      fetchPhotos()
      onUploaded?.()
    } catch (e) {
      alert('Erro ao enviar fotos.')
    } finally {
      setUploading(false)
      if (fileRef.current) fileRef.current.value = ''
    }
  }

  const handleDelete = async (photoId: number) => {
    if (!confirm('Remover esta foto?')) return
    try {
      await api.delete(`/rooms/${roomId}/photos/${photoId}`)
      fetchPhotos()
    } catch {}
  }

  return (
    <div className="border border-gray-200 rounded-xl p-4">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-sm font-semibold text-gray-700">{label}</h4>
        <button
          onClick={() => fileRef.current?.click()}
          disabled={uploading}
          className="flex items-center gap-1 text-xs bg-slate-800 text-white px-3 py-1.5 rounded-lg hover:bg-slate-700 disabled:opacity-50"
        >
          <Camera size={14} />
          {uploading ? 'Enviando...' : `Adicionar Fotos`}
        </button>
        <input
          ref={fileRef}
          type="file"
          accept="image/*"
          multiple
          className="hidden"
          onChange={handleFiles}
        />
      </div>

      {photos.length === 0 ? (
        <p className="text-xs text-gray-400 text-center py-4">Nenhuma foto {photoType === 'before' ? 'antes' : 'depois'}</p>
      ) : (
        <div className="grid grid-cols-3 sm:grid-cols-4 gap-2">
          {photos.map((p) => (
            <div key={p.id} className="relative group">
              <img
                src={p.photo_data || p.file_path}
                alt={p.caption || ''}
                className="w-full h-20 object-cover rounded-lg border border-gray-200"
              />
              <button
                onClick={() => handleDelete(p.id)}
                className="absolute top-1 right-1 bg-red-500 text-white rounded-full p-0.5 opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <Trash2 size={12} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function toBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result as string)
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}
