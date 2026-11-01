/// <reference path="./styles.d.ts" />
/// <reference path="./vite-env.d.ts" />
import { useEffect, useRef, useState } from "react";
import "./ChatWidget.css";

type Role = "user" | "assistant";
type Message = {
  id: number;
  role: Role;
  content: string;
  error?: boolean;
};
type Suggestion = { label: string; question: string };

type Props = {
  apiUrl?: string;
  business?: "course" | "web" | "merch";
  title?: string;
  greeting?: string;
  avatarUrl?: string;
  suggestions?: Suggestion[];
};

const API_URL = (import.meta.env.VITE_CHAT_API_URL as string | undefined) ?? "";
const GENERIC_ERROR = "Түр алдаа гарлаа. Дахин оролдоно уу.";

export default function ChatWidget({
  apiUrl = API_URL,
  business,
  title = "Magi Шидэт туслах",
  greeting = "Сайн уу! Намайг Magi гэдэг. Би Magic Code AI-ийн туслах. Танд юугаар туслах вэ?",
  avatarUrl = "/assets/chatbot-owl.png",
  suggestions = [
    { label: "Сургалтууд", question: "Ямар сургалтууд байдаг вэ?" },
    { label: "Вебсайтын үнэ", question: "Вебсайт хийлгэхэд хэдэн төгрөг вэ?" },
    { label: "Холбогдох", question: "Тантай хэрхэн холбогдох вэ?" },
  ],
}: Props) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const idRef = useRef(1);
  const listRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const launcherRef = useRef<HTMLButtonElement>(null);
  const wasOpen = useRef(false);
  const requestRef = useRef<AbortController | null>(null);

  useEffect(() => {
    const el = listRef.current;
    if (el) el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
  }, [messages, loading, open]);

  useEffect(() => {
    if (open) inputRef.current?.focus();
    else if (wasOpen.current) launcherRef.current?.focus(); // хаасны дараа фокусыг шувуунд буцаана
    wasOpen.current = open;
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

  function reset() {
    requestRef.current?.abort(); // хүлээгдэж буй хариу шинэ чатад орж ирэхгүй
    requestRef.current = null;
    setMessages([]);
    setInput("");
    setLoading(false);
    inputRef.current?.focus();
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
    requestRef.current = controller;
    let timedOut = false;
    const timer = window.setTimeout(() => {
      timedOut = true;
      controller.abort();
    }, 30000);

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
      push({ role: "assistant", content: String(data.answer ?? "") });
    } catch (e) {
      if (controller.signal.aborted && !timedOut) return; // reset() цуцалсан
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
      if (requestRef.current === controller) {
        requestRef.current = null;
        setLoading(false);
      }
    }
  }

  return (
    <div className={"cw-root" + (open ? " cw-open" : "")}>
      {open && (
        <section className="cw-panel" role="dialog" aria-label={title}>
          {/* <header> биш: сайтын глобал `header {position: fixed}` дүрэмд өртөхгүйн тулд */}
          <div className="cw-header">
            <img className="cw-avatar" src={avatarUrl} alt="" width="44" height="44" />
            <strong>{title}</strong>
            <button
              type="button"
              className="cw-icon-btn cw-refresh"
              onClick={reset}
              disabled={messages.length === 0 && !loading}
              aria-label="Чатыг шинээр эхлүүлэх"
              title="Чатыг шинээр эхлүүлэх"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M20 11a8 8 0 1 0-2.34 5.66" />
                <path d="M20 4v7h-7" />
              </svg>
            </button>
            <button type="button" className="cw-icon-btn cw-close" onClick={() => setOpen(false)} aria-label="Хаах">
              ×
            </button>
          </div>

          <div className="cw-messages" ref={listRef} aria-live="polite">
            <div className="cw-msg cw-assistant">
              <p>{greeting}</p>
            </div>

            {messages.map((m) => (
              <div
                key={m.id}
                className={
                  "cw-msg " +
                  (m.role === "user" ? "cw-user" : "cw-assistant") +
                  (m.error ? " cw-error" : "")
                }
              >
                <p>{m.content}</p>
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

          {messages.length === 0 && suggestions.length > 0 && (
            <div className="cw-chips">
              {suggestions.map((s) => (
                <button type="button" key={s.label} onClick={() => send(s.question)} disabled={loading}>
                  {s.label}
                </button>
              ))}
            </div>
          )}

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
              placeholder="Асуух зүйлээ бичээрэй…"
              maxLength={500}
              aria-label="Асуулт"
            />
            <button type="submit" disabled={loading || !input.trim()} aria-label="Илгээх">
              ↑
            </button>
          </form>
        </section>
      )}

      {/* Чат нээлттэй үед шувуу нуугдана, хаахдаа × эсвэл Esc */}
      {!open && (
        <button
          type="button"
          className="cw-launcher"
          ref={launcherRef}
          onClick={() => setOpen(true)}
          aria-label="Magi шидэт туслахыг нээх"
        >
          <img src={avatarUrl} alt="" width="76" height="76" />
        </button>
      )}
    </div>
  );
}
