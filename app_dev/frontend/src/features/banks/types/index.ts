export interface BankCompatibility {
  id: number
  bank_name: string
  file_format: string
  status: 'OK' | 'WIP' | 'TBD'
}

export interface BankCreate {
  bank_name: string
  formats: {
    CSV?: 'OK' | 'WIP' | 'TBD'
    Excel?: 'OK' | 'WIP' | 'TBD'
    PDF?: 'OK' | 'WIP' | 'TBD'
    OFX?: 'OK' | 'WIP' | 'TBD'
  }
}

export interface BankUpdate extends BankCreate {
  old_bank_name?: string
}

export interface BankResponse {
  banks: BankCompatibility[]
  total: number
}
