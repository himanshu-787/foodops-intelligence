import { useEffect, useState } from "react";

// value badalne ke `delay` ms baad hi nayi value deta hai
export function useDebounce<T>(value: T, delay = 400): T {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);   // naya akshar aaya toh purana timer cancel
  }, [value, delay]);

  return debounced;
}