import type { Metadata } from 'next'
import '../styles/globals.css'

export const metadata: Metadata = {
  title: 'Aiteebar AI Security',
  description: 'AI-powered security analysis and threat intelligence platform',
  keywords: ['security', 'AI', 'threat detection', 'vulnerability assessment'],
  viewport: 'width=device-width, initial-scale=1',
  openGraph: {
    title: 'Aiteebar AI Security',
    description: 'AI-powered security analysis and threat intelligence platform',
    type: 'website',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <meta charSet="utf-8" />
        <meta name="theme-color" content="#0f172a" />
      </head>
      <body className="bg-slate-900 text-slate-100 antialiased">
        {children}
      </body>
    </html>
  )
}
