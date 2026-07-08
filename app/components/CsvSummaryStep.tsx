import React from "react";
import styles from "./CsvColumnSelector.module.css";

interface Props {
  selected: string[];
  onReset: () => void;
}

export default function CsvSummaryStep({ selected, onReset }: Props) {
  return (
    <div>
      <div className={styles.summaryBox}>
        <h2 className={styles.sectionTitle}>Colunas selecionadas</h2>
        <p className={styles.sectionText}>Confira o resultado e inicie um novo upload quando quiser.</p>
        <ul className={styles.simpleList}>
          {selected.map((col) => (
            <li key={col}>{col}</li>
          ))}
        </ul>
      </div>
      <div className={styles.footerActions}>
        <button className={styles.button} onClick={onReset}>
          Novo upload
        </button>
      </div>
    </div>
  );
}