import Link from "next/link";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-gray-50 flex flex-col">

      {/* Navbar */}
      <nav className="w-full px-8 py-5 flex items-center justify-between border-b border-gray-100 bg-white">
        <span className="text-lg font-bold text-teal-700 tracking-tight">CaForB</span>
        <Link
          href="/assessment"
          className="px-4 py-2 text-sm font-semibold text-white bg-teal-600 rounded-lg hover:bg-teal-700 transition"
        >
          Start Assessment
        </Link>
      </nav>

      {/* Hero */}
      <section className="flex-1 flex flex-col items-center justify-center text-center px-4 py-24">
        <span className="text-xs font-semibold uppercase tracking-widest text-teal-600 bg-teal-50 px-3 py-1 rounded-full mb-6">
          AI-Powered Innovation Intelligence
        </span>
        <h1 className="text-5xl font-bold text-gray-900 leading-tight max-w-2xl mb-6">
          Turn your company's context into a{" "}
          <span className="text-teal-600">strategic roadmap</span>
        </h1>
        <p className="text-lg text-gray-500 max-w-xl mb-10 leading-relaxed">
          Answer 5 short sections about your business. Get a personalised
          innovation maturity score, ranked opportunities, and actionable next steps — in under 2 minutes.
        </p>
        <Link
          href="/assessment"
          className="px-8 py-4 text-base font-semibold text-white bg-teal-600 rounded-xl hover:bg-teal-700 transition shadow-lg shadow-teal-200"
        >
          Start Free Assessment →
        </Link>
      </section>

      {/* Feature strip */}
      <section className="w-full border-t border-gray-100 bg-white py-10 px-8">
        <div className="max-w-4xl mx-auto grid grid-cols-3 gap-8 text-center">
          {[
            { icon: "🎯", title: "Context-aware", desc: "Tailored to your sector, size, and strategic goals" },
            { icon: "⚡", title: "Instant results", desc: "AI analysis powered by a fine-tuned LLM" },
            { icon: "📋", title: "Actionable output", desc: "Scored opportunities with timeframes and difficulty ratings" },
          ].map(({ icon, title, desc }) => (
            <div key={title}>
              <div className="text-3xl mb-3">{icon}</div>
              <div className="text-sm font-semibold text-gray-800 mb-1">{title}</div>
              <div className="text-xs text-gray-500">{desc}</div>
            </div>
          ))}
        </div>
      </section>

    </main>
  );
}