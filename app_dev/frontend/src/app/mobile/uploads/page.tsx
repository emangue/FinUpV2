'use client';

/**
 * Central de Uploads - Mobile
 * Lista uploads realizados (confirmados) com opção de revisar
 */

import { MobileHeader } from '@/components/mobile/mobile-header';
import { UploadsPanel } from './components/uploads-panel';
import { useRequireAuth } from '@/core/hooks/use-require-auth';

export default function UploadsCentralPage() {
  const isAuth = useRequireAuth();

  if (!isAuth) {
    return (
      <div className="min-h-screen bg-gray-50">
        <MobileHeader title="Painel de Uploads" leftAction="back" />
        <div className="flex items-center justify-center h-[calc(100vh-64px)]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4" />
            <p className="text-gray-600">Verificando autenticação...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <MobileHeader title="Painel de Uploads" leftAction="back" />
      <div className="p-5">
        <UploadsPanel limit={10} />
      </div>
    </div>
  );
}
