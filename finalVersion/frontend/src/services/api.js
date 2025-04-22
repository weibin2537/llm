import axios from "axios";

// Get backend URL from environment if available or use service DNS name
const getBackendUrl = () => {
  // For development environment
  if (process.env.REACT_APP_BACKEND_URL) {
    return process.env.REACT_APP_BACKEND_URL;
  }

  // Within Kubernetes, use service DNS
  return 'http://chatbox-backend:8000';
};

const fetchResponse = async (message) => {
  try {
    const backendUrl = getBackendUrl();
    console.log("Connecting to backend at:", backendUrl);

    const response = await axios.post(`${backendUrl}/chat`, { message });
    return typeof response.data.response === 'object'
      ? JSON.stringify(response.data.response)
      : response.data.response;
  } catch (error) {
    console.error("Error fetching response:", error);
    return "Sorry, I couldn't get a response. Error: " + error.message;
  }
};

export { fetchResponse };
