"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  { href: "/test", label: "Test Input" },
  { href: "/results", label: "Results" },
  { href: "/meals", label: "Meals" },
  { href: "/food", label: "Food" },
];

export function Logo() {
  return (
    <Link href="/" className="logo text-2xl leading-none" aria-label="Panel to Table home">
      <span className="text-[var(--forest)]">Panel </span>
      <span className="italic text-[var(--clay-bright)]">to</span>
      <span className="text-[var(--forest)]"> Table</span>
    </Link>
  );
}

export function SiteHeader() {
  const path = usePathname();
  const landing = path === "/";

  return (
    <header className="flex items-center justify-between gap-4">
      <Logo />
      {landing ? (
        <Link href="/test" className="btn btn-forest px-5 py-2 text-sm">Start</Link>
      ) : (
        <nav className="flex flex-wrap justify-end gap-x-4 gap-y-2 text-sm">
          {LINKS.map((link) => (
            <Link key={link.href} href={link.href} aria-current={path === link.href ? "page" : undefined}>
              {link.label}
            </Link>
          ))}
        </nav>
      )}
    </header>
  );
}
