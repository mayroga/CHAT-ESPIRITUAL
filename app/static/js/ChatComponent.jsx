export default class ChatComponent {
    constructor({ apiUrl }) {
        this.apiUrl = apiUrl;
    }

    mount(element) {
        element.innerHTML = `
            <div id="chat-container" class="bg-white p-4 rounded-lg shadow-md flex flex-col h-[500px]">
                <div id="messages" class="flex-grow overflow-y-auto mb-4 p-2 border rounded"></div>
                <div class="flex">
                    <input id="chat-input" type="text" placeholder="Escribe tu mensaje..." class="flex-grow border p-2 rounded-l">
                    <button id="chat-send" class="bg-blue-500 text-white px-4 py-2 rounded-r">Enviar</button>
                </div>
            </div>
        `;

        const messagesContainer = element.querySelector("#messages");
        const chatInput = element.querySelector("#chat-input");
        const chatSendBtn = element.querySelector("#chat-send");
        const audioPlayer = new Audio();

        const sendMessage = async () => {
            const message = chatInput.value.trim();
            if (!message) return;

            // Display user message
            messagesContainer.innerHTML += `<div class="text-right text-gray-700 p-2">${message}</div>`;
            chatInput.value = "";
            messagesContainer.scrollTop = messagesContainer.scrollHeight;

            try {
                const res = await fetch(this.apiUrl + "/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ message })
                });
                const data = await res.json();
                
                // Display AI reply
                messagesContainer.innerHTML += `<div class="text-left text-gray-500 p-2">Dios: ${data.reply}</div>`;
                messagesContainer.scrollTop = messagesContainer.scrollHeight;

                if (data.audio) {
                    audioPlayer.src = `data:audio/mp3;base64,${data.audio}`;
                    audioPlayer.play();
                }

            } catch (error) {
                messagesContainer.innerHTML += `<div class="text-left text-red-500 p-2">Error: No se pudo conectar.</div>`;
            }
        };

        chatSendBtn.onclick = sendMessage;
        chatInput.onkeydown = (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        };
    }
}
