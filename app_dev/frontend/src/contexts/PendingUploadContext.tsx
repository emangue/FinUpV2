'use client';

/**
 * Context para passar arquivo selecionado no FAB da bottom nav
 * para a tela de upload (fluxo: toca Upload → abre file picker → navega com arquivo)
 */
import React, { createContext, useContext, useState, useCallback } from 'react';

interface PendingUploadContextValue {
  pendingFile: File | null;
  setPendingFile: (file: File | null) => void;
  consumePendingFile: () => File | null;
}

const PendingUploadContext = createContext<PendingUploadContextValue | null>(null);

export function PendingUploadProvider({ children }: { children: React.ReactNode }) {
  const [pendingFile, setPendingFileState] = useState<File | null>(null);

  const consumePendingFile = useCallback(() => {
    const file = pendingFile;
    setPendingFileState(null);
    return file;
  }, [pendingFile]);

  const setPendingFile = useCallback((file: File | null) => {
    setPendingFileState(file);
  }, []);

  return (
    <PendingUploadContext.Provider
      value={{ pendingFile, setPendingFile, consumePendingFile }}
    >
      {children}
    </PendingUploadContext.Provider>
  );
}

export function usePendingUpload() {
  const ctx = useContext(PendingUploadContext);
  if (!ctx) {
    return {
      pendingFile: null,
      setPendingFile: () => {},
      consumePendingFile: () => null,
    };
  }
  return ctx;
}
