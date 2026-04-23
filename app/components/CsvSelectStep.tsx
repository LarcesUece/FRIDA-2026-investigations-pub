import React from "react";
import styles from "./CsvColumnSelector.module.css";

interface Props {
  columns: string[];
  selected: string[];
  checkboxRenderMs: number | null;
  onSelect: (selected: string[]) => void;
  onBack: () => void;
  onConfirm: () => void;
  formatCheckboxRenderTime: (ms: number | null) => string;
}

export default function CsvSelectStep({
  columns, selected, checkboxRenderMs, onSelect, onBack, onConfirm, formatCheckboxRenderTime
}: Props) {
  function handleCheck(col: string) {
    if (selected.includes(col)) {
      onSelect(selected.filter(c => c !== col));
    } else {
      onSelect([...selected, col]);
    }
  }
  return (
    <>
      <h2 className={styles.sectionTitle}>Selecionar colunas</h2>
      <p className={styles.sectionText}>Escolha as colunas que devem ser anonimizadas.</p>
      <div className={styles.fileStatus}>
        <div className={styles.fileLine}>
          Quantidade de colunas: <span className={styles.fileLineStrong}>{columns.length}</span>
        </div>
        <div className={styles.fileLine}>
          Tempo para renderizar os checkboxes:{" "}
          <span className={styles.fileLineStrong}>{formatCheckboxRenderTime(checkboxRenderMs)}</span>
        </div>
      </div>
      {checkboxRenderMs === null ? (
        <div style={{ textAlign: "center", margin: "16px 0" }}>Renderizando colunas...</div>
      ) : (
        <div className={styles.columnList}>
          {columns.map((col) => (
            <label key={col} className={styles.columnItem}>
              <input
                type="checkbox"
                checked={selected.includes(col)}
                onChange={() => handleCheck(col)}
              />
              <span>{col}</span>
            </label>
          ))}
        </div>
      )}
      <div className={styles.footerActions}>
        <button className={styles.button} onClick={onBack}>
          Voltar
        </button>
        <button
          className={styles.button}
          onClick={onConfirm}
          disabled={selected.length === 0 || checkboxRenderMs === null}
        >
          Confirmar
        </button>
      </div>
    </>
  );
}