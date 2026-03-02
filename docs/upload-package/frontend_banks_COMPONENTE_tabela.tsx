"use client"

import { BankCompatibility, StatusType } from '../types'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Edit, Trash2 } from "lucide-react"

interface BanksTableProps {
  banks: BankCompatibility[]
  onEdit?: (bank: BankCompatibility) => void
  onDelete?: (id: number) => void
  onUpdateFormat?: (id: number, format: string, newStatus: StatusType) => void
}

const STATUS_CONFIG = {
  OK: { variant: "default" as const, label: "OK" },
  WIP: { variant: "secondary" as const, label: "WIP" },
  TBD: { variant: "destructive" as const, label: "TBD" }
}

export function BanksTable({ banks, onEdit, onDelete, onUpdateFormat }: BanksTableProps) {
  const handleStatusChange = (bankId: number, format: string, newStatus: string) => {
    if (onUpdateFormat) {
      onUpdateFormat(bankId, format, newStatus as StatusType)
    }
  }

  const renderStatusBadge = (status: StatusType) => {
    const config = STATUS_CONFIG[status]
    return (
      <Badge variant={config.variant}>
        {config.label}
      </Badge>
    )
  }

  const renderStatusSelect = (bank: BankCompatibility, format: string, currentStatus: StatusType) => {
    if (!onUpdateFormat) {
      return renderStatusBadge(currentStatus)
    }

    return (
      <Select 
        value={currentStatus} 
        onValueChange={(value) => handleStatusChange(bank.id, format, value)}
      >
        <SelectTrigger className="w-[100px]">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="OK">
            <span className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-green-500" />
              OK
            </span>
          </SelectItem>
          <SelectItem value="WIP">
            <span className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-yellow-500" />
              WIP
            </span>
          </SelectItem>
          <SelectItem value="TBD">
            <span className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-red-500" />
              TBD
            </span>
          </SelectItem>
        </SelectContent>
      </Select>
    )
  }

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[200px]">Banco</TableHead>
            <TableHead className="text-center">CSV</TableHead>
            <TableHead className="text-center">Excel</TableHead>
            <TableHead className="text-center">PDF</TableHead>
            <TableHead className="text-center">OFX</TableHead>
            {(onEdit || onDelete) && (
              <TableHead className="w-[100px] text-center">Ações</TableHead>
            )}
          </TableRow>
        </TableHeader>
        <TableBody>
          {banks.length === 0 ? (
            <TableRow>
              <TableCell 
                colSpan={onEdit || onDelete ? 6 : 5} 
                className="text-center text-muted-foreground h-32"
              >
                Nenhum banco cadastrado
              </TableCell>
            </TableRow>
          ) : (
            banks.map((bank) => (
              <TableRow key={bank.id}>
                <TableCell className="font-medium">{bank.bank_name}</TableCell>
                <TableCell className="text-center">
                  {renderStatusSelect(bank, 'csv', bank.csv_status)}
                </TableCell>
                <TableCell className="text-center">
                  {renderStatusSelect(bank, 'excel', bank.excel_status)}
                </TableCell>
                <TableCell className="text-center">
                  {renderStatusSelect(bank, 'pdf', bank.pdf_status)}
                </TableCell>
                <TableCell className="text-center">
                  {renderStatusSelect(bank, 'ofx', bank.ofx_status)}
                </TableCell>
                {(onEdit || onDelete) && (
                  <TableCell className="text-center">
                    <div className="flex gap-2 justify-center">
                      {onEdit && (
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => onEdit(bank)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                      )}
                      {onDelete && (
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => onDelete(bank.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </TableCell>
                )}
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  )
}
