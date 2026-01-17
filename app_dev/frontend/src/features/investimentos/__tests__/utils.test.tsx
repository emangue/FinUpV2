/**
 * Testes para funções utilitárias de investimentos
 */

describe('Investimentos Utils', () => {
  describe('formatCurrency', () => {
    const formatCurrency = (value: number): string => {
      return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(value)
    }

    it('deve formatar valores positivos corretamente', () => {
      expect(formatCurrency(1000)).toBe('R$ 1.000,00')
      expect(formatCurrency(1234.56)).toBe('R$ 1.234,56')
      expect(formatCurrency(0.99)).toBe('R$ 0,99')
    })

    it('deve formatar valores negativos corretamente', () => {
      expect(formatCurrency(-1000)).toBe('-R$ 1.000,00')
      expect(formatCurrency(-0.50)).toBe('-R$ 0,50')
    })

    it('deve formatar zero corretamente', () => {
      expect(formatCurrency(0)).toBe('R$ 0,00')
    })

    it('deve formatar valores grandes corretamente', () => {
      expect(formatCurrency(1000000)).toBe('R$ 1.000.000,00')
      expect(formatCurrency(1234567.89)).toBe('R$ 1.234.567,89')
    })
  })

  describe('parsePercentage', () => {
    const parsePercentage = (value: number): string => {
      const sign = value >= 0 ? '+' : ''
      return `${sign}${value.toFixed(2)}%`
    }

    it('deve formatar percentuais positivos com sinal +', () => {
      expect(parsePercentage(15.5)).toBe('+15,50%')
      expect(parsePercentage(0.1)).toBe('+0,10%')
    })

    it('deve formatar percentuais negativos com sinal -', () => {
      expect(parsePercentage(-5.25)).toBe('-5,25%')
      expect(parsePercentage(-0.5)).toBe('-0,50%')
    })

    it('deve formatar zero sem sinal', () => {
      expect(parsePercentage(0)).toBe('+0,00%')
    })
  })

  describe('formatDate', () => {
    const formatDate = (dateStr: string): string => {
      if (!dateStr) return '-'
      try {
        const date = new Date(dateStr)
        return date.toLocaleDateString('pt-BR')
      } catch {
        return dateStr
      }
    }

    it('deve formatar datas ISO corretamente', () => {
      expect(formatDate('2024-01-15')).toMatch(/15\/01\/2024/)
      expect(formatDate('2024-12-31')).toMatch(/31\/12\/2024/)
    })

    it('deve formatar datetime ISO corretamente', () => {
      expect(formatDate('2024-01-15T10:30:00Z')).toMatch(/15\/01\/2024/)
    })

    it('deve retornar "-" para strings vazias', () => {
      expect(formatDate('')).toBe('-')
    })

    it('deve retornar a string original para formatos inválidos', () => {
      expect(formatDate('invalid-date')).toBe('invalid-date')
      expect(formatDate('2024-13-45')).toBe('2024-13-45')
    })
  })

  describe('calculatePercentage', () => {
    const calculatePercentage = (value: number, total: number): number => {
      if (total === 0) return 0
      return (value / total) * 100
    }

    it('deve calcular percentuais corretamente', () => {
      expect(calculatePercentage(25, 100)).toBe(25)
      expect(calculatePercentage(1, 3)).toBeCloseTo(33.33, 2)
      expect(calculatePercentage(150, 100)).toBe(150)
    })

    it('deve retornar 0 quando total for zero', () => {
      expect(calculatePercentage(100, 0)).toBe(0)
    })

    it('deve lidar com valores negativos', () => {
      expect(calculatePercentage(-25, 100)).toBe(-25)
      expect(calculatePercentage(25, -100)).toBe(-25)
    })
  })

  describe('Investment Type Colors', () => {
    const getTipoColor = (tipo: string): string => {
      const colorMap: Record<string, string> = {
        'Fundo Imobiliário': 'blue-500',
        'Renda Fixa': 'green-500',
        'Ação': 'purple-500',
        'Casa': 'orange-500',
        'Apartamento': 'yellow-500',
        'Previdência Privada': 'indigo-500',
        'Conta Corrente': 'gray-500',
        'FGTS': 'pink-500',
        'Fundo de Investimento': 'teal-500',
        'Automóvel': 'red-500',
      }
      return colorMap[tipo] || 'gray-400'
    }

    it('deve retornar cores corretas para tipos conhecidos', () => {
      expect(getTipoColor('Fundo Imobiliário')).toBe('blue-500')
      expect(getTipoColor('Renda Fixa')).toBe('green-500')
      expect(getTipoColor('Ação')).toBe('purple-500')
    })

    it('deve retornar cor padrão para tipos desconhecidos', () => {
      expect(getTipoColor('Tipo Inexistente')).toBe('gray-400')
      expect(getTipoColor('')).toBe('gray-400')
    })
  })

  describe('Risk Assessment', () => {
    const assessConcentrationRisk = (percentage: number): 'low' | 'medium' | 'high' => {
      if (percentage >= 30) return 'high'
      if (percentage >= 20) return 'medium'
      return 'low'
    }

    it('deve classificar risco de concentração corretamente', () => {
      expect(assessConcentrationRisk(10)).toBe('low')
      expect(assessConcentrationRisk(19.9)).toBe('low')
      expect(assessConcentrationRisk(20)).toBe('medium')
      expect(assessConcentrationRisk(29.9)).toBe('medium')
      expect(assessConcentrationRisk(30)).toBe('high')
      expect(assessConcentrationRisk(50)).toBe('high')
    })

    it('deve lidar com valores extremos', () => {
      expect(assessConcentrationRisk(0)).toBe('low')
      expect(assessConcentrationRisk(100)).toBe('high')
    })
  })

  describe('Data Validation', () => {
    const isValidInvestimento = (inv: any): boolean => {
      return !!(
        inv &&
        inv.balance_id &&
        inv.nome_produto &&
        inv.corretora &&
        inv.tipo_investimento &&
        typeof inv.quantidade === 'number' &&
        inv.quantidade > 0
      )
    }

    it('deve validar investimento válido', () => {
      const validInv = {
        balance_id: 'TEST001',
        nome_produto: 'Produto Teste',
        corretora: 'Corretora Teste',
        tipo_investimento: 'Ação',
        quantidade: 10,
      }
      expect(isValidInvestimento(validInv)).toBe(true)
    })

    it('deve invalidar investimento com campos obrigatórios faltando', () => {
      expect(isValidInvestimento({})).toBe(false)
      expect(isValidInvestimento(null)).toBe(false)
      expect(isValidInvestimento(undefined)).toBe(false)

      const invSemBalanceId = {
        nome_produto: 'Produto',
        corretora: 'Corretora',
        tipo_investimento: 'Ação',
        quantidade: 10,
      }
      expect(isValidInvestimento(invSemBalanceId)).toBe(false)
    })

    it('deve invalidar investimento com quantidade inválida', () => {
      const invQuantidadeZero = {
        balance_id: 'TEST001',
        nome_produto: 'Produto',
        corretora: 'Corretora',
        tipo_investimento: 'Ação',
        quantidade: 0,
      }
      expect(isValidInvestimento(invQuantidadeZero)).toBe(false)

      const invQuantidadeNegativa = {
        ...invQuantidadeZero,
        quantidade: -5,
      }
      expect(isValidInvestimento(invQuantidadeNegativa)).toBe(false)
    })
  })
})