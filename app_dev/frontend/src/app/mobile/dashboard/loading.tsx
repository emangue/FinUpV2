export default function DashboardLoading() {
  return (
    <div className="flex flex-col h-screen bg-gray-50 animate-pulse">
      {/* Month scroll skeleton */}
      <div className="sticky top-0 z-20 bg-white border-b border-gray-200 h-14 flex items-center px-4 gap-3">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="h-8 w-14 bg-gray-100 rounded-full" />
        ))}
        <div className="ml-auto flex gap-1">
          <div className="h-9 w-9 bg-gray-100 rounded-full" />
          <div className="h-9 w-9 bg-gray-100 rounded-full" />
        </div>
      </div>

      {/* YTD toggle skeleton */}
      <div className="flex justify-center py-4 bg-white border-b border-gray-200">
        <div className="h-9 w-52 bg-gray-100 rounded-full" />
      </div>

      {/* Content skeleton */}
      <div className="flex-1 overflow-hidden bg-white px-6 pt-6 pb-6 space-y-4">
        {/* Tabs */}
        <div className="flex gap-6 border-b border-gray-200 pb-2">
          <div className="h-5 w-20 bg-gray-200 rounded" />
          <div className="h-5 w-20 bg-gray-100 rounded" />
        </div>

        {/* Resumo card */}
        <div className="rounded-xl border border-gray-200 p-4 space-y-3">
          <div className="flex justify-between">
            <div className="h-4 w-24 bg-gray-100 rounded" />
            <div className="h-4 w-16 bg-gray-100 rounded" />
          </div>
          <div className="grid grid-cols-3 gap-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-14 bg-gray-100 rounded-xl" />
            ))}
          </div>
        </div>

        {/* Chart skeleton */}
        <div className="rounded-xl border border-gray-200 p-4">
          <div className="h-4 w-32 bg-gray-100 rounded mb-4" />
          <div className="h-40 bg-gray-100 rounded-lg" />
        </div>

        {/* Despesas/Receitas skeleton */}
        <div className="rounded-xl border border-gray-200 p-4 space-y-3">
          <div className="h-4 w-40 bg-gray-100 rounded" />
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex items-center gap-3">
              <div className="h-3 w-3 bg-gray-200 rounded-full" />
              <div className="flex-1 h-3 bg-gray-100 rounded" />
              <div className="h-3 w-16 bg-gray-100 rounded" />
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
