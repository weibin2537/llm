import  { useState } from "react";
import MessageInput from "./MessageInput"; // 导入 MessageInput 组件
import { fetchResponse } from "../services/api"; // 导入 API 服务文件

const ChatWindow = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const handleSendMessage = async () => {
    if (input.trim() === "") return;

    setMessages((prevMessages) => [
      ...prevMessages,
      { sender: "user", text: input },
    ]);

    const botResponse = await fetchResponse(input);      // 调用 fetchResponse 函数

    setMessages((prevMessages) => [
      ...prevMessages,
      { sender: "bot", text: botResponse },
    ]);

    setInput("");
  };

  const handleInputChange = (event) => {
    setInput(event.target.value);
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((msg, index) => (
          <div key={index} className={msg.sender}>
            {msg.text}
          </div>
        ))}
      </div>
      <MessageInput
        input={input}
        onInputChange={handleInputChange}
        onSendMessage={handleSendMessage}
      />
    </div>
  );
};

export default ChatWindow;
