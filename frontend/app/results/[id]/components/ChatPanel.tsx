"use client";

import { useEffect, useRef, useState } from "react";
import { useMutation, useQuery } from "@apollo/client/react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ASK_INSIGHT, CHAT_SESSION } from "@/lib/graphql/chat";
import type { ChatTag, ReportSection } from "@/lib/types";
import { MessageSquare, X, Send, Sparkles, Loader2, Maximize2, Minimize2 } from "lucide-react";

interface ChatMessage {
  id: number;
  role: string;
  content: string;
  taggedOpportunityId?: string | null;
  taggedNextStepId?: string | null;
  createdAt: string;
}

interface ChatPanelProps {
  insightId: number;
  open: boolean;
  onClose: () => void;
  expanded: boolean;
  onToggleExpanded: () => void;
  pendingTag: ChatTag | null;
  onSetTag: (tag: ChatTag) => void;
  onConsumeTag: () => void;
  sections: ReportSection[];
}

export default function ChatPanel({
  insightId,
  open,
  onClose,
  expanded,
  onToggleExpanded,
  pendingTag,
  onSetTag,
  onConsumeTag,
  sections,
}: ChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [picker, setPicker] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  const { data, refetch } = useQuery(CHAT_SESSION, {
    variables: { insightId },
    skip: !open,
    fetchPolicy: "network-only",
  });

  const [askInsight] = useMutation(ASK_INSIGHT);

  useEffect(() => {
    const session = (data as any)?.chatSession;
    if (session) {
      setSessionId(session.id);
      setMessages(session.messages ?? []);
    } else if (data && !session) {
      setSessionId(null);
      setMessages([]);
    }
  }, [data]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, sending]);

  const handleSend = async () => {
    const text = input.trim();
    if (!text || sending) return;

    const taggedOpportunityId =
      pendingTag?.kind === "opportunity" ? pendingTag.id : undefined;
    const taggedNextStepId =
      pendingTag?.kind === "nextStep" ? pendingTag.id : undefined;
    const taggedWeakness =
      pendingTag?.kind === "weakness" ? pendingTag.label : undefined;

    setInput("");
    onConsumeTag();
    setSending(true);
    setError(null);

    try {
      await askInsight({
        variables: {
          insightId,
          message: text,
          taggedOpportunityId,
          taggedNextStepId,
          taggedWeakness,
          sessionId,
        },
      });
      await refetch();
    } catch {
      setError("Could not reach the AI. Please try again.");
      setInput(text);
    } finally {
      setSending(false);
    }
  };

  if (!open) return null;

  return (
    <div className={`fixed z-50 flex flex-col shadow-2xl shadow-black/50 overflow-hidden print:hidden ${expanded ? "top-0 right-0 h-full w-full lg:w-1/3 bg-stone-950 border-l border-stone-800" : "bottom-6 right-6 w-[min(24rem,calc(100vw-3rem))] glass-card rounded-3xl border border-stone-700/70"}`}>
      {/* Header */}
      <div className="flex items-center gap-3 px-4 py-3 border-b border-stone-800/80 bg-stone-900/40">
        <div className="w-8 h-8 rounded-xl bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-amber-400">
          <Sparkles className="w-4 h-4" />
        </div>
        <div className="flex-1">
          <h3 className="text-sm font-bold text-white">Ask about this report</h3>
          <p className="text-[10px] text-stone-500">Answers grounded in your assessment</p>
        </div>
        <button
          onClick={onToggleExpanded}
          className="p-1.5 rounded-lg text-stone-400 hover:text-white hover:bg-stone-800 transition"
          aria-label={expanded ? "Minimize chat" : "Expand chat"}
        >
          {expanded ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
        </button>
        <button
          onClick={onClose}
          className="p-1.5 rounded-lg text-stone-400 hover:text-white hover:bg-stone-800 transition"
          aria-label="Close chat"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Messages */}
      <div
        ref={scrollRef}
        className={`flex-1 ${expanded ? "max-h-none" : "max-h-[22rem]"} min-h-[12rem] overflow-y-auto px-4 py-4 space-y-3`}
      >
        {messages.length === 0 && !sending && (
          <p className="text-xs text-stone-500 text-center pt-6">
            Ask a question about your score, an opportunity, or a next step.
          </p>
        )}

        {messages.map((m) => (
          <div
            key={m.id}
            className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[85%] px-3.5 py-2.5 rounded-2xl text-sm leading-relaxed ${
                m.role === "user"
                  ? "bg-amber-400 text-stone-950 whitespace-pre-wrap"
                  : "bg-stone-800/80 text-stone-100 border border-stone-700/60"
              }`}
            >
              {m.role === "assistant" ? (
                <div className="chat-markdown">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {m.content}
                  </ReactMarkdown>
                </div>
              ) : (
                m.content
              )}
            </div>
          </div>
        ))}

        {sending && (
          <div className="flex justify-start">
            <div className="px-3.5 py-2.5 rounded-2xl bg-stone-800/80 border border-stone-700/60 text-stone-400 flex items-center gap-2 text-sm">
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              Thinking…
            </div>
          </div>
        )}

        {error && (
          <p className="text-xs text-rose-400 text-center">{error}</p>
        )}
      </div>

      {/* Tag chip + input */}
      <div className="border-t border-stone-800/80 px-3 py-3 space-y-2">
        {pendingTag && (
          <div className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-amber-950/50 border border-amber-800/50 text-xs text-amber-300">
            <MessageSquare className="w-3.5 h-3.5 shrink-0" />
            <span className="truncate">Asking about: {pendingTag.label}</span>
            <button
              onClick={onConsumeTag}
              className="ml-auto p-0.5 rounded hover:bg-amber-900/40 text-amber-400"
              aria-label="Remove tag"
            >
              <X className="w-3 h-3" />
            </button>
          </div>
        )}

        {sections.length > 0 && (
          <div className="flex items-center gap-2">
            <MessageSquare className="w-3.5 h-3.5 text-stone-500 shrink-0" />
            <select
              value={picker}
              onChange={(e) => {
                const v = e.target.value;
                setPicker("");
                if (v !== "") {
                  const s = sections[Number(v)];
                  onSetTag({ kind: s.kind, id: s.id, label: s.label });
                }
              }}
              className="flex-1 min-w-0 bg-stone-900/70 border border-stone-700/60 rounded-xl px-2.5 py-2 text-xs text-stone-300 focus:border-amber-500/60 focus:ring-0"
            >
              <option value="">Ask about a specific section…</option>
              {(["opportunity", "nextStep", "weakness"] as const).map((kind) => {
                const items = sections
                  .map((s, i) => ({ ...s, i }))
                  .filter((s) => s.kind === kind);
                if (!items.length) return null;
                const label =
                  kind === "opportunity"
                    ? "Opportunities"
                    : kind === "nextStep"
                      ? "Next Steps"
                      : "Vulnerabilities";
                return (
                  <optgroup key={kind} label={label}>
                    {items.map((s) => (
                      <option key={s.i} value={String(s.i)}>
                        {s.label}
                      </option>
                    ))}
                  </optgroup>
                );
              })}
            </select>
          </div>
        )}

        <div className="flex items-end gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            rows={1}
            placeholder="Ask a question…"
            className="flex-1 resize-none max-h-32 bg-stone-900/70 border border-stone-700/60 rounded-xl px-3 py-2 text-sm text-stone-100 placeholder:text-stone-600 focus:border-amber-500/60 focus:ring-0"
          />
          <button
            onClick={handleSend}
            disabled={sending || !input.trim()}
            className="p-2.5 rounded-xl bg-amber-400 text-stone-950 hover:bg-amber-300 disabled:opacity-40 disabled:cursor-not-allowed transition shrink-0"
            aria-label="Send"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
