import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
  Scatter,
} from "recharts";

function App() {
  const [stocks, setStocks] = useState([]);
  const [selectedStock, setSelectedStock] = useState("");
  const [data, setData] = useState([]);
  const [extrema, setExtrema] = useState([]);
  const [range, setRange] = useState("5Y");

  // 🔵 Load stocks
  useEffect(() => {
    fetch("http://127.0.0.1:8000/stocks")
      .then((res) => res.json())
      .then((res) => {
        setStocks(res.stocks);
        setSelectedStock(res.stocks[0]);
      });
  }, []);

  // 🔵 Fetch data
  useEffect(() => {
    if (!selectedStock) return;

    fetch(`http://127.0.0.1:8000/stock/${selectedStock}`)
      .then((res) => res.json())
      .then((resData) => {
        setData(resData.prices);
        setExtrema(resData.extrema || []);
      });
  }, [selectedStock]);

  // 🔥 RANGE FILTER (ONLY FILTER LOGIC)
  const getFilteredData = () => {
    if (!data.length) return [];

    const lastDate = new Date(data[data.length - 1].Date);

    const daysMap = {
      "1D": 1,
      "5D": 5,
      "1M": 30,
      "6M": 180,
      "1Y": 365,
      "5Y": 1825,
    };

    const cutoff = new Date(lastDate);
    cutoff.setDate(lastDate.getDate() - daysMap[range]);

    return data.filter((d) => new Date(d.Date) >= cutoff);
  };

  // ✅ STEP 1 — get filtered data
  const filteredData = getFilteredData();

  // ✅ STEP 2 — build date set (VERY IMPORTANT LOCATION)
  const filteredDatesSet = new Set(
    filteredData.map((d) =>
      new Date(d.Date).toISOString().split("T")[0]
    )
  );

  // 🔥 NORMALIZE DATE
  const normalizeDate = (d) =>
    new Date(d).toISOString().split("T")[0];

  // 🔥 EXTREMA MAP
  const extremaMap = {};

  extrema.forEach((e) => {
    const key = normalizeDate(e.date);

    if (!extremaMap[key]) {
      extremaMap[key] = { min: null, max: null };
    }

    const price = Number(e.price.toFixed(2));

    if (e.type === "min") extremaMap[key].min = price;
    if (e.type === "max") extremaMap[key].max = price;
  });

  // 🔥 FINAL CHART DATA
  const chartData = filteredData.map((d) => {
    const dateKey = normalizeDate(d.Date);
    const timestamp = new Date(dateKey).getTime();

    const price = Number(d.Close.toFixed(2));

    return {
      date: timestamp,
      price: price,

      // ✅ ONLY SHOW points inside selected range
      min: filteredDatesSet.has(dateKey)
        ? extremaMap[dateKey]?.min ?? null
        : null,

      max: filteredDatesSet.has(dateKey)
        ? extremaMap[dateKey]?.max ?? null
        : null,
    };
  });

  // 🔍 DEBUG
  console.log(
    "Min points:",
    chartData.filter((d) => d.min !== null).length
  );
  console.log(
    "Max points:",
    chartData.filter((d) => d.max !== null).length
  );

  return (
    <div style={{ padding: "20px", background: "#0b0f19", color: "white" }}>
      <h1 style={{ textAlign: "center", fontSize: "32px" }}>
        {selectedStock}
      </h1>

      {/* 🔵 CONTROLS */}
      <div style={{ display: "flex", gap: "10px", marginBottom: "20px" }}>
        <select onChange={(e) => setSelectedStock(e.target.value)}>
          {stocks.map((s) => (
            <option key={s}>{s}</option>
          ))}
        </select>

        {["1D", "5D", "1M", "6M", "1Y", "5Y"].map((r) => (
          <button
            key={r}
            onClick={() => setRange(r)}
            style={{
              padding: "6px 12px",
              background: range === r ? "#22c55e" : "#1e293b",
              color: "white",
              border: "none",
              cursor: "pointer",
            }}
          >
            {r}
          </button>
        ))}
      </div>

      {/* 🔵 CHART */}
      {filteredData.length === 0 ? (
        <p>Loading...</p>
      ) : (
        <ResponsiveContainer width="100%" height={550}>
          <LineChart data={chartData}>
            {/* 🔥 GRID */}
            <CartesianGrid stroke="#1f2937" strokeDasharray="3 3" />

            {/* 🔥 GRADIENT */}
            <defs>
              <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#22c55e" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
              </linearGradient>
            </defs>

            {/* 🔥 X AXIS (FIXED + IMPROVED) */}
            <XAxis
              dataKey="date"
              type="number"
              scale="time"                     // ⭐ critical for time series
              domain={["dataMin", "dataMax"]}
              tickFormatter={(d) => {
                const date = new Date(d);

                if (range === "1D" || range === "5D") {
                  return date.toLocaleTimeString("en-IN", {
                    hour: "2-digit",
                    minute: "2-digit",
                  });
                }

                if (range === "1M" || range === "6M") {
                  return date.toLocaleDateString("en-IN", {
                    day: "2-digit",
                    month: "short",
                  });
                }

                // ⭐ 1Y / 5Y → include year
                return date.toLocaleDateString("en-IN", {
                  month: "short",
                  year: "2-digit",
                });
              }}
              tick={{ fill: "#9ca3af", fontSize: 12 }}
              minTickGap={30}                  // avoids clutter
              stroke="#9ca3af"
            />

            {/* 🔥 Y AXIS */}
            <YAxis
              stroke="#9ca3af"
              domain={["auto", "auto"]}
              tickFormatter={(v) => `₹${Math.round(v)}`}  // optional but cleaner
            />

            {/* 🔥 TOOLTIP (PRO LEVEL) */}
            <Tooltip
              cursor={{ stroke: "#64748b", strokeWidth: 1 }}
              content={({ active, payload, label }) => {
                if (!active || !payload || !payload.length) return null;

                const d = payload[0].payload;

                return (
                  <div style={{
                    background: "#111827",
                    padding: "10px",
                    border: "1px solid #374151",
                    borderRadius: "6px"
                  }}>
                    <p>{new Date(label).toLocaleDateString()}</p>
                    <p>Price: ₹{d.price}</p>
                    {d.min && <p style={{ color: "red" }}>🔴 Swing Low</p>}
                    {d.max && <p style={{ color: "#22c55e" }}>🟢 Swing High</p>}
                  </div>
                );
              }}
            />

            {/* 🔥 AREA (GOOGLE STYLE) */}
            <Area
              type="monotone"
              dataKey="price"
              stroke="none"
              fill="url(#priceGradient)"
            />

            {/* 🔥 PRICE LINE */}
            <Line
              type="monotone"
              dataKey="price"
              stroke="#22c55e"
              dot={false}
              strokeWidth={2}
            />

            {/* 🔴 MINIMA */}
            <Scatter
              data={chartData.filter(d => d.min !== null).map(d => ({
                x: d.date,
                y: d.min
              }))}
              dataKey="y"
              fill="red"
              shape={(props) => (
                <polygon
                  points={`${props.cx},${props.cy - 6} ${props.cx - 6},${props.cy + 6} ${props.cx + 6},${props.cy + 6}`}
                  fill="red"
                />
              )}
            />

            {/* 🟢 MAXIMA */}
            <Scatter
              data={chartData.filter(d => d.max !== null).map(d => ({
                x: d.date,
                y: d.max
              }))}
              dataKey="y"
              fill="#22c55e"
              shape={(props) => (
                <polygon
                  points={`${props.cx},${props.cy + 6} ${props.cx - 6},${props.cy - 6} ${props.cx + 6},${props.cy - 6}`}
                  fill="#22c55e"
                />
              )}
            />

          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}

export default App;