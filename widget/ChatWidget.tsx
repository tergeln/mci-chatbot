/// <reference path="./styles.d.ts" />
/// <reference path="./vite-env.d.ts" />
import { useEffect, useRef, useState } from "react";
import "./ChatWidget.css";

type Role = "user" | "assistant";
type Source = { title: string; heading?: string | null; page?: number | null };
type Message = {
  id: number;
  role: Role;
  content: string;
  sources?: Source[];
  found?: boolean;
  error?: boolean;
};

type Props = {
  apiUrl?: string;
  business?: "course" | "web" | "merch";
  title?: string;
  greeting?: string;
  suggestions?: string[];
  showSources?: boolean;
};

const API_URL = (import.meta.env.VITE_CHAT_API_URL as string | undefined) ?? "";
const GENERIC_ERROR = "Түр алдаа гарлаа. Дахин оролдоно уу.";

export default function ChatWidget({
  apiUrl = API_URL,
  business,
  title = "Туслах",
  greeting = "Сайн байна уу! Би вебсайт хөгжүүлэлт, мерч, онлайн сургалтын талаарх асуултад хариулна.",
  suggestions = ["Вебсайт хийлгэхэд хэдэн төгрөг вэ?", "Ямар сургалтууд байдаг вэ?"],
  showSources = true,
}: Props) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const idRef = useRef(1);
  const listRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const el = listRef.current;
    if (el) el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
  }, [messages, loading, open]);

  useEffect(() => {
    if (open) inputRef.current?.focus();
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  function push(message: Omit<Message, "id">) {
    setMessages((prev) => [...prev, { ...message, id: idRef.current++ }]);
  }

  async function send(text: string) {
    const question = text.trim();
    if (!question || loading) return;

    const history = messages
      .filter((m) => !m.error)
      .slice(-6)
      .map((m) => ({ role: m.role, content: m.content.slice(0, 1000) }));

    push({ role: "user", content: question });
    setInput("");

    if (!apiUrl) {
      console.error("VITE_CHAT_API_URL тохируулагдаагүй байна");
      push({ role: "assistant", content: GENERIC_ERROR, error: true });
      return;
    }

    setLoading(true);
    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), 30000);

    try {
      const res = await fetch(`${apiUrl.replace(/\/$/, "")}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: question, history, ...(business ? { business } : {}) }),
        signal: controller.signal,
      });
      const data = await res.json().catch(() => null);
      if (!res.ok) {
        throw new Error(typeof data?.detail === "string" ? data.detail : GENERIC_ERROR);
      }
      push({
        role: "assistant",
        content: String(data.answer ?? ""),
        sources: Array.isArray(data.sources) ? data.sources : [],
        found: Boolean(data.found),
      });
    } catch (e) {
      const message =
        e instanceof DOMException && e.name === "AbortError"
          ? "Хариу удаан байна. Дахин оролдоно уу."
          : e instanceof TypeError
            ? "Сүлжээний алдаа. Интернэт холболтоо шалгана уу."
            : e instanceof Error
              ? e.message
              : GENERIC_ERROR;
      push({ role: "assistant", content: message, error: true });
    } finally {
      window.clearTimeout(timer);
      setLoading(false);
    }
  }

  return (
    <div className="cw-root">
      {open && (
        <section className="cw-panel" role="dialog" aria-label={title}>
          <header className="cw-header">
            <div>
              <strong>{title}</strong>
              <span className="cw-sub">AI туслах</span>
            </div>
            <button type="button" className="cw-close" onClick={() => setOpen(false)} aria-label="Хаах">
              ×
            </button>
          </header>

          <div className="cw-messages" ref={listRef} aria-live="polite">
            <div className="cw-msg cw-assistant">
              <p>{greeting}</p>
            </div>

            {messages.length === 0 && suggestions.length > 0 && (
              <div className="cw-chips">
                {suggestions.map((s) => (
                  <button type="button" key={s} onClick={() => send(s)} disabled={loading}>
                    {s}
                  </button>
                ))}
              </div>
            )}

            {messages.map((m) => (
              <div
                key={m.id}
                className={
                  "cw-msg " +
                  (m.role === "user" ? "cw-user" : "cw-assistant") +
                  (m.error ? " cw-error" : "") +
                  (m.found === false ? " cw-muted" : "")
                }
              >
                <p>{m.content}</p>
                {showSources && m.sources && m.sources.length > 0 && (
                  <details className="cw-sources">
                    <summary>Эх сурвалж</summary>
                    <ul>
                      {m.sources.map((s, i) => (
                        <li key={i}>
                          {s.heading || s.title}
                          {s.page ? `, ${s.page}-р хуудас` : ""}
                        </li>
                      ))}
                    </ul>
                  </details>
                )}
              </div>
            ))}

            {loading && (
              <div className="cw-msg cw-assistant">
                <span className="cw-typing" aria-label="Хариулж байна">
                  <i />
                  <i />
                  <i />
                </span>
              </div>
            )}
          </div>

          <form
            className="cw-form"
            onSubmit={(e) => {
              e.preventDefault();
              send(input);
            }}
          >
            <input
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Асуултаа бичнэ үү..."
              maxLength={500}
              aria-label="Асуулт"
            />
            <button type="submit" disabled={loading || !input.trim()}>
              Илгээх
            </button>
          </form>
          <p className="cw-note">Хариулт буруу байж болзошгүй. Чухал мэдээллээ баталгаажуулна уу.</p>
        </section>
      )}

      <button
        type="button"
        className="cw-launcher"
        onClick={() => setOpen((o) => !o)}
        aria-label={open ? "Чатыг хаах" : "Чат нээх"}
        aria-expanded={open}
      >
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path
            d="M4 5h16a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H9l-4.2 3.4A.5.5 0 0 1 4 20.5V17a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1Z"
            fill="currentColor"
          />
        </svg>
      </button>
    </div>
  );
}
