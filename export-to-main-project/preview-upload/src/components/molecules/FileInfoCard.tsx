import { FileInfo } from '@/types';
import { formatCurrency } from '@/lib/constants';

interface FileInfoCardProps {
  fileInfo: FileInfo;
}

export default function FileInfoCard({ fileInfo }: FileInfoCardProps) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-4 animate-fade-in">
      <div className="flex items-center gap-2 mb-3">
        <svg className="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
        <h2 className="font-semibold text-gray-900">Informações do Arquivo</h2>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="text-xs text-gray-500 mb-1">Banco</p>
          <p className="font-semibold text-gray-900">{fileInfo.banco}</p>
        </div>

        <div>
          <p className="text-xs text-gray-500 mb-1">Cartão</p>
          <p className="font-semibold text-gray-900">{fileInfo.cartao}</p>
        </div>

        <div className="col-span-2">
          <p className="text-xs text-gray-500 mb-1">Arquivo</p>
          <p className="font-semibold text-gray-900 truncate">{fileInfo.arquivo}</p>
        </div>

        <div className="col-span-2">
          <p className="text-xs text-gray-500 mb-1">Mês Fatura</p>
          <p className="font-semibold text-gray-900">{fileInfo.mesFatura}</p>
        </div>

        <div>
          <p className="text-xs text-gray-500 mb-1">Total de Lançamentos</p>
          <p className="font-semibold text-gray-900">{fileInfo.totalLancamentos}</p>
        </div>

        <div>
          <p className="text-xs text-gray-500 mb-1">Soma Total</p>
          <p className="font-semibold text-red-600">{formatCurrency(fileInfo.somaTotal)}</p>
        </div>
      </div>
    </div>
  );
}
