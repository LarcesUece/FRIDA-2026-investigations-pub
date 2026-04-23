import CsvColumnSelector from "./components/CsvColumnSelector";
import styles from "./page.module.css";

export default function Page() {
  return (
    <main className={styles.page}>
      <div className={styles.pageContent}>
        <CsvColumnSelector />
      </div>
    </main>
  );
}