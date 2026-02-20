'use client'

import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LabelList,
} from 'recharts'

interface ChartDataPoint {
  anomes: number
  mesLabel: string
  ativos: number
  passivosAbs: number
  pl: number
  plChart: number
}

interface PatrimonioChartProps {
  chartData: ChartDataPoint[]
  domain: [number, number]
  formatCompact: (v: number) => string
  formatTooltipValue: (value: number, name: string) => string
}

export function PatrimonioChart({
  chartData,
  domain,
  formatCompact,
  formatTooltipValue,
}: PatrimonioChartProps) {
  return (
    <div className="h-[280px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart
          data={chartData}
          margin={{ top: 35, right: 10, left: 10, bottom: 0 }}
          barCategoryGap="20%"
        >
          <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200" />
          <XAxis
            dataKey="mesLabel"
            tick={{ fontSize: 10 }}
            interval="preserveStartEnd"
          />
          <YAxis hide domain={domain} />
          <Tooltip
            formatter={formatTooltipValue}
            labelFormatter={(label: string) => label}
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              fontSize: '12px',
            }}
          />
          <Legend wrapperStyle={{ fontSize: '11px' }} iconSize={10} />
          <Bar dataKey="ativos" fill="#10b981" name="Ativos" radius={[4, 4, 0, 0]}>
            <LabelList
              dataKey="ativos"
              position="top"
              fontSize={9}
              fill="#10b981"
              offset={2}
              formatter={(v: number) => formatCompact(v)}
            />
          </Bar>
          <Bar dataKey="passivosAbs" fill="#ef4444" name="Passivos" radius={[4, 4, 0, 0]}>
            <LabelList
              dataKey="passivosAbs"
              position="top"
              fontSize={9}
              fill="#ef4444"
              offset={2}
              formatter={(v: number) => formatCompact(v)}
            />
          </Bar>
          <Line
            type="monotone"
            dataKey="plChart"
            stroke="#3b82f6"
            strokeWidth={2}
            name="Patrimônio Líquido"
            dot={{ r: 3 }}
          >
            <LabelList
              dataKey="pl"
              position="top"
              fontSize={9}
              fill="#3b82f6"
              offset={8}
              formatter={(v: number) => formatCompact(v)}
            />
          </Line>
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}
