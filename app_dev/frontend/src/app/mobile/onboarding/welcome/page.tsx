'use client';

/**
 * Tela de boas-vindas — primeiro acesso
 * F.03: headline + 3 bullets + 2 CTAs + "Pular"
 */

import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Wallet, Target, TrendingUp } from 'lucide-react';

const ONBOARDING_PULADO_KEY = 'onboarding_pulado';

export default function WelcomePage() {
  const router = useRouter();

  const markPular = () => {
    if (typeof window !== 'undefined') {
      localStorage.setItem(ONBOARDING_PULADO_KEY, 'true');
    }
    router.push('/mobile/dashboard');
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-dvh p-8 text-center">
      <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mb-8">
        <Wallet className="w-8 h-8 text-primary" />
      </div>
      <h1 className="text-2xl font-bold mb-4">Bem-vindo ao FinUp</h1>
      <ul className="text-sm text-muted-foreground space-y-3 mb-10 text-left max-w-xs">
        <li className="flex items-center gap-2">
          <span className="text-primary">✓</span>
          Veja para onde vai seu dinheiro todo mês
        </li>
        <li className="flex items-center gap-2">
          <Target className="w-4 h-4 text-primary shrink-0" />
          Planeje sua aposentadoria e metas
        </li>
        <li className="flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-primary shrink-0" />
          Acompanhe seus investimentos em um lugar só
        </li>
      </ul>
      <div className="w-full max-w-xs space-y-3">
        <Link href="/mobile/onboarding/choose-path" className="block">
          <Button size="lg" className="w-full">
            Começar →
          </Button>
        </Link>
        <Button variant="ghost" size="sm" className="w-full" onClick={markPular}>
          Pular por agora
        </Button>
      </div>
    </div>
  );
}
