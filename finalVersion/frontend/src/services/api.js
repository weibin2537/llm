import axios from "axios";
const fetchResponse = async (message) => {
  try {
    const response = await axios.post('http://backend-service:8000/chat', { message });
    return typeof response.data.response === 'object' 
      ? JSON.stringify(response.data.response) 
      : response.data.response;
  } catch (error) {
    console.error("Error fetching response:", error);
    return "Sorry, I couldn't get a response.";  // 错误处理
  }
};


export { fetchResponse };
