import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import Card from './UI/Card';

function StokeByMonthChart({ data }) {
  if (!data || data.length === 0) {
    return null;
  }

  // Ensure avg_stoke is a number or null
  const chartData = data.map(item => ({
    ...item,
    avg_stoke: item.avg_stoke === null ? null : Number(item.avg_stoke),
  }));

  return (
    <Card className="mt-8">
      <h3 className="text-xl font-bold text-gray-800 mb-4 text-center">Stoke by Month</h3>
      <div style={{ width: '100%', height: 300 }}>
        <ResponsiveContainer>
          <LineChart
            data={chartData}
            margin={{
              top: 5,
              right: 20,
              left: -10,
              bottom: 5,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="month" tick={{ fontSize: 12 }} />
            <YAxis domain={[1, 10]} ticks={[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]} allowDecimals={false} />
            <Tooltip
              contentStyle={{
                backgroundColor: 'rgba(255, 255, 255, 0.8)',
                border: '1px solid #ccc',
                borderRadius: '5px',
              }}
              labelStyle={{ fontWeight: 'bold' }}
              formatter={(value) => (value === null ? 'No sessions' : [value.toFixed(2), 'Avg Stoke'])}
            />
            <Line type="monotone" dataKey="avg_stoke" stroke="#10B981" strokeWidth={2} activeDot={{ r: 8 }} name="Avg Stoke" connectNulls={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}

export default StokeByMonthChart;

