'use client'

import { Sheet, SheetContent, SheetHeader, SheetTitle } from '@/components/ui/sheet'
import ChartAreaInteractive from '../chart-area-interactive'

interface ChartModalProps {
  open: boolean
  onClose: () => void
  title: string
  chartData: any[]
  selectedMonth: string
  onMonthClick: (month: string) => void
  loading: boolean
  error: string | null
}

export function ChartModal({
  open,
  onClose,
  title,
  chartData,
  selectedMonth,
  onMonthClick,
  loading,
  error
}: ChartModalProps) {
  return (
    <Sheet open={open} onOpenChange={onClose}>
      <SheetContent side="bottom" className="h-[90vh] p-0">
        <div className="h-full flex flex-col">
          <SheetHeader className="px-6 py-4 border-b">
            <SheetTitle className="text-lg font-semibold">
              {title}
            </SheetTitle>
          </SheetHeader>
          
          <div className="flex-1 overflow-y-auto p-4">
            {loading ? (
              <div className="flex items-center justify-center h-[400px]">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
              </div>
            ) : error ? (
              <div className="flex items-center justify-center h-[400px]">
                <p className="text-sm text-red-600">Erro: {error}</p>
              </div>
            ) : (
              <div className="h-[calc(90vh-120px)]">
                <ChartAreaInteractive
                  data={chartData}
                  selectedMonth={selectedMonth}
                  onMonthClick={onMonthClick}
                  loading={false}
                  error={null}
                />
              </div>
            )}
          </div>
        </div>
      </SheetContent>
    </Sheet>
  )
}
