/**
 * MonthYearPicker - Seletor de Mês e Ano
 * Componente reutilizável para seleção de período (mês/ano)
 */

interface MonthYearPickerProps {
  months: string[];
  years: number[];
  selectedMonth: string;
  selectedYear: number;
  onMonthChange: (month: string) => void;
  onYearChange: (year: number) => void;
  required?: boolean;
}

export function MonthYearPicker({
  months,
  years,
  selectedMonth,
  selectedYear,
  onMonthChange,
  onYearChange,
  required = false
}: MonthYearPickerProps) {
  return (
    <div className="mb-6">
      <label className="block text-sm font-bold text-gray-900 mb-2">
        Período da Fatura {required && <span className="text-red-500">*</span>}
      </label>
      <div className="flex gap-3">
        <div className="relative w-32">
          <select 
            value={selectedYear}
            onChange={(e) => onYearChange(Number(e.target.value))}
            className="w-full px-4 py-3 border border-gray-200 rounded-xl text-gray-700 font-medium appearance-none cursor-pointer hover:border-gray-300 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
          >
            {years.map((year) => (
              <option key={year} value={year}>{year}</option>
            ))}
          </select>
          <svg className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
          </svg>
        </div>
        <div className="relative flex-1">
          <select 
            value={selectedMonth}
            onChange={(e) => onMonthChange(e.target.value)}
            className="w-full px-4 py-3 border border-gray-200 rounded-xl text-gray-700 font-medium appearance-none cursor-pointer hover:border-gray-300 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
          >
            {months.map((month) => (
              <option key={month} value={month}>{month}</option>
            ))}
          </select>
          <svg className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
          </svg>
        </div>
      </div>
    </div>
  );
}
