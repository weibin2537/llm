
const MessageInput = ({ input, onInputChange, onSendMessage }) => {
  return (
    <div className="input-container">
      <input
        type="text"
        value={input}
        onChange={onInputChange}
        placeholder="Type your message..."
      />
      <button onClick={onSendMessage}>Send</button>
    </div>
  );
};

export default MessageInput;
