"use client"

import { BankCompatibility } from '../types'
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
import { Edit, Trash2 } from "lucide-react"

interface BanksTableProps {
  banks: BankCompatibility[]
  onEdit: (bank: BankCompatibility) => void
  onDelete?: (id: number) => void
}

const STATUS_CONFIG = {
  OK: { variant: "default" as const, label: "OK" },
  WIP: { variant: "secondary" as const, label: "WIP" },
  TBD: { variant: "destructive" as const, label: "TBD" }
}

export function BanksTable({ banks, onEdit, onDelete }: BanksTableProps) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Banco</TableHead>
          <TableHead>Formato</TableHead>
          <TableHead>Status</TableHead>
          <TableHead className="w-[100px]">Ações</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {banks.length === 0 ? (
          <TableRow>
            <TableCell colSpan={4} className="text-center text-muted-foreground">
              Nenhum banco cadastrado
            </TableCell>
          </TableRow>
        ) : (
          banks.map((bank) => {
            const statusConfig = STATUS_CONFIG[bank.status]
            return (
              <TableRow key={bank.id}>
                <TableCell className="font-medium">{bank.bank_name}</TableCell>
                <TableCell>{bank.file_format}</TableCell>
                <TableCell>
                  <Badge variant={statusConfig.variant}>
                    {statusConfig.label}
                  </Badge>
                </TableCell>
                <TableCell className="flex gap-2">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => onEdit(bank)}
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  {onDelete && (
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => onDelete(bank.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </TableCell>
              </TableRow>
            )
          })
        )}
      </TableBody>
    </Table>
  )
}
