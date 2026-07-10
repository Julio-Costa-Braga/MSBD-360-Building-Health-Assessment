export interface Inspection {
  id: number
  client_name: string
  property_address: string
  inspector_name: string
  inspection_date: string
  status: 'draft' | 'completed'
  overall_isa_score: number | null
  notes: string | null
  created_at: string
  updated_at: string
}

export interface InspectionListItem {
  id: number
  client_name: string
  property_address: string
  inspector_name: string
  inspection_date: string
  status: 'draft' | 'completed'
  overall_isa_score: number | null
}

export interface InspectionCreate {
  client_name: string
  property_address: string
  inspector_name: string
  inspection_date: string
  notes?: string
}

export interface Room {
  id: number
  inspection_id: number
  name: string
  room_type: string
  floor_level: number
  area_sqm: number | null
}

export interface RoomCreate {
  name: string
  room_type: string
  floor_level: number
  area_sqm?: number
}

export interface Measurement {
  id: number
  room_id: number
  sub_location: string | null
  temperature: number | null
  relative_humidity: number | null
  co2: number | null
  surface_temperature: number | null
  material_moisture: number | null
  illuminance: number | null
  observations: string | null
  measured_at: string
}

export interface MeasurementCreate {
  sub_location?: string | null
  temperature?: number | null
  relative_humidity?: number | null
  co2?: number | null
  surface_temperature?: number | null
  material_moisture?: number | null
  illuminance?: number | null
  observations?: string
}

export interface Photo {
  id: number
  room_id: number
  file_path: string
  caption: string | null
  taken_at: string
}

export interface PillarScore {
  score: number
  details: string
}

export interface RoomISAResult {
  room_id: number
  room_name: string
  overall_score: number
  category: string
  pillars: Record<string, PillarScore>
}

export interface ISAResult {
  overall_score: number
  category: string
  rooms: RoomISAResult[]
}
