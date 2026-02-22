"use client"

import * as React from "react"
import DashboardLayout from "@/components/dashboard-layout"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

export default function APIPage() {
  return (
    <DashboardLayout>
      <div className="flex flex-1 flex-col gap-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold">API</h1>
            <p className="text-muted-foreground">
              Documentação e informações da API do sistema
            </p>
          </div>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Documentação da API</CardTitle>
            <CardDescription>
              Acesse a documentação interativa do backend FastAPI
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="rounded-lg border p-4 bg-blue-50">
              <h3 className="font-semibold text-lg mb-2">Swagger UI - Documentação Interativa</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Interface completa com todos os endpoints da API, exemplos de requisições e respostas.
              </p>
              <a 
                href="http://localhost:8000/docs" 
                target="_blank" 
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
                Abrir Swagger UI
              </a>
            </div>

            <div className="rounded-lg border p-4">
              <h3 className="font-semibold text-lg mb-2">ReDoc - Documentação Alternativa</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Visualização limpa e organizada da documentação da API.
              </p>
              <a 
                href="http://localhost:8000/redoc" 
                target="_blank" 
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
                Abrir ReDoc
              </a>
            </div>

            <div className="rounded-lg border p-4 bg-gray-50">
              <h3 className="font-semibold text-lg mb-2">Informações Técnicas</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Backend URL:</span>
                  <code className="bg-gray-200 px-2 py-1 rounded">http://localhost:8000</code>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">API Version:</span>
                  <code className="bg-gray-200 px-2 py-1 rounded">v1</code>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Base Path:</span>
                  <code className="bg-gray-200 px-2 py-1 rounded">/api/v1</code>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Autenticação:</span>
                  <code className="bg-gray-200 px-2 py-1 rounded">JWT Bearer Token</code>
                </div>
              </div>
            </div>

            <div className="rounded-lg border p-4 bg-yellow-50">
              <h3 className="font-semibold text-lg mb-2">⚠️ Importante</h3>
              <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
                <li>O backend deve estar rodando na porta 8000</li>
                <li>Use o token JWT obtido no login para requisições autenticadas</li>
                <li>Consulte a documentação do Swagger para exemplos de uso</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
