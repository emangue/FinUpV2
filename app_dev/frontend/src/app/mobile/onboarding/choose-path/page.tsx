'use client';

/**
 * Escolher caminho: "Meus dados" (upload) vs "Explorar" (demo)
 * F.04
 */

import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Upload, Sparkles } from 'lucide-react';

const apiUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export default function ChoosePathPage() {
  const router = useRouter();

  const handleMeusDados = () => {
    router.push('/mobile/upload');
  };

  const handleExplorar = async () => {
    try {
      const res = await fetch(`${apiUrl}/api/v1/onboarding/modo-demo`, {
        method: 'POST',
        credentials: 'include',
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Erro ao ativar modo demo');
      router.push('/mobile/dashboard');
    } catch (err) {
      console.error(err);
      router.push('/mobile/dashboard');
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-dvh p-8">
      <h1 className="text-xl font-bold mb-2">Como quer começar?</h1>
      <p className="text-sm text-muted-foreground mb-8 text-center">
        Escolha uma opção para explorar o app
      </p>
      <div className="w-full max-w-xs space-y-4">
        <Button
          size="lg"
          variant="outline"
          className="w-full h-20 flex flex-col gap-1"
          onClick={handleMeusDados}
        >
          <Upload className="w-6 h-6" />
          <span>Começar com meus dados</span>
          <span className="text-xs font-normal text-muted-foreground">
            Suba seu extrato ou fatura
          </span>
        </Button>
        <Button
          size="lg"
          className="w-full h-20 flex flex-col gap-1"
          onClick={handleExplorar}
        >
          <Sparkles className="w-6 h-6" />
          <span>Explorar primeiro</span>
          <span className="text-xs font-normal text-primary-foreground/80">
            Dados fictícios para conhecer o app
          </span>
        </Button>
      </div>
    </div>
  );
}
