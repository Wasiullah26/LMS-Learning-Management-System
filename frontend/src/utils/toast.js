/**
 * Toast notification utility
 */

let toastId = 0;
let toastListeners = [];

export const toast = {
  success: (message) => {
    const id = ++toastId;
    toastListeners.forEach(listener => listener({ id, message, type: 'success' }));
    return id;
  },
  
  error: (message) => {
    const id = ++toastId;
    toastListeners.forEach(listener => listener({ id, message, type: 'error' }));
    return id;
  },
  
  info: (message) => {
    const id = ++toastId;
    toastListeners.forEach(listener => listener({ id, message, type: 'info' }));
    return id;
  },
  
  subscribe: (listener) => {
    toastListeners.push(listener);
    return () => {
      toastListeners = toastListeners.filter(l => l !== listener);
    };
  }
};

