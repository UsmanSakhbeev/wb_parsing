import React, { useState, useEffect, useMemo } from "react";
import axios from "axios";
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  flexRender,
} from "@tanstack/react-table";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ScatterChart,
  Scatter,
  CartesianGrid,
  Line,
} from "recharts";

export default function App() {
  const [data, setData] = useState([]);
  const [sorting, setSorting] = useState([]);
  const [filters, setFilters] = useState({
    minPrice: 0,
    maxPrice: 1000000,
    minRating: 0,
    minFeedbacks: 0,
  });

  // fetch when filters/sorting change (debounced 300 ms)
  useEffect(() => {
    const id = setTimeout(fetchData, 300);
    return () => clearTimeout(id);
  }, [filters, sorting]);

  async function fetchData() {
    const params = {
      min_price: filters.minPrice * 100,
      max_price: filters.maxPrice * 100,
      min_rating: filters.minRating,
      min_feedbacks: filters.minFeedbacks,
    };
    if (sorting.length) {
      params.ordering = (sorting[0].desc ? "-" : "") + sorting[0].id.replace("_rub", "");
    }
    const res = await axios.get("/api/products/", { params });
    setData(res.data.results);
  }

  const columns = useMemo(
    () => [
      { header: "Название", accessorKey: "name" },
      { header: "Цена, ₽", accessorKey: "price_rub" },
      { header: "Цена со скидкой, ₽", accessorKey: "sale_price_rub" },
      { header: "Рейтинг", accessorKey: "rating" },
      { header: "Отзывы", accessorKey: "feedbacks" },
    ],
    []
  );

  const table = useReactTable({
    data,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
  });

  // histogram (10 bins)
  const histogramData = useMemo(() => {
    if (!data.length) return [];
    const prices = data.map((d) => d.sale_price_rub);
    const min = Math.min(...prices);
    const max = Math.max(...prices);
    const step = (max - min) / 10 || 1;
    const bins = Array.from({ length: 10 }, (_, i) => ({
      name: `${Math.round(min + i * step)}–${Math.round(min + (i + 1) * step)}`,
      count: 0,
    }));
    prices.forEach((p) => {
      const idx = Math.min(9, Math.floor((p - min) / step));
      bins[idx].count += 1;
    });
    return bins;
  }, [data]);

  // scatter (discount % vs rating)
  const scatterData = useMemo(
    () =>
      data.map((d) => ({
        rating: d.rating,
        discount: Math.round(100 - (d.sale_price_rub / d.price_rub) * 100),
      })),
    [data]
  );

  return (
    <div className="p-6 space-y-8">
      <h1 className="text-3xl font-bold">WB Products Analytics</h1>

      {/* Filters */}
      <div className="grid md:grid-cols-4 gap-4">
        <div>
          <label className="block text-sm font-medium">Min price ₽</label>
          <input
            type="number"
            className="w-full border rounded p-2"
            value={filters.minPrice}
            onChange={(e) => setFilters((f) => ({ ...f, minPrice: +e.target.value }))}
          />
        </div>
        <div>
          <label className="block text-sm font-medium">Max price ₽</label>
          <input
            type="number"
            className="w-full border rounded p-2"
            value={filters.maxPrice}
            onChange={(e) => setFilters((f) => ({ ...f, maxPrice: +e.target.value }))}
          />
        </div>
        <div>
          <label className="block text-sm font-medium">Min rating</label>
          <input
            type="number"
            step="0.1"
            min="0"
            max="5"
            className="w-full border rounded p-2"
            value={filters.minRating}
            onChange={(e) => setFilters((f) => ({ ...f, minRating: +e.target.value }))}
          />
        </div>
        <div>
          <label className="block text-sm font-medium">Min feedbacks</label>
          <input
            type="number"
            className="w-full border rounded p-2"
            value={filters.minFeedbacks}
            onChange={(e) => setFilters((f) => ({ ...f, minFeedbacks: +e.target.value }))}
          />
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full table-auto border">
          <thead className="bg-gray-100">
            {table.getHeaderGroups().map((hg) => (
              <tr key={hg.id}>
                {hg.headers.map((h) => (
                  <th
                    key={h.id}
                    colSpan={h.colSpan}
                    className="px-4 py-2 cursor-pointer select-none"
                    onClick={h.column.getToggleSortingHandler()}
                  >
                    {flexRender(h.column.columnDef.header, h.getContext())}{" "}
                    {{ asc: "▲", desc: "▼" }[h.column.getIsSorted() ?? null]}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.map((row) => (
              <tr key={row.id} className="border-t">
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id} className="px-4 py-2">
                    {flexRender(
                      cell.column.columnDef.cell ?? cell.column.columnDef.header,
                      cell.getContext()
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Histogram */}
      <div className="w-full md:w-2/3">
        <h2 className="text-xl font-semibold mb-2">Price histogram</h2>
        <BarChart width={600} height={300} data={histogramData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis allowDecimals={false} />
          <Tooltip />
          <Bar dataKey="count" />
        </BarChart>
      </div>

      {/* Scatter */}
      <div className="w-full md:w-2/3">
        <h2 className="text-xl font-semibold mb-2">Discount vs Rating</h2>
        <ScatterChart width={600} height={300}>
          <CartesianGrid />
          <XAxis type="number" dataKey="rating" name="Rating" domain={[0, 5]} />
          <YAxis type="number" dataKey="discount" name="Discount %" domain={[0, 100]} />
          <Tooltip />
          <Scatter data={scatterData} line>
            <Line type="monotone" dataKey="discount" strokeWidth={2} />
          </Scatter>
        </ScatterChart>
      </div>
    </div>
  );
}
