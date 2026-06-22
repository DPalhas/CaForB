"use client";

import { useQuery } from "@apollo/client/react";
import { useParams, useRouter } from "next/navigation";
import { GET_INSIGHT } from "@/lib/graphql/queries";
import ScoreCard from "./components/ScoreCard";
import OpportunitiesList from "./components/OpportunitiesList";
import NextStepsList from "./components/NextStepsList";
import WeaknessesList from "./components/WeaknessesList";
import ResultsSkeleton from "./components/ResultsSkeleton";

export default function ResultsPage() {
  const params = useParams();
  const router = useRouter();
  const id = parseInt(params.id as string, 10);

  const { data, loading, error } = useQuery(GET_INSIGHT, {
    variables: { id },
  });

  const insight = data?.getInsight;

  return (
    <main className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="w-full max-w-2xl mx-auto">

        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-2xl font-bold text-gray-900">Your Innovation Assessment</h1>
          <p className="text-sm text-gray-500 mt-1">
            {loading ? "Generating your personalised strategy..." : `Analysis #${id}`}
          </p>
        </div>

        {/* Loading state */}
        {loading && (
          <div className="flex flex-col items-center gap-4 mb-8">
            <div className="w-10 h-10 border-4 border-teal-600 border-t-transparent rounded-full animate-spin" />
            <p className="text-sm text-gray-500">Analysing your company profile with AI...</p>
          </div>
        )}
        {loading && <ResultsSkeleton />}

        {/* Error state */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
            <p className="text-red-700 font-medium">Something went wrong loading your results.</p>
            <p className="text-red-500 text-sm mt-1">{error.message}</p>
            <button
              onClick={() => router.push("/assessment")}
              className="mt-4 px-4 py-2 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
            >
              Try Again
            </button>
          </div>
        )}

        {/* Results */}
        {insight && (
          <div className="flex flex-col gap-6">

            {/* Score */}
            {insight.innovationScore !== null && (
              <ScoreCard score={insight.innovationScore} />
            )}

            {/* Opportunities */}
            <OpportunitiesList opportunities={insight.opportunities} />

            {/* Next Steps */}
            <NextStepsList steps={insight.nextSteps} />

            {/* Weaknesses */}
            <WeaknessesList weaknesses={insight.keyWeaknesses} />

            {/* CTA */}
            <div className="text-center pt-4 pb-8">
              <button
                onClick={() => router.push("/assessment")}
                className="px-6 py-3 text-sm font-semibold text-white bg-teal-600 rounded-xl hover:bg-teal-700 transition"
              >
                Run Another Assessment →
              </button>
            </div>
          </div>
        )}

      </div>
    </main>
  );
}