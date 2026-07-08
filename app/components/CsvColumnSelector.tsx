'use client'
import React, { useState, useRef, useEffect } from "react";
import Papa from "papaparse";
import styles from "./CsvColumnSelector.module.css";
import CsvUploadStep from "./CsvUploadStep";
import CsvSelectStep from "./CsvSelectStep";
import CsvSummaryStep from "./CsvSummaryStep";

type FileAnalysis = {
  name: string;
  size: number;
  parseTime: number | null;
  headers: string[];
  delimiter: string | null;
  error: string | null;
};

export default function CsvColumnSelector() {
  const [phase, setPhase] = useState<"upload" | "select" | "summary">("upload");
  const [filesAnalysis, setFilesAnalysis] = useState<FileAnalysis[]>([]);
  const [filesList, setFilesList] = useState<{ name: string; size: number }[]>([]);
  const [columns, setColumns] = useState<string[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [error, setError] = useState<string>("");

  // Para medir render dos checkboxes
  const [checkboxRenderMs, setCheckboxRenderMs] = useState<number | null>(null);
  const selectStartRef = useRef<number | null>(null);

  // Controle de fases
  function resetAll() {
    setFilesList([]);
    setFilesAnalysis([]);
    setColumns([]);
    setSelected([]);
    setError("");
    setCheckboxRenderMs(null);
    selectStartRef.current = null;
  }
  function handleReset() { setPhase("upload"); resetAll(); }
  function handleNext() {
    setCheckboxRenderMs(null);
    selectStartRef.current = performance.now();
    setPhase("select");
  }
  function handleConfirm() { setPhase("summary"); }
  function handleBack() { setPhase("upload"); }

  // Analisar múltiplos arquivos, mostrar nome e tamanho de imediato
  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    setError("");
    setFilesList([]);
    setFilesAnalysis([]);
    setColumns([]);
    setSelected([]);
    setCheckboxRenderMs(null);
    selectStartRef.current = null;

    if (!e.target.files || e.target.files.length === 0) return;

    const files = Array.from(e.target.files);

    // Seta lista de nomes e tamanhos imediatamente!
    setFilesList(files.map(f => ({ name: f.name, size: f.size })));

    // processar todos os arquivos em paralelo (parse)
    const results: FileAnalysis[] = await Promise.all(files.map(file =>
      new Promise<FileAnalysis>(resolve => {
        const parseStart = performance.now();
        Papa.parse(file, {
          preview: 1,
          delimiter: "",
          skipEmptyLines: true,
          complete(results) {
            const parseTime = performance.now() - parseStart;
            const headers = (results.data?.[0] as string[]) || [];
            resolve({
              name: file.name,
              size: file.size,
              parseTime,
              headers,
              delimiter: results.meta.delimiter ?? null,
              error: results.errors?.[0]?.message ?? null,
            });
          },
          error(err) {
            resolve({
              name: file.name,
              size: file.size,
              parseTime: null,
              headers: [],
              delimiter: null,
              error: err.message,
            });
          }
        });
      })
    ));

    setFilesAnalysis(results);

    // Se todos deram certo e todos os headers são idênticos, define colunas
    if (results.every(r => !r.error)) {
      const allSameHeaders = results.every(r =>
        JSON.stringify(r.headers) === JSON.stringify(results[0].headers)
      );
      if (allSameHeaders) {
        setColumns(results[0].headers);
      }
    }
  }

  // Validação dos headers
  const headersIgual =
    filesAnalysis.length > 0 &&
    filesAnalysis.every(fa =>
      JSON.stringify(fa.headers) === JSON.stringify(filesAnalysis[0].headers)
    );

  const isMulti = filesAnalysis.length > 1;

  // Meça o tempo só quando for para a etapa de seleção
  useEffect(() => {
    if (phase === "select" && columns.length && checkboxRenderMs === null) {
      const raf = requestAnimationFrame(() => {
        if (selectStartRef.current !== null) {
          setCheckboxRenderMs(performance.now() - selectStartRef.current);
        }
      });
      return () => cancelAnimationFrame(raf);
    }
  }, [phase, columns.length, checkboxRenderMs]);

  return (
    <div className={styles.card}>
      <header className={styles.header}>
        <h1 className={styles.title}>Upload de Dataset</h1>
        <p className={styles.subtitle}>
          Faça upload de um ou mais arquivos CSV.<br />
          O sistema irá analisar cada arquivo, medir o tempo e comparar os headers.
        </p>
      </header>
      <section className={styles.panel}>
        {phase === "upload" && (
          <CsvUploadStep
            filesList={filesList}
            filesAnalysis={filesAnalysis}
            headersIgual={headersIgual}
            isMulti={isMulti}
            onFileChange={handleFileChange}
            onReset={handleReset}
            onNext={handleNext}
            error={error}
            columns={columns}
          />
        )}
        {phase === "select" && columns.length > 0 && (
          <CsvSelectStep
            columns={columns}
            selected={selected}
            checkboxRenderMs={checkboxRenderMs}
            onSelect={setSelected}
            onBack={handleBack}
            onConfirm={handleConfirm}
            formatCheckboxRenderTime={ms =>
              ms === null ? "carregando..." : `${ms.toFixed(2)} ms`
            }
          />
        )}
        {phase === "select" && columns.length === 0 && (
          <div className={styles.sectionText} style={{ textAlign: "center", margin: 32 }}>
            Carregando colunas...
          </div>
        )}
        {phase === "summary" && (
          <CsvSummaryStep
            selected={selected}
            onReset={handleReset}
          />
        )}
      </section>
    </div>
  );
}