import 'bootstrap/dist/css/bootstrap.min.css';
import 'styles/main-style.css';
import StickyHeader from '@components/Header/sticky-header';
import React, { ReactNode } from 'react';
import NavBar from '@components/Navigation/NavBar';
import Script from 'next/script';

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="shortcut icon" href="img/favicon.ico" />
        <title>Future Site of CSLC Tutoring Portal</title>

        {/* Globally expose bootstrap-js on client components */}
        <Script
          src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/js/bootstrap.bundle.min.js"
          integrity="sha384-ENjdO4Dr2bkBIFxQpeoTz1HIcje39Wm4jDKdf19U8gI4ddQ3GYNS7NTKfAdVQSZe"
          crossOrigin="anonymous"
        />
      </head>

      <body className="d-flex flex-column min-vh-100">
        <StickyHeader />
        <NavBar />

        <div id="content" className="container-fluid">
          {children}
        </div>
        <footer className="mt-auto" />
      </body>
    </html>
  );
}
