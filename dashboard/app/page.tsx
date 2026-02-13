'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { monthlyData, incomeSources, expenseSources, totalIncome, totalExpenses } from '@/lib/constants';

export default function InsightsPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'income' | 'expenses' | 'budget'>('income');
  const [hoveredBar, setHoveredBar] = useState<number | null>(null);
  const [selectedMonth, setSelectedMonth] = useState('Aug');
  const [selectedYear, setSelectedYear] = useState(2024);

  const maxHeight = Math.max(...monthlyData.map(d => d.income));
  
  // Função para formatar números de forma consistente
  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US').format(num);
  };
  
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  
  // Gerar meses com anos (últimos 6 meses + próximos 6 meses)
  const monthsWithYears = [
    ...months.slice(-6).map(m => ({ month: m, year: 2023 })),
    ...months.map(m => ({ month: m, year: 2024 })),
    ...months.slice(0, 6).map(m => ({ month: m, year: 2025 }))
  ];

  return (
    <div className="bg-gray-50 min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-md mx-auto">
        
        {/* Header */}
        <header className="bg-white rounded-t-3xl px-6 py-4 flex items-center justify-between border-b border-gray-100">
          <button 
            onClick={() => router.back()}
            className="text-gray-700 hover:text-gray-900 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7"></path>
            </svg>
          </button>
          <h1 className="text-lg font-bold text-gray-800">Insights</h1>
          <button className="text-sm font-semibold text-gray-700 hover:text-gray-900 transition-colors">
            Download
          </button>
        </header>
        
        {/* Date */}
        <div className="bg-white px-6 py-2">
          <p className="text-xs text-gray-400 text-right">{selectedMonth}. {selectedYear}</p>
        </div>
        
        {/* Month Selector (Horizontal Scroll) */}
        <div className="bg-white border-b border-gray-100">
          <div className="flex gap-2 px-6 py-3 overflow-x-auto scrollbar-hide">
            {monthsWithYears.map((item, index) => (
              <button
                key={`${item.month}-${item.year}-${index}`}
                onClick={() => {
                  setSelectedMonth(item.month);
                  setSelectedYear(item.year);
                }}
                className={`flex-shrink-0 w-16 py-2.5 rounded-xl text-center transition-all ${
                  selectedMonth === item.month && selectedYear === item.year
                    ? 'bg-gray-900 text-white shadow-lg'
                    : 'bg-gray-50 text-gray-500 hover:bg-gray-100'
                }`}
              >
                <p className="text-xs font-semibold">{item.month.toUpperCase()}</p>
                <p className={`text-[10px] mt-0.5 ${
                  selectedMonth === item.month && selectedYear === item.year
                    ? 'text-gray-300'
                    : 'text-gray-400'
                }`}>
                  {item.year}
                </p>
              </button>
            ))}
          </div>
        </div>
        
        {/* Main Content */}
        <div className="bg-white px-6 pb-6">
          
          {/* Wallet Balance Card */}
          <div className="mb-6">
            <p className="text-xs text-gray-500 mb-1">Wallet Balance</p>
            <div className="flex items-baseline gap-2 mb-3">
              <h2 className="text-3xl font-bold text-gray-900">1,000,000</h2>
              <span className="text-sm font-semibold text-green-500">+2.5%</span>
            </div>
            
            {/* Tabs */}
            <div className="flex gap-6 border-b border-gray-200">
              <button 
                onClick={() => setActiveTab('income')}
                className={`pb-2 text-sm font-semibold transition-colors ${
                  activeTab === 'income'
                    ? 'text-gray-900 border-b-2 border-gray-900'
                    : 'text-gray-400 hover:text-gray-600'
                }`}
              >
                Income
              </button>
              <button 
                onClick={() => setActiveTab('expenses')}
                className={`pb-2 text-sm font-medium transition-colors ${
                  activeTab === 'expenses'
                    ? 'text-gray-900 border-b-2 border-gray-900'
                    : 'text-gray-400 hover:text-gray-600'
                }`}
              >
                Expenses
              </button>
              <button 
                onClick={() => setActiveTab('budget')}
                className={`pb-2 text-sm font-medium transition-colors ${
                  activeTab === 'budget'
                    ? 'text-gray-900 border-b-2 border-gray-900'
                    : 'text-gray-400 hover:text-gray-600'
                }`}
              >
                Budget
              </button>
            </div>
          </div>
          
          {/* Income Trend Chart */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-bold text-gray-900">Income Trend</h3>
              <p className="text-lg font-bold text-gray-900">₦{formatNumber(totalIncome)}</p>
            </div>
            <p className="text-xs text-gray-400 mb-4">Weekly Comparison</p>
            
            {/* Bar Chart */}
            <div className="relative">
              <div className="flex items-end justify-between gap-4 h-40 px-2">
                {monthlyData.map((data, index) => {
                  // Alturas fixas em pixels (como no HTML)
                  const heights = [
                    { income: 65, expense: 50 },  // Jan
                    { income: 80, expense: 62 },  // Feb
                    { income: 95, expense: 75 },  // Mar
                    { income: 72, expense: 58 },  // Apr
                    { income: 110, expense: 88 }, // May
                    { income: 125, expense: 98 }, // Jun
                    { income: 88, expense: 70 },  // Jul
                  ];
                  
                  return (
                    <div 
                      key={data.month}
                      className="flex items-end gap-1 flex-1 relative group"
                      onMouseEnter={() => setHoveredBar(index)}
                      onMouseLeave={() => setHoveredBar(null)}
                    >
                      <div 
                        className="w-2 bg-gray-400 rounded-t-sm cursor-pointer transition-opacity hover:opacity-80"
                        style={{ height: `${heights[index].expense}px` }}
                      />
                      <div 
                        className="w-2 bg-gray-900 rounded-t-sm cursor-pointer transition-opacity hover:opacity-80"
                        style={{ height: `${heights[index].income}px` }}
                      />
                      
                      {/* Tooltip */}
                      {hoveredBar === index && (
                        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 bg-gray-900 text-white text-xs px-3 py-2 rounded-lg shadow-lg whitespace-nowrap z-10">
                          <div className="font-semibold mb-1">{data.month} 2024</div>
                          <div className="flex items-center gap-2 mb-1">
                            <div className="w-2 h-2 bg-gray-400 rounded-sm"></div>
                            <span className="text-[11px]">Expenses: ₦{formatNumber(data.expenses)}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <div className="w-2 h-2 bg-white rounded-sm"></div>
                            <span className="text-[11px]">Income: ₦{formatNumber(data.income)}</span>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
              
              {/* Month Labels */}
              <div className="flex justify-between px-2 mt-2">
                {monthlyData.map(data => (
                  <span key={data.month} className="text-[9px] text-gray-400 flex-1 text-center">
                    {data.month}
                  </span>
                ))}
              </div>
            </div>
            
            {/* Legend */}
            <div className="flex items-center justify-center gap-6 mt-6">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-sm bg-gray-400"></div>
                <span className="text-xs text-gray-600">Expenses</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-sm bg-gray-900"></div>
                <span className="text-xs text-gray-600">Income</span>
              </div>
            </div>
          </div>
          
          {/* Income Sources */}
          <div className="mb-6">
            <h3 className="text-sm font-bold text-gray-900 mb-4">{activeTab === 'income' ? 'Income Sources' : 'Expense Categories'}</h3>
            
            <div className="flex items-center gap-6">
              {/* Donut Chart */}
              <div className="relative w-32 h-32 flex-shrink-0">
                <svg viewBox="0 0 200 200" className="transform -rotate-90 w-full h-full">
                  <circle cx="100" cy="100" r="70" fill="none" stroke="#F3F4F6" strokeWidth="28" />
                  
                  {activeTab === 'income' ? (
                    <>
                      {/* Income Sources - Salary 38% */}
                      <circle cx="100" cy="100" r="70" fill="none" stroke="#1F2937" strokeWidth="28"
                          strokeDasharray="167 440" strokeDashoffset="0" strokeLinecap="round" />
                      {/* Wages 23% */}
                      <circle cx="100" cy="100" r="70" fill="none" stroke="#4B5563" strokeWidth="28"
                          strokeDasharray="101 440" strokeDashoffset="-167" strokeLinecap="round" />
                      {/* Business 38% */}
                      <circle cx="100" cy="100" r="70" fill="none" stroke="#9CA3AF" strokeWidth="28"
                          strokeDasharray="167 440" strokeDashoffset="-268" strokeLinecap="round" />
                    </>
                  ) : (
                    <>
                      {/* Expense Categories - Food 23% */}
                      <circle cx="100" cy="100" r="70" fill="none" stroke="#1F2937" strokeWidth="28"
                          strokeDasharray="101 440" strokeDashoffset="0" strokeLinecap="round" />
                      {/* Transport 14% */}
                      <circle cx="100" cy="100" r="70" fill="none" stroke="#4B5563" strokeWidth="28"
                          strokeDasharray="62 440" strokeDashoffset="-101" strokeLinecap="round" />
                      {/* Shopping 20% */}
                      <circle cx="100" cy="100" r="70" fill="none" stroke="#9CA3AF" strokeWidth="28"
                          strokeDasharray="88 440" strokeDashoffset="-163" strokeLinecap="round" />
                      {/* Bills 17% */}
                      <circle cx="100" cy="100" r="70" fill="none" stroke="#6B7280" strokeWidth="28"
                          strokeDasharray="75 440" strokeDashoffset="-251" strokeLinecap="round" />
                    </>
                  )}
                </svg>
              </div>
              
              {/* Legend */}
              <div className="flex-1 space-y-2">
                {(activeTab === 'income' ? incomeSources : expenseSources).map((source) => (
                  <div key={source.name} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: source.color }}></div>
                      <span className="text-xs text-gray-600">{source.name}</span>
                    </div>
                    <span className={`text-xs font-semibold ${source.amount > 0 ? 'text-gray-900' : 'text-gray-400'}`}>
                      {source.amount > 0 ? `₦${formatNumber(source.amount)}` : '0.00'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
          
          {/* Recent Transactions */}
          <div className="border-t border-gray-100 pt-4">
            <h3 className="text-sm font-bold text-gray-900 mb-3">Recent Transactions</h3>
            <p className="text-xs text-gray-400 text-center py-4">No transactions yet</p>
          </div>
        </div>
        
        {/* Bottom Navigation */}
        <nav className="bg-white rounded-b-3xl px-6 py-4 flex items-center justify-around border-t border-gray-100">
          <button className="flex flex-col items-center gap-1 text-gray-400 hover:text-gray-900 transition-colors">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
            </svg>
            <span className="text-[10px] font-medium">Home</span>
          </button>
          <button className="flex flex-col items-center gap-1 text-gray-400 hover:text-gray-900 transition-colors">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"></path>
            </svg>
            <span className="text-[10px] font-medium">Card</span>
          </button>
          <button className="flex flex-col items-center gap-1 text-gray-900">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
            </svg>
            <span className="text-[10px] font-bold">Insights</span>
          </button>
        </nav>
      </div>
    </div>
  );
}
