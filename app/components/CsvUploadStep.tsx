import React from "react";
import styles from "./CsvColumnSelector.module.css";

interface FileAnalysis {
  name: string;
  size: number;
  parseTime: number | null;
  delimiter: string | null;
  error: string | null;
}
interface Props {
  filesList: { name: string; size: number }[];
  filesAnalysis: FileAnalysis[];
  headersIgual: boolean;
  isMulti: boolean;
  onFileChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onReset: () => void;
  onNext: () => void;
  error: string;
  columns: string[];
}
// helper
function getAnalysis(filesAnalysis: FileAnalysis[], name: string) {
  return filesAnalysis.find(fa => fa.name === name);
}

export default function CsvUploadStep({
  filesList, filesAnalysis, headersIgual, isMulti, onFileChange, onReset, onNext, error, columns,
}: Props) {
  return (
    <>
      <div className={styles.centered}>
        <label className={styles.filePicker}>
          Selecionar arquivo(s)
          <input
            type="file"
            accept=".csv"
            multiple
            onChange={onFileChange}
            className={styles.hiddenInput}
          />
        </label>
      </div>

      {filesList.length > 0 && (
        <div className={styles.fileStatus}>
          {filesList.map((f, idx) => {
            const fa = getAnalysis(filesAnalysis, f.name);
            return (
              <div key={f.name + idx} className={styles.fileLine}>
                <strong>{f.name}</strong> ({(f.size / 1024).toFixed(1)} KB) <br />
                {fa?.error ? (
                  <span style={{ color: 'red' }}>Erro: {fa?.error}</span>
                ) : (
                  <>
                    Tempo parse:{" "}
                    <span className={styles.fileLineStrong}>
                      {fa?.parseTime == null ? "aguardando leitura" : `${fa.parseTime.toFixed(2)} ms`}
                    </span>
                    <br />
                    Delimitador:{" "}
                    <span className={styles.fileLineStrong}>
                      {fa?.delimiter == null ? "aguardando leitura" : fa.delimiter}
                    </span>
                  </>
                )}
              </div>
            );
          })}
        </div>
      )}

      {filesAnalysis.length > 1 && (
        <div className={styles.headerStatus} style={{ color: headersIgual ? "#0a0" : "#b00" }}>
          Cabeçalhos são iguais? {headersIgual ? "SIM" : "NÃO"}
        </div>
      )}

      <div className={styles.footerActions}>
        <button className={styles.button} onClick={onReset}>Cancelar</button>
        <button
          className={styles.button}
          onClick={onNext}
          disabled={
            filesList.length === 0 ||
            filesAnalysis.length !== filesList.length ||
            filesAnalysis.some(fa => !!fa.error) ||
            !headersIgual ||
            !columns.length
          }
        >
          Continuar
        </button>
      </div>
      {error && <div className={styles.errorBox}>{error}</div>}
      <div className={styles.sectionText} style={{ marginTop: 12 }}>
        {isMulti
          ? "Você selecionou múltiplos arquivos. O relatório detalha cada arquivo e valida se todos os headers são idênticos, conforme solicitado."
          : "Para análise concorrente, segure Ctrl ou Shift e selecione vários arquivos."}
      </div>
    </>
  );
}