import { useState } from "https://cdn.skypack.dev/react";
import { createRoot } from "https://cdn.skypack.dev/react-dom/client";

export default function ChatComponent({ apiUrl }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const sendMessage = async () => {
    if(!input.trim()) return;
    const res = await fetch(apiUrl + "/chat", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ message: input })
    });
    const data = await res.json();
    setMessages([...messages, { user: input, reply: data.reply }]);
    setInput("");
  }

  return {
    mount(el) {
      createRoot(el).render(
        <div className="p-4 border rounded shadow">
          <div className="h-64 overflow-y-auto mb-2 border p-2">
            {messages.map((m,i) => (
              <div key={i} className="mb-2">
                <div className="font-bold">Tú:</div><div>{m.user}</div>
                <div className="font-bold text-green-700">Guía:</div><div>{m.reply}</div>
              </div>
            ))}
          </div>
          <input
            type="text"
            className="border p-2 w-full"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key==="Enter" && sendMessage()}
            placeholder="Escribe tu mensaje..."
          />
        </div>
      );
    }
  }
}
