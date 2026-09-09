import axios from 'axios';

let rawURL = import.meta.env.VITE_API_URL || '/api';
if (rawURL.endsWith('/')) {
  rawURL = rawURL.slice(0, -1);
}
const baseURL = rawURL.endsWith('/api') ? rawURL : `${rawURL}/api`;

const api = axios.create({
  baseURL,
  headers: {
    Accept: 'application/json',
  },
});

export default api;


