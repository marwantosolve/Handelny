import Link from 'next/link';

const features = [
  {
    title: 'Multilingual RAG',
    description:
      'Answer customers in their own language, powered by retrieval over your documents.',
  },
  {
    title: 'Grounded, cited answers',
    description:
      'Every response is backed by real citations from your knowledge base — no hallucinations.',
  },
  {
    title: 'Fast setup',
    description:
      'Upload your docs, configure an agent, and go live in minutes — no ML expertise required.',
  },
];

export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <span className="text-lg font-semibold text-slate-900">
            Handelny
          </span>
          <nav className="flex items-center gap-4 text-sm font-medium">
            <Link
              href="/login"
              className="text-slate-600 hover:text-slate-900"
            >
              Log in
            </Link>
            <Link
              href="/register"
              className="rounded-lg bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-500"
            >
              Get started
            </Link>
          </nav>
        </div>
      </header>

      <section className="flex-1 bg-gradient-to-b from-indigo-50 via-white to-white">
        <div className="mx-auto max-w-4xl px-6 py-24 text-center">
          <h1 className="text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
            Create AI Customer Support Agents From Your Documents
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-600">
            Handelny turns your knowledge base into a support agent that
            answers customer questions accurately, in any language, with
            sources attached.
          </p>
          <div className="mt-10 flex items-center justify-center gap-4">
            <Link
              href="/register"
              className="rounded-lg bg-indigo-600 px-6 py-3 text-base font-semibold text-white shadow-sm hover:bg-indigo-500"
            >
              Get started for free
            </Link>
            <Link
              href="/login"
              className="rounded-lg border border-slate-300 px-6 py-3 text-base font-semibold text-slate-700 hover:bg-slate-50"
            >
              Log in
            </Link>
          </div>
        </div>

        <div className="mx-auto max-w-5xl px-6 pb-24">
          <div className="grid gap-6 sm:grid-cols-3">
            {features.map((feature) => (
              <div
                key={feature.title}
                className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
              >
                <h3 className="text-lg font-semibold text-slate-900">
                  {feature.title}
                </h3>
                <p className="mt-2 text-sm text-slate-600">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <footer className="border-t border-slate-200 bg-white py-6 text-center text-sm text-slate-500">
        © {new Date().getFullYear()} Handelny. All rights reserved.
      </footer>
    </main>
  );
}
