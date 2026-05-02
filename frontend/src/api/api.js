export const fetchStock = async (symbol, range) => {
  const res = await fetch(`http://127.0.0.1:8000/stock/${symbol}?range=${range}`);
  return await res.json();
};