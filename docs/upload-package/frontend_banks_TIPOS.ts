export type StatusType = 'OK' | 'WIP' | 'TBD'

export interface BankCompatibility {
  id: number
  bank_name: string
  csv_status: StatusType
  excel_status: StatusType
  pdf_status: StatusType
  ofx_status: StatusType
  created_at: string
  updated_at?: string
}

export interface BankCreate {
  bank_name: string
  csv_status?: StatusType
  excel_status?: StatusType
  pdf_status?: StatusType
  ofx_status?: StatusType
}

export interface BankUpdate {
  bank_name?: string
  csv_status?: StatusType
  excel_status?: StatusType
  pdf_status?: StatusType
  ofx_status?: StatusType
}

export interface BankResponse {
  banks: BankCompatibility[]
  total: number
}

export interface FormatValidation {
  bank_name: string
  file_format: string
  status: StatusType
  is_supported: boolean
  message?: string
}
