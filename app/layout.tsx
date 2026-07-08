import "./globals.css";

export const metadata = {
  title: "Anonimização de Dados CSV",
  description: "App bonito para anonimizar colunas do seu arquivo CSV",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-br">
      <body>
        {children}
      </body>
    </html>
  );
}