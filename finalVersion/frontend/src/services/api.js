import axios from "axios";

/**
 * Determines the appropriate backend URL based on environment
 */
const getBackendUrl = () => {
  // Check if we're in development environment
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:8000';
  }

  // In Kubernetes, use relative URL for gateway routing
  return '';
};

/**
 * Fetches a response from the LLM via the backend service
 * @param {string} message - The user's message to send to the model
 * @returns {Promise<string>} - The model's response
 */
const fetchResponse = async (message) => {
  try {
    // Get the base URL
    const baseUrl = getBackendUrl();

    // Construct the full URL
    const url = baseUrl ? `${baseUrl}/chat` : '/chat';

    console.log(`Sending request to: ${url}`);

    // Make the request
    const response = await axios.post(url, { message });

    // Handle the response
    if (response.data && response.data.response) {
      // Check if response is an object or string
      return typeof response.data.response === 'object'
        ? JSON.stringify(response.data.response)
        : response.data.response;
    } else {
      console.error("Invalid response format:", response.data);
      return "Received an invalid response format from the server.";
    }
  } catch (error) {
    console.error("Error fetching response:", error);

    // Provide a more detailed error message for debugging
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error("Server responded with error:", error.response.status, error.response.data);
      return `Sorry, I couldn't get a response. Server error: ${error.response.status}`;
    } else if (error.request) {
      // The request was made but no response was received
      console.error("No response received:", error.request);
      return "Sorry, I couldn't get a response. The server did not respond.";
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error("Request setup error:", error.message);
      return `Sorry, I couldn't get a response. Error: ${error.message}`;
    }
  }
};

export { fetchResponse };
